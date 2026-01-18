"""NIRO V2 Catalog Service

Source of truth for packages and remedies.
All recommendations must reference IDs from this catalog.
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime

from .models import (
    Package, Remedy, ConsultPolicy, Topic, Branch, RemedyCategory,
    SelfGuidedItem, AdditionalService, ItemSchedule,
    PackageTargeting, LiveSessionPolicy, ChatPolicy
)

logger = logging.getLogger(__name__)

# Current catalog version - increment when catalog changes
CATALOG_VERSION = "2025.01.15.001"


class CatalogService:
    """Manages package and remedy catalogs"""
    
    def __init__(self):
        self.packages: Dict[str, Package] = {}
        self.remedies: Dict[str, Remedy] = {}
        self.consult_policies: Dict[str, ConsultPolicy] = {}
        self.catalog_version = CATALOG_VERSION
        
        # Initialize with seed data
        self._seed_consult_policies()
        self._seed_packages()
        self._seed_remedies()
        
        logger.info(f"CatalogService initialized with {len(self.packages)} packages, {len(self.remedies)} remedies")
    
    # =========================================================================
    # CONSULT POLICIES
    # =========================================================================
    
    def _seed_consult_policies(self):
        """Seed consultation policies"""
        
        self.consult_policies = {
            "consult-policy-standard-8wk": ConsultPolicy(
                policy_id="consult-policy-standard-8wk",
                name="Standard 8-Week Consultation",
                validity_weeks=8,
                live_sessions=LiveSessionPolicy(
                    max_minutes_per_session=60,
                    sessions_per_week_limit=1,
                    total_sessions_included=8
                ),
                chat=ChatPolicy(is_unlimited=True, sla_hours=12),
                fair_use_summary="Unlimited chat (replies within 12hrs) + 1 video session/week (60 min max)",
                catalog_version=CATALOG_VERSION
            ),
            "consult-policy-standard-6wk": ConsultPolicy(
                policy_id="consult-policy-standard-6wk",
                name="Standard 6-Week Consultation",
                validity_weeks=6,
                live_sessions=LiveSessionPolicy(
                    max_minutes_per_session=45,
                    sessions_per_week_limit=1,
                    total_sessions_included=3
                ),
                chat=ChatPolicy(is_unlimited=True, sla_hours=24),
                fair_use_summary="Unlimited chat (replies within 24hrs) + bi-weekly 45-min sessions",
                catalog_version=CATALOG_VERSION
            ),
            "consult-policy-standard-10wk": ConsultPolicy(
                policy_id="consult-policy-standard-10wk",
                name="Standard 10-Week Consultation",
                validity_weeks=10,
                live_sessions=LiveSessionPolicy(
                    max_minutes_per_session=60,
                    sessions_per_week_limit=1,
                    total_sessions_included=10
                ),
                chat=ChatPolicy(is_unlimited=True, sla_hours=12),
                fair_use_summary="Unlimited chat (replies within 12hrs) + 1 video session/week (60 min max)",
                catalog_version=CATALOG_VERSION
            ),
            "consult-policy-standard-12wk": ConsultPolicy(
                policy_id="consult-policy-standard-12wk",
                name="Standard 12-Week Consultation",
                validity_weeks=12,
                live_sessions=LiveSessionPolicy(
                    max_minutes_per_session=45,
                    sessions_per_week_limit=1,
                    total_sessions_included=6
                ),
                chat=ChatPolicy(is_unlimited=True, sla_hours=24),
                fair_use_summary="Unlimited chat (replies within 24hrs) + bi-weekly 45-min sessions",
                catalog_version=CATALOG_VERSION
            ),
        }
    
    # =========================================================================
    # PACKAGES
    # =========================================================================
    
    def _seed_packages(self):
        """Seed package catalog with 6 packages"""
        
        # Package 1: Career Clarity Pro
        self.packages["career-clarity-pro"] = Package(
            package_id="career-clarity-pro",
            slug="career-clarity-pro",
            name="Career Clarity Pro",
            tagline="Complete career guidance with expert support",
            description="Structured approach to career decisions with personalized timing analysis and expert consultation.",
            hero_image_url="/images/packages/career-clarity-pro.jpg",
            topic=Topic.CAREER,
            branch=Branch.COMBINED,
            duration_weeks=8,
            daily_commitment_minutes=15,
            price_inr=7999,
            includes_consultation=True,
            consult_policy_id="consult-policy-standard-8wk",
            self_guided_items=[
                SelfGuidedItem(
                    item_id="sg-career-decision-framework",
                    name="Decision Framework Tool",
                    type="decision_framework",
                    description="Structured tool to evaluate your career options objectively",
                    content_type="interactive_tool",
                    duration_minutes=20,
                    schedule=ItemSchedule(day_start=1, day_end=7, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-career-timing-analysis",
                    name="Career Timing Analysis",
                    type="timing_analysis",
                    description="Personalized windows for career moves based on your chart",
                    content_type="guided_content",
                    duration_minutes=15,
                    schedule=ItemSchedule(day_start=3, day_end=3, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-career-weekly-action",
                    name="Weekly Action Plans",
                    type="action_plan",
                    description="What to focus on each week of your career transition",
                    content_type="checklist",
                    duration_minutes=10,
                    schedule=ItemSchedule(day_start=1, day_end=56, is_repeating=True, repeat_frequency="weekly")
                ),
                SelfGuidedItem(
                    item_id="sg-career-reflection",
                    name="Career Reflection Prompts",
                    type="career_reflection",
                    description="Guided questions to clarify your career goals",
                    content_type="guided_content",
                    duration_minutes=15,
                    schedule=ItemSchedule(day_start=1, day_end=56, is_repeating=True, repeat_frequency="twice_weekly")
                )
            ],
            additional_services=[
                AdditionalService(
                    service_id="as-career-report",
                    name="Career Potential Report",
                    type="career_report",
                    description="Detailed PDF analysis of your career strengths and timing",
                    delivery_type="pdf_report",
                    delivery_timeline="Within 48 hours"
                ),
                AdditionalService(
                    service_id="as-career-forecast-3month",
                    name="3-Month Career Forecast",
                    type="forecast_3month",
                    description="What's coming up in your professional sphere",
                    delivery_type="pdf_report",
                    delivery_timeline="Within 48 hours"
                ),
                AdditionalService(
                    service_id="as-career-emergency-consult",
                    name="Emergency Career Consult",
                    type="emergency_consult",
                    description="Quick 15-min call for urgent decisions",
                    delivery_type="live_session",
                    delivery_timeline="Within 24 hours"
                )
            ],
            suggested_remedy_ids=["remedy-gemstone-guidance", "remedy-career-puja", "remedy-mantra-diksha"],
            targeting=PackageTargeting(
                urgency_fit=["medium", "high"],
                priority_score=100,
                compatible_concerns=["job_change", "career_growth", "timing", "promotion", "business_start"]
            ),
            catalog_version=CATALOG_VERSION
        )
        
        # Package 2: Career Momentum
        self.packages["career-momentum"] = Package(
            package_id="career-momentum",
            slug="career-momentum",
            name="Career Momentum",
            tagline="Self-guided career tools with expert check-ins",
            description="Build career momentum with structured tools and periodic expert guidance.",
            topic=Topic.CAREER,
            branch=Branch.COMBINED,
            duration_weeks=6,
            daily_commitment_minutes=10,
            price_inr=4999,
            includes_consultation=True,
            consult_policy_id="consult-policy-standard-6wk",
            self_guided_items=[
                SelfGuidedItem(
                    item_id="sg-career-options-map",
                    name="Career Options Map",
                    type="options_map",
                    description="Visual tool to map and compare your career options",
                    content_type="interactive_tool",
                    duration_minutes=20,
                    schedule=ItemSchedule(day_start=1, day_end=7, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-career-weekly-focus",
                    name="Weekly Focus Guide",
                    type="action_plan",
                    description="Simple weekly priorities for career progress",
                    content_type="checklist",
                    duration_minutes=5,
                    schedule=ItemSchedule(day_start=1, day_end=42, is_repeating=True, repeat_frequency="weekly")
                )
            ],
            additional_services=[
                AdditionalService(
                    service_id="as-career-snapshot",
                    name="Career Snapshot Report",
                    type="career_report",
                    description="Concise career insights from your chart",
                    delivery_type="pdf_report",
                    delivery_timeline="Within 72 hours"
                )
            ],
            suggested_remedy_ids=["remedy-muhurta-selection", "remedy-mantra-diksha"],
            targeting=PackageTargeting(
                urgency_fit=["low", "medium"],
                priority_score=80,
                compatible_concerns=["career_growth", "job_search", "skill_development"]
            ),
            catalog_version=CATALOG_VERSION
        )
        
        # Package 3: Relationship Harmony Pro
        self.packages["relationship-harmony-pro"] = Package(
            package_id="relationship-harmony-pro",
            slug="relationship-harmony-pro",
            name="Relationship Harmony Pro",
            tagline="Deep relationship guidance with ongoing expert support",
            description="Navigate relationship challenges with expert guidance and structured practices.",
            topic=Topic.RELATIONSHIPS,
            branch=Branch.COMBINED,
            duration_weeks=10,
            daily_commitment_minutes=15,
            price_inr=8999,
            includes_consultation=True,
            consult_policy_id="consult-policy-standard-10wk",
            self_guided_items=[
                SelfGuidedItem(
                    item_id="sg-rel-communication",
                    name="Communication Toolkit",
                    type="communication_toolkit",
                    description="Frameworks for healthy relationship communication",
                    content_type="guided_content",
                    duration_minutes=15,
                    schedule=ItemSchedule(day_start=1, day_end=14, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-rel-conflict",
                    name="Conflict Resolution Guide",
                    type="conflict_resolution",
                    description="Step-by-step approach to resolving relationship conflicts",
                    content_type="interactive_tool",
                    duration_minutes=20,
                    schedule=ItemSchedule(day_start=8, day_end=21, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-rel-compatibility",
                    name="Compatibility Deep Dive",
                    type="compatibility_insights",
                    description="Understanding your relationship dynamics through charts",
                    content_type="guided_content",
                    duration_minutes=20,
                    schedule=ItemSchedule(day_start=3, day_end=3, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-rel-reflection",
                    name="Relationship Reflection Journal",
                    type="relationship_reflection",
                    description="Guided prompts for relationship clarity",
                    content_type="guided_content",
                    duration_minutes=10,
                    schedule=ItemSchedule(day_start=1, day_end=70, is_repeating=True, repeat_frequency="twice_weekly")
                )
            ],
            additional_services=[
                AdditionalService(
                    service_id="as-rel-compatibility-report",
                    name="Compatibility Report",
                    type="compatibility_report",
                    description="Detailed analysis of relationship dynamics",
                    delivery_type="pdf_report",
                    delivery_timeline="Within 48 hours"
                ),
                AdditionalService(
                    service_id="as-rel-forecast",
                    name="Relationship Forecast",
                    type="relationship_forecast",
                    description="Timing for relationship milestones",
                    delivery_type="pdf_report",
                    delivery_timeline="Within 48 hours"
                )
            ],
            suggested_remedy_ids=["remedy-relationship-puja", "remedy-crystal-kit", "remedy-mantra-diksha"],
            targeting=PackageTargeting(
                urgency_fit=["medium", "high"],
                priority_score=100,
                compatible_concerns=["marriage", "compatibility", "conflict", "communication", "divorce"]
            ),
            catalog_version=CATALOG_VERSION
        )
        
        # Package 4: Financial Clarity Pro
        self.packages["financial-clarity-pro"] = Package(
            package_id="financial-clarity-pro",
            slug="financial-clarity-pro",
            name="Financial Clarity Pro",
            tagline="Strategic money guidance with expert consultation",
            description="Navigate financial decisions with timing analysis and expert guidance.",
            topic=Topic.MONEY,
            branch=Branch.COMBINED,
            duration_weeks=8,
            daily_commitment_minutes=15,
            price_inr=9999,
            includes_consultation=True,
            consult_policy_id="consult-policy-standard-8wk",
            self_guided_items=[
                SelfGuidedItem(
                    item_id="sg-money-planning",
                    name="Financial Planning Framework",
                    type="financial_planning",
                    description="Structured approach to financial decision-making",
                    content_type="interactive_tool",
                    duration_minutes=25,
                    schedule=ItemSchedule(day_start=1, day_end=14, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-money-timing",
                    name="Investment Timing Guide",
                    type="investment_timing",
                    description="Favorable periods for financial moves based on your chart",
                    content_type="guided_content",
                    duration_minutes=15,
                    schedule=ItemSchedule(day_start=5, day_end=5, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-money-abundance",
                    name="Abundance Mindset Practice",
                    type="abundance_mindset",
                    description="Daily practices to shift money blocks",
                    content_type="audio",
                    duration_minutes=10,
                    schedule=ItemSchedule(day_start=1, day_end=56, is_repeating=True, repeat_frequency="daily")
                ),
                SelfGuidedItem(
                    item_id="sg-money-blocks",
                    name="Money Blocks Identifier",
                    type="money_blocks",
                    description="Uncover and address psychological money blocks",
                    content_type="interactive_tool",
                    duration_minutes=20,
                    schedule=ItemSchedule(day_start=7, day_end=14, is_repeating=False)
                )
            ],
            additional_services=[
                AdditionalService(
                    service_id="as-money-wealth-report",
                    name="Wealth Potential Report",
                    type="wealth_report",
                    description="Comprehensive analysis of your financial potential",
                    delivery_type="pdf_report",
                    delivery_timeline="Within 48 hours"
                ),
                AdditionalService(
                    service_id="as-money-business-timing",
                    name="Business Launch Timing",
                    type="business_launch_timing",
                    description="Optimal timing for business/investment moves",
                    delivery_type="pdf_report",
                    delivery_timeline="Within 48 hours"
                )
            ],
            suggested_remedy_ids=["remedy-lakshmi-puja", "remedy-gemstone-guidance", "remedy-yantra-energization"],
            targeting=PackageTargeting(
                urgency_fit=["medium", "high"],
                priority_score=100,
                compatible_concerns=["investment", "debt", "wealth", "business", "property"]
            ),
            catalog_version=CATALOG_VERSION
        )
        
        # Package 5: Health & Vitality Pro
        self.packages["health-vitality-pro"] = Package(
            package_id="health-vitality-pro",
            slug="health-vitality-pro",
            name="Health & Vitality Pro",
            tagline="Holistic health guidance with expert support",
            description="Address health concerns with personalized guidance and wellness practices.",
            topic=Topic.HEALTH,
            branch=Branch.COMBINED,
            duration_weeks=12,
            daily_commitment_minutes=20,
            price_inr=7999,
            includes_consultation=True,
            consult_policy_id="consult-policy-standard-12wk",
            self_guided_items=[
                SelfGuidedItem(
                    item_id="sg-health-wellness",
                    name="Personalized Wellness Routine",
                    type="wellness_routine",
                    description="Daily routine optimized for your constitution",
                    content_type="checklist",
                    duration_minutes=15,
                    schedule=ItemSchedule(day_start=1, day_end=84, is_repeating=True, repeat_frequency="daily")
                ),
                SelfGuidedItem(
                    item_id="sg-health-energy",
                    name="Energy Balancing Practice",
                    type="energy_practice",
                    description="Breathwork and movement for your energy type",
                    content_type="audio",
                    duration_minutes=15,
                    schedule=ItemSchedule(day_start=1, day_end=84, is_repeating=True, repeat_frequency="daily")
                ),
                SelfGuidedItem(
                    item_id="sg-health-protocol",
                    name="Healing Protocol",
                    type="healing_protocol",
                    description="Structured approach to address health concerns",
                    content_type="guided_content",
                    duration_minutes=20,
                    schedule=ItemSchedule(day_start=1, day_end=28, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-health-lifestyle",
                    name="Lifestyle Optimization Plan",
                    type="lifestyle_plan",
                    description="Sleep, diet, and routine recommendations",
                    content_type="checklist",
                    duration_minutes=10,
                    schedule=ItemSchedule(day_start=7, day_end=7, is_repeating=False)
                )
            ],
            additional_services=[
                AdditionalService(
                    service_id="as-health-forecast",
                    name="Health Forecast Report",
                    type="health_forecast",
                    description="Health timing and vulnerability periods",
                    delivery_type="pdf_report",
                    delivery_timeline="Within 48 hours"
                ),
                AdditionalService(
                    service_id="as-health-wellness-report",
                    name="Wellness Compatibility Analysis",
                    type="wellness_report",
                    description="What works best for your constitution",
                    delivery_type="pdf_report",
                    delivery_timeline="Within 48 hours"
                )
            ],
            suggested_remedy_ids=["remedy-crystal-kit", "remedy-chakra-balancing", "remedy-navagraha-shanti"],
            targeting=PackageTargeting(
                urgency_fit=["low", "medium", "high"],
                priority_score=90,
                compatible_concerns=["chronic_illness", "energy", "sleep", "stress", "wellness"]
            ),
            catalog_version=CATALOG_VERSION
        )
        
        # Package 6: Child & Education Guidance
        self.packages["child-education-guidance"] = Package(
            package_id="child-education-guidance",
            slug="child-education-guidance",
            name="Child & Education Guidance",
            tagline="Comprehensive guidance for your child's path",
            description="Navigate your child's education and development with expert guidance.",
            topic=Topic.CHILDREN,
            branch=Branch.COMBINED,
            duration_weeks=6,
            daily_commitment_minutes=15,
            price_inr=6999,
            includes_consultation=True,
            consult_policy_id="consult-policy-standard-6wk",
            self_guided_items=[
                SelfGuidedItem(
                    item_id="sg-child-potential",
                    name="Child Potential Assessment",
                    type="child_development",
                    description="Understanding your child's natural strengths and timing",
                    content_type="guided_content",
                    duration_minutes=20,
                    schedule=ItemSchedule(day_start=1, day_end=7, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-child-education-timing",
                    name="Education Timing Guide",
                    type="education_timing",
                    description="Optimal timing for educational decisions",
                    content_type="guided_content",
                    duration_minutes=15,
                    schedule=ItemSchedule(day_start=5, day_end=5, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-child-parenting",
                    name="Parenting Style Insights",
                    type="parenting_guide",
                    description="Tailored parenting approaches for your child",
                    content_type="guided_content",
                    duration_minutes=15,
                    schedule=ItemSchedule(day_start=7, day_end=21, is_repeating=False)
                ),
                SelfGuidedItem(
                    item_id="sg-child-progress",
                    name="Weekly Progress Check-in",
                    type="action_plan",
                    description="Track and optimize your child's development",
                    content_type="checklist",
                    duration_minutes=10,
                    schedule=ItemSchedule(day_start=1, day_end=42, is_repeating=True, repeat_frequency="weekly")
                )
            ],
            additional_services=[
                AdditionalService(
                    service_id="as-child-chart",
                    name="Child Chart Analysis",
                    type="child_chart_analysis",
                    description="Comprehensive analysis of your child's birth chart",
                    delivery_type="pdf_report",
                    delivery_timeline="Within 48 hours"
                ),
                AdditionalService(
                    service_id="as-child-name",
                    name="Name Consultation",
                    type="name_consultation",
                    description="Guidance on auspicious naming (for newborns)",
                    delivery_type="live_session",
                    delivery_timeline="Scheduled session"
                )
            ],
            suggested_remedy_ids=["remedy-child-blessing-puja", "remedy-education-yantra", "remedy-mantra-diksha"],
            targeting=PackageTargeting(
                urgency_fit=["low", "medium", "high"],
                priority_score=90,
                compatible_concerns=["education", "child_development", "school_choice", "career_guidance", "naming"]
            ),
            catalog_version=CATALOG_VERSION
        )
    
    # =========================================================================
    # REMEDIES
    # =========================================================================
    
    def _seed_remedies(self):
        """Seed remedy catalog with 12+ remedies"""
        
        # Astrological Remedies
        self.remedies["remedy-gemstone-guidance"] = Remedy(
            remedy_id="remedy-gemstone-guidance",
            slug="gemstone-guidance",
            name="Gemstone Guidance + Sourcing",
            description="Personalized gemstone recommendation based on your birth chart and current goals.",
            category=RemedyCategory.ASTROLOGICAL,
            sub_type="gemstone",
            price_inr=2999,
            what_included=[
                "Chart analysis for gemstone suitability",
                "Primary + alternative gemstone options",
                "Wearing instructions (finger, metal, timing)",
                "Sourcing assistance from verified suppliers",
                "Energization guidance"
            ],
            how_it_works=[
                "Purchase this add-on",
                "Expert analyzes your chart",
                "Receive recommendation within 48 hours",
                "Choose to source through us or independently"
            ],
            delivery_timeline="48 hours",
            compatible_topics=["career", "money", "health", "relationships"],
            compatible_concerns=["growth", "protection", "success", "stability"],
            catalog_version=CATALOG_VERSION
        )
        
        self.remedies["remedy-yantra-energization"] = Remedy(
            remedy_id="remedy-yantra-energization",
            slug="yantra-energization",
            name="Yantra Energization + Delivery",
            description="Sacred geometric tool energized specifically for your goal and chart.",
            category=RemedyCategory.ASTROLOGICAL,
            sub_type="yantra",
            price_inr=1999,
            what_included=[
                "Yantra selection based on your goal",
                "Professional energization ritual",
                "Installation guidance",
                "Physical yantra delivered to your address"
            ],
            how_it_works=[
                "Purchase this add-on",
                "We select appropriate yantra for your situation",
                "Yantra energized at auspicious time",
                "Delivered within 7-10 days"
            ],
            delivery_timeline="7-10 days",
            fulfillment_type="physical",
            compatible_topics=["career", "money", "health", "family"],
            compatible_concerns=["protection", "prosperity", "success", "peace"],
            catalog_version=CATALOG_VERSION
        )
        
        self.remedies["remedy-mantra-diksha"] = Remedy(
            remedy_id="remedy-mantra-diksha",
            slug="mantra-diksha",
            name="Personalized Mantra Diksha",
            description="Mantra initiation personalized for your chart and goal.",
            category=RemedyCategory.ASTROLOGICAL,
            sub_type="mantra_diksha",
            price_inr=2499,
            what_included=[
                "Personalized mantra selection",
                "Initiation session with expert",
                "Practice guidelines and schedule",
                "Audio recording for daily practice",
                "Follow-up guidance"
            ],
            how_it_works=[
                "Purchase this add-on",
                "Schedule initiation session",
                "Receive mantra and practice guidance",
                "Begin daily practice with support"
            ],
            delivery_timeline="Scheduled session",
            requires_consultation=True,
            compatible_topics=["career", "money", "health", "relationships", "children"],
            compatible_concerns=["focus", "peace", "success", "healing", "protection"],
            catalog_version=CATALOG_VERSION
        )
        
        self.remedies["remedy-muhurta-selection"] = Remedy(
            remedy_id="remedy-muhurta-selection",
            slug="muhurta-selection",
            name="Muhurta Selection",
            description="Auspicious timing selection for your specific action or decision.",
            category=RemedyCategory.ASTROLOGICAL,
            sub_type="muhurta",
            price_inr=999,
            what_included=[
                "Analysis of your birth chart",
                "3 optimal date/time options",
                "Backup dates if needed",
                "Pre-action guidelines"
            ],
            how_it_works=[
                "Purchase this add-on",
                "Provide details of planned action",
                "Receive muhurta options within 24 hours"
            ],
            delivery_timeline="24 hours",
            fulfillment_type="digital",
            compatible_topics=["career", "money", "relationships", "family"],
            compatible_concerns=["timing", "new_start", "important_decision"],
            catalog_version=CATALOG_VERSION
        )
        
        # Spiritual Remedies
        self.remedies["remedy-career-puja"] = Remedy(
            remedy_id="remedy-career-puja",
            slug="career-puja",
            name="Career Success Puja",
            description="Temple ritual specifically for career success and professional growth.",
            category=RemedyCategory.SPIRITUAL,
            sub_type="temple_puja",
            price_inr=2499,
            what_included=[
                "Puja at designated temple",
                "Performed on auspicious day",
                "Sankalpa with your name and goal",
                "Video/photos of ritual",
                "Prasad delivery (optional)"
            ],
            how_it_works=[
                "Purchase this add-on",
                "We schedule puja on auspicious day",
                "Ritual performed with your sankalpa",
                "Receive video and prasad within 7 days"
            ],
            delivery_timeline="5-7 days",
            fulfillment_type="service",
            compatible_topics=["career"],
            compatible_concerns=["job_change", "promotion", "business_start", "success"],
            catalog_version=CATALOG_VERSION
        )
        
        self.remedies["remedy-relationship-puja"] = Remedy(
            remedy_id="remedy-relationship-puja",
            slug="relationship-puja",
            name="Relationship Harmony Puja",
            description="Temple ritual for relationship harmony and resolution of conflicts.",
            category=RemedyCategory.SPIRITUAL,
            sub_type="temple_puja",
            price_inr=2999,
            what_included=[
                "Puja for relationship harmony",
                "Performed at relationship-specific temple",
                "Both partners' names in sankalpa",
                "Video/photos of ritual",
                "Prasad delivery"
            ],
            how_it_works=[
                "Purchase this add-on",
                "Provide both names and relationship details",
                "Puja scheduled on favorable day",
                "Receive video and prasad within 7 days"
            ],
            delivery_timeline="5-7 days",
            fulfillment_type="service",
            compatible_topics=["relationships", "family"],
            compatible_concerns=["marriage", "harmony", "conflict", "compatibility"],
            catalog_version=CATALOG_VERSION
        )
        
        self.remedies["remedy-lakshmi-puja"] = Remedy(
            remedy_id="remedy-lakshmi-puja",
            slug="lakshmi-puja",
            name="Lakshmi Abundance Puja",
            description="Sacred ritual to invite abundance and remove financial obstacles.",
            category=RemedyCategory.SPIRITUAL,
            sub_type="temple_puja",
            price_inr=3499,
            what_included=[
                "Full Lakshmi puja ritual",
                "Performed on auspicious Friday or Diwali",
                "108 offerings with your sankalpa",
                "Video of complete ritual",
                "Energized coin prasad"
            ],
            how_it_works=[
                "Purchase this add-on",
                "We schedule on next auspicious day",
                "Complete ritual with your sankalpa",
                "Receive video and prasad within 10 days"
            ],
            delivery_timeline="7-10 days",
            fulfillment_type="service",
            compatible_topics=["money"],
            compatible_concerns=["wealth", "abundance", "debt", "business"],
            catalog_version=CATALOG_VERSION
        )
        
        self.remedies["remedy-navagraha-shanti"] = Remedy(
            remedy_id="remedy-navagraha-shanti",
            slug="navagraha-shanti",
            name="Navagraha Shanti Puja",
            description="Complete planetary pacification ritual for overall balance.",
            category=RemedyCategory.SPIRITUAL,
            sub_type="havan",
            price_inr=4999,
            what_included=[
                "Complete Navagraha havan",
                "All 9 planetary mantras",
                "Performed by experienced pandits",
                "Full video documentation",
                "Blessed items from ritual"
            ],
            how_it_works=[
                "Purchase this add-on",
                "We analyze your chart for focus planets",
                "Havan performed on auspicious muhurta",
                "Receive video and items within 14 days"
            ],
            delivery_timeline="10-14 days",
            fulfillment_type="service",
            compatible_topics=["health", "career", "relationships", "family"],
            compatible_concerns=["balance", "protection", "healing", "obstacles"],
            catalog_version=CATALOG_VERSION
        )
        
        self.remedies["remedy-child-blessing-puja"] = Remedy(
            remedy_id="remedy-child-blessing-puja",
            slug="child-blessing-puja",
            name="Child Blessing Puja",
            description="Special puja for child's wellbeing, education, and bright future.",
            category=RemedyCategory.SPIRITUAL,
            sub_type="temple_puja",
            price_inr=2499,
            what_included=[
                "Puja for child's success and protection",
                "Performed at Saraswati/Ganesha temple",
                "Child's name and DOB in sankalpa",
                "Video of ritual",
                "Blessed educational items"
            ],
            how_it_works=[
                "Purchase this add-on",
                "Provide child's details",
                "Puja on auspicious education muhurta",
                "Receive video and items within 7 days"
            ],
            delivery_timeline="5-7 days",
            fulfillment_type="service",
            compatible_topics=["children"],
            compatible_concerns=["education", "protection", "success", "health"],
            catalog_version=CATALOG_VERSION
        )
        
        # Healing Remedies
        self.remedies["remedy-crystal-kit"] = Remedy(
            remedy_id="remedy-crystal-kit",
            slug="crystal-kit",
            name="Crystal Healing Kit",
            description="Personalized crystal set selected for your specific needs and chart.",
            category=RemedyCategory.HEALING,
            sub_type="crystal",
            price_inr=1999,
            what_included=[
                "3 crystals selected for your needs",
                "Cleansing and charging instructions",
                "Placement and usage guide",
                "Crystal pouch for carrying"
            ],
            how_it_works=[
                "Purchase this add-on",
                "We analyze your needs and chart",
                "Crystals selected and cleansed",
                "Delivered within 7 days"
            ],
            delivery_timeline="5-7 days",
            fulfillment_type="physical",
            compatible_topics=["health", "relationships", "career"],
            compatible_concerns=["energy", "protection", "healing", "peace"],
            catalog_version=CATALOG_VERSION
        )
        
        self.remedies["remedy-chakra-balancing"] = Remedy(
            remedy_id="remedy-chakra-balancing",
            slug="chakra-balancing",
            name="Chakra Balancing Session",
            description="Remote energy healing session to balance your chakras.",
            category=RemedyCategory.HEALING,
            sub_type="chakra_balancing",
            price_inr=1999,
            what_included=[
                "45-minute remote healing session",
                "Chakra assessment",
                "Balancing and clearing",
                "Post-session guidance",
                "Recording of session insights"
            ],
            how_it_works=[
                "Purchase this add-on",
                "Schedule your session",
                "Attend remote healing (Zoom)",
                "Receive insights and guidance"
            ],
            delivery_timeline="Scheduled session",
            fulfillment_type="service",
            requires_consultation=True,
            compatible_topics=["health", "relationships"],
            compatible_concerns=["energy", "healing", "emotional_balance", "stress"],
            catalog_version=CATALOG_VERSION
        )
        
        self.remedies["remedy-education-yantra"] = Remedy(
            remedy_id="remedy-education-yantra",
            slug="education-yantra",
            name="Education Success Yantra",
            description="Saraswati yantra for academic success and learning.",
            category=RemedyCategory.ASTROLOGICAL,
            sub_type="yantra",
            price_inr=1499,
            what_included=[
                "Energized Saraswati/Vidya yantra",
                "Study placement guidelines",
                "Activation mantra",
                "Care instructions"
            ],
            how_it_works=[
                "Purchase this add-on",
                "Yantra energized for your child",
                "Delivered with placement guide",
                "Place in study area as directed"
            ],
            delivery_timeline="7-10 days",
            fulfillment_type="physical",
            compatible_topics=["children"],
            compatible_concerns=["education", "focus", "learning", "exams"],
            catalog_version=CATALOG_VERSION
        )
    
    # =========================================================================
    # QUERY METHODS
    # =========================================================================
    
    def get_package(self, package_id: str) -> Optional[Package]:
        """Get package by ID"""
        return self.packages.get(package_id)
    
    def get_remedy(self, remedy_id: str) -> Optional[Remedy]:
        """Get remedy by ID"""
        return self.remedies.get(remedy_id)
    
    def get_consult_policy(self, policy_id: str) -> Optional[ConsultPolicy]:
        """Get consultation policy by ID"""
        return self.consult_policies.get(policy_id)
    
    def get_all_packages(self, topic: Optional[str] = None, branch: Optional[str] = None, active_only: bool = True) -> List[Package]:
        """Get all packages with optional filtering"""
        packages = list(self.packages.values())
        
        if active_only:
            packages = [p for p in packages if p.is_active]
        
        if topic:
            packages = [p for p in packages if p.topic.value == topic]
        
        if branch:
            packages = [p for p in packages if p.branch.value == branch]
        
        return packages
    
    def get_all_remedies(self, category: Optional[str] = None, topic: Optional[str] = None, active_only: bool = True) -> List[Remedy]:
        """Get all remedies with optional filtering"""
        remedies = list(self.remedies.values())
        
        if active_only:
            remedies = [r for r in remedies if r.is_active]
        
        if category:
            remedies = [r for r in remedies if r.category.value == category]
        
        if topic:
            remedies = [r for r in remedies if topic in r.compatible_topics]
        
        return remedies
    
    def get_package_with_policy(self, package_id: str) -> Optional[Dict]:
        """Get package with resolved consultation policy"""
        package = self.get_package(package_id)
        if not package:
            return None
        
        result = package.model_dump()
        
        if package.consult_policy_id:
            policy = self.get_consult_policy(package.consult_policy_id)
            if policy:
                result['consult_policy'] = policy.model_dump()
        
        # Resolve suggested remedies
        result['suggested_remedies'] = [
            self.get_remedy(rid).model_dump() 
            for rid in package.suggested_remedy_ids 
            if self.get_remedy(rid)
        ]
        
        return result
    
    def validate_package_id(self, package_id: str) -> bool:
        """Check if package ID exists in catalog"""
        return package_id in self.packages
    
    def validate_remedy_id(self, remedy_id: str) -> bool:
        """Check if remedy ID exists in catalog"""
        return remedy_id in self.remedies
    
    def get_packages_for_topic(self, topic: str) -> List[Package]:
        """Get all packages for a specific topic"""
        return self.get_all_packages(topic=topic)
    
    def get_suggested_remedies_for_package(self, package_id: str) -> List[Remedy]:
        """Get suggested remedies for a package"""
        package = self.get_package(package_id)
        if not package:
            return []
        
        return [
            self.get_remedy(rid) 
            for rid in package.suggested_remedy_ids 
            if self.get_remedy(rid)
        ]


# Singleton instance
_catalog_service: Optional[CatalogService] = None


def get_catalog_service() -> CatalogService:
    """Get or create catalog service singleton"""
    global _catalog_service
    if _catalog_service is None:
        _catalog_service = CatalogService()
    return _catalog_service
