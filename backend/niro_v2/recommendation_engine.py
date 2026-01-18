"""NIRO V2 Recommendation Engine

Deterministic rules-based recommendation with LLM enrichment.
Validates all outputs against catalog.
"""

import logging
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import time

from .models import (
    Package, Remedy, Topic, Branch, Urgency,
    StepAExtraction, StepBRecommendation, ChartInsight,
    ChatRecommendationResponse, ValidatedRecommendation,
    ValidationError, ValidationErrorDetail, RetryMessage,
    HandoffVersions, AuditInfo, ChatHandoffPayload,
    CatalogContext, CatalogPackageContext, CatalogRemedyContext,
    UserContext, IntakeSignals, SituationIntake
)
from .catalog import CatalogService, get_catalog_service, CATALOG_VERSION

logger = logging.getLogger(__name__)

# Current prompt version
PROMPT_VERSION = "v2.0.0"


class RecommendationEngine:
    """
    Controlled recommendation engine:
    1. Builds handoff payload with catalog context
    2. Validates chat responses against catalog
    3. Falls back to rules if validation fails
    """
    
    def __init__(self, catalog_service: Optional[CatalogService] = None):
        self.catalog = catalog_service or get_catalog_service()
        self.prompt_version = PROMPT_VERSION
        self.catalog_version = CATALOG_VERSION
    
    # =========================================================================
    # HANDOFF PAYLOAD BUILDING
    # =========================================================================
    
    def build_handoff_payload(
        self,
        session_id: str,
        user_id: str,
        user_context: UserContext,
        intake: SituationIntake
    ) -> ChatHandoffPayload:
        """
        Build the handoff payload to send to chat engine.
        Includes catalog context with only IDs the chat can recommend.
        """
        
        # Get packages for the intake topic
        topic_packages = self.catalog.get_packages_for_topic(intake.topic.value)
        
        # Build catalog context
        package_context = [
            CatalogPackageContext(
                package_id=p.package_id,
                topic=p.topic.value,
                branch=p.branch.value,
                price_inr=p.price_inr,
                has_consultation=p.includes_consultation,
                duration_weeks=p.duration_weeks,
                priority_score=p.targeting.priority_score
            )
            for p in topic_packages
        ]
        
        # Get remedies compatible with topic
        topic_remedies = self.catalog.get_all_remedies(topic=intake.topic.value)
        
        remedy_context = [
            CatalogRemedyContext(
                remedy_id=r.remedy_id,
                category=r.category.value,
                price_inr=r.price_inr,
                compatible_topics=r.compatible_topics
            )
            for r in topic_remedies
        ]
        
        return ChatHandoffPayload(
            session_id=session_id,
            user_id=user_id,
            mode="PACKAGE_RECOMMENDATION",
            versions=HandoffVersions(
                prompt_version=self.prompt_version,
                catalog_version=self.catalog_version
            ),
            user_context=user_context,
            intake_signals=IntakeSignals(
                topic=intake.topic.value,
                urgency=intake.urgency.value,
                desired_outcome=intake.desired_outcome,
                decision_ownership=intake.decision_ownership.value
            ),
            catalog_context=CatalogContext(
                available_packages=package_context,
                available_remedies=remedy_context
            )
        )
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def validate_recommendation(
        self,
        response: ChatRecommendationResponse,
        allowed_package_ids: List[str],
        allowed_remedy_ids: List[str]
    ) -> Tuple[bool, Optional[ValidationError]]:
        """
        Validate chat recommendation response.
        Returns (is_valid, validation_error if invalid)
        """
        errors = []
        
        # Validate primary package ID
        primary_id = response.step_b_recommendation.primary_package_id
        if primary_id not in allowed_package_ids:
            errors.append(ValidationErrorDetail(
                error_code="UNKNOWN_PACKAGE_ID",
                field="step_b_recommendation.primary_package_id",
                received_value=primary_id,
                message=f"Package ID '{primary_id}' not found in catalog"
            ))
        
        # Validate alternative package IDs
        for i, alt_id in enumerate(response.step_b_recommendation.alternative_package_ids):
            if alt_id not in allowed_package_ids:
                errors.append(ValidationErrorDetail(
                    error_code="UNKNOWN_PACKAGE_ID",
                    field=f"step_b_recommendation.alternative_package_ids[{i}]",
                    received_value=alt_id,
                    message=f"Package ID '{alt_id}' not found in catalog"
                ))
        
        # Validate suggested remedy IDs
        for i, remedy_id in enumerate(response.step_b_recommendation.suggested_remedy_ids):
            if remedy_id not in allowed_remedy_ids:
                errors.append(ValidationErrorDetail(
                    error_code="UNKNOWN_REMEDY_ID",
                    field=f"step_b_recommendation.suggested_remedy_ids[{i}]",
                    received_value=remedy_id,
                    message=f"Remedy ID '{remedy_id}' not found in catalog"
                ))
        
        # Validate branch is valid
        valid_branches = ["remedies_only", "consult_only", "combined"]
        if response.step_b_recommendation.branch not in valid_branches:
            errors.append(ValidationErrorDetail(
                error_code="INVALID_BRANCH",
                field="step_b_recommendation.branch",
                received_value=response.step_b_recommendation.branch,
                message=f"Branch must be one of {valid_branches}"
            ))
        
        if errors:
            return False, ValidationError(
                session_id=response.session_id,
                response_id=response.response_id,
                errors=errors,
                retry_message=RetryMessage(
                    instruction="RETRY: Your recommendation contains invalid IDs. Choose ONLY from the following allowed options.",
                    allowed_package_ids=allowed_package_ids,
                    allowed_remedy_ids=allowed_remedy_ids,
                    retry_count=1
                ),
                versions=response.versions
            )
        
        return True, None
    
    # =========================================================================
    # RULES-BASED RECOMMENDATION (FALLBACK)
    # =========================================================================
    
    def determine_branch(self, extraction: StepAExtraction, intake: SituationIntake) -> str:
        """
        Determine recommended branch using deterministic rules.
        """
        urgency = intake.urgency.value
        wants_consult = extraction.wants_consultation
        concern_count = len(extraction.key_concerns)
        decision_owner = intake.decision_ownership.value
        
        # Rule 1: Explicit consultation request
        if wants_consult and urgency == "high":
            return "combined"
        
        # Rule 2: High urgency + complex situation
        if urgency == "high" and concern_count >= 3:
            return "combined"
        
        # Rule 3: High urgency
        if urgency == "high":
            return "combined" if wants_consult else "consult_only"
        
        # Rule 4: Medium urgency + self-motivated
        if urgency == "medium" and not wants_consult:
            return "remedies_only"
        
        # Rule 5: Medium urgency + wants support
        if urgency == "medium" and wants_consult:
            return "combined"
        
        # Rule 6: Low urgency
        if urgency == "low":
            return "remedies_only"
        
        # Rule 7: Family involvement
        if decision_owner in ["family", "both"]:
            return "combined"
        
        # Default
        return "combined"
    
    def rank_packages(
        self,
        topic: str,
        branch: str,
        extraction: StepAExtraction
    ) -> List[Tuple[Package, int]]:
        """
        Rank packages by score using deterministic rules.
        Returns list of (package, score) tuples sorted by score descending.
        """
        packages = self.catalog.get_packages_for_topic(topic)
        scored = []
        
        for pkg in packages:
            if not pkg.is_active:
                continue
            
            # Filter by branch compatibility
            if pkg.branch.value != branch and pkg.branch.value != "combined":
                continue
            
            # Filter by urgency fit
            if extraction.urgency_level not in pkg.targeting.urgency_fit:
                continue
            
            # Calculate score
            score = pkg.targeting.priority_score  # Base: 0-100
            
            # Urgency match: +20
            if extraction.urgency_level in pkg.targeting.urgency_fit:
                score += 20
            
            # Concern match: +5 per concern (max +25)
            matched_concerns = set(extraction.key_concerns) & set(pkg.targeting.compatible_concerns)
            score += min(len(matched_concerns) * 5, 25)
            
            # Consultation preference: +15
            if extraction.wants_consultation and pkg.includes_consultation:
                score += 15
            
            # Duration fit: +10
            duration_fits = {
                "high": range(4, 9),
                "medium": range(6, 11),
                "low": range(4, 13)
            }
            if pkg.duration_weeks in duration_fits.get(extraction.urgency_level, range(4, 13)):
                score += 10
            
            # Branch exact match: +10
            if pkg.branch.value == branch:
                score += 10
            
            scored.append((pkg, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return scored
    
    def suggest_remedies(
        self,
        topic: str,
        extraction: StepAExtraction,
        max_count: int = 3
    ) -> List[str]:
        """
        Suggest remedy IDs based on topic and concerns.
        """
        remedies = self.catalog.get_all_remedies(topic=topic)
        scored = []
        category_seen = set()
        
        for remedy in remedies:
            if not remedy.is_active:
                continue
            
            score = 30  # Base topic match
            
            # Concern match: +10 per concern (max +30)
            matched = set(extraction.key_concerns) & set(remedy.compatible_concerns)
            score += min(len(matched) * 10, 30)
            
            # Category diversity bonus: +15 for first of each category
            if remedy.category.value not in category_seen:
                score += 15
                category_seen.add(remedy.category.value)
            
            scored.append((remedy.remedy_id, score, remedy.category.value))
        
        # Sort by score and select top N
        scored.sort(key=lambda x: x[1], reverse=True)
        
        selected = []
        categories_selected = []
        
        for remedy_id, score, category in scored:
            if len(selected) >= max_count:
                break
            # Ensure diversity: max 2 from same category
            if categories_selected.count(category) < 2:
                selected.append(remedy_id)
                categories_selected.append(category)
        
        return selected
    
    def generate_rules_based_recommendation(
        self,
        session_id: str,
        user_id: str,
        extraction: StepAExtraction,
        intake: SituationIntake
    ) -> ValidatedRecommendation:
        """
        Generate recommendation purely from rules (no LLM).
        Used as fallback when chat validation fails.
        """
        start_time = time.time()
        
        topic = intake.topic.value
        
        # Determine branch
        branch = self.determine_branch(extraction, intake)
        
        # Rank packages
        ranked_packages = self.rank_packages(topic, branch, extraction)
        
        if not ranked_packages:
            # Fallback to first available package for topic
            all_topic_packages = self.catalog.get_packages_for_topic(topic)
            if all_topic_packages:
                primary_package = all_topic_packages[0]
                alt_packages = all_topic_packages[1:2] if len(all_topic_packages) > 1 else []
            else:
                raise ValueError(f"No packages available for topic: {topic}")
        else:
            primary_package = ranked_packages[0][0]
            alt_packages = [p for p, _ in ranked_packages[1:3]]
        
        # Suggest remedies
        suggested_remedies = self.suggest_remedies(topic, extraction)
        
        # Build recommendation
        recommendation = StepBRecommendation(
            branch=branch,
            primary_package_id=primary_package.package_id,
            alternative_package_ids=[p.package_id for p in alt_packages],
            suggested_remedy_ids=suggested_remedies,
            reasoning=f"Based on your {topic} situation with {extraction.urgency_level} urgency, we recommend the {primary_package.name} for comprehensive guidance."
        )
        
        # Generate chart insights (stub - would come from astro engine)
        chart_insights = [
            ChartInsight(
                insight="Your current planetary period supports focused action",
                relevance="This is a favorable time for making decisions in this area"
            )
        ]
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return ValidatedRecommendation(
            session_id=session_id,
            user_id=user_id,
            situation=extraction,
            chart_insights=chart_insights,
            recommendation=recommendation,
            audit=AuditInfo(
                prompt_version=self.prompt_version,
                catalog_version=self.catalog_version,
                validation_duration_ms=duration_ms,
                retry_count=0
            )
        )
    
    # =========================================================================
    # FULL RECOMMENDATION FLOW
    # =========================================================================
    
    def process_chat_response(
        self,
        response: ChatRecommendationResponse,
        handoff: ChatHandoffPayload,
        user_id: str,
        max_retries: int = 2
    ) -> ValidatedRecommendation:
        """
        Process and validate chat response.
        Returns validated recommendation or falls back to rules.
        """
        start_time = time.time()
        
        # Get allowed IDs from handoff
        allowed_package_ids = [p.package_id for p in handoff.catalog_context.available_packages]
        allowed_remedy_ids = [r.remedy_id for r in handoff.catalog_context.available_remedies]
        
        # Validate
        is_valid, validation_error = self.validate_recommendation(
            response, allowed_package_ids, allowed_remedy_ids
        )
        
        if is_valid:
            duration_ms = int((time.time() - start_time) * 1000)
            
            return ValidatedRecommendation(
                session_id=response.session_id,
                user_id=user_id,
                situation=response.step_a_extraction,
                chart_insights=response.chart_insights,
                recommendation=response.step_b_recommendation,
                audit=AuditInfo(
                    prompt_version=response.versions.prompt_version,
                    catalog_version=response.versions.catalog_version,
                    validation_duration_ms=duration_ms,
                    retry_count=0
                )
            )
        
        # Validation failed - log error and fall back to rules
        logger.warning(
            f"Chat recommendation validation failed for session {response.session_id}: "
            f"{[e.message for e in validation_error.errors]}"
        )
        
        # Create intake from handoff signals
        intake = SituationIntake(
            user_id=user_id,
            topic=Topic(handoff.intake_signals.topic),
            urgency=Urgency(handoff.intake_signals.urgency),
            desired_outcome=handoff.intake_signals.desired_outcome,
            decision_ownership=handoff.intake_signals.decision_ownership
        )
        
        # Fall back to rules-based recommendation
        return self.generate_rules_based_recommendation(
            session_id=response.session_id,
            user_id=user_id,
            extraction=response.step_a_extraction,
            intake=intake
        )


# Singleton instance
_recommendation_engine: Optional[RecommendationEngine] = None


def get_recommendation_engine() -> RecommendationEngine:
    """Get or create recommendation engine singleton"""
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine
