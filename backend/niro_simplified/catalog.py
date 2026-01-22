"""NIRO Simplified V1 - Catalog Service

Source of truth for topics, experts, scenarios, tiers, and tools.
"""

import logging
from typing import List, Optional, Dict
from .models import (
    Topic, ExpertProfile, ScenarioChip, PackTier, TopicFreeTool,
    AccessPolicy, UnlimitedAccessConditions
)

logger = logging.getLogger(__name__)

CATALOG_VERSION = "2025.01.simplified.v1"


class SimplifiedCatalog:
    """Manages all catalog data for NIRO Simplified"""
    
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.experts: Dict[str, ExpertProfile] = {}
        self.scenarios: Dict[str, ScenarioChip] = {}
        self.tiers: Dict[str, PackTier] = {}
        self.tools: Dict[str, TopicFreeTool] = {}
        self.unlimited_conditions = UnlimitedAccessConditions()
        
        # Seed all data
        self._seed_topics()
        self._seed_experts()
        self._seed_scenarios()
        self._seed_tiers()
        self._seed_tools()
        
        logger.info(f"SimplifiedCatalog initialized: {len(self.topics)} topics, {len(self.experts)} experts")
    
    # =========================================================================
    # SEED TOPICS (12 topics)
    # =========================================================================
    
    def _seed_topics(self):
        """Seed all 14 life topics - V2: Added Meditation and Counseling"""
        topics_data = [
            ("career", "Career & Work", "💼", "Navigate your professional path", "blue", 1),
            ("money", "Money & Financial Stability", "💰", "Achieve financial clarity", "yellow", 2),
            ("health", "Health & Wellbeing", "🏥", "Optimize your vitality", "green", 3),
            ("marriage", "Marriage & Family", "💑", "Strengthen family bonds", "purple", 4),
            ("children", "Children & Education", "👶", "Guide your child's future", "orange", 5),
            ("love", "Love & Relationships", "💕", "Find harmony in love", "pink", 6),
            ("business", "Business & Entrepreneurship", "🚀", "Grow your venture", "indigo", 7),
            ("travel", "Travel / Relocation / Foreign Settlement", "✈️", "Plan your move", "cyan", 8),
            ("property", "Property & Home", "🏠", "Make smart property decisions", "amber", 9),
            ("mental_health", "Mental Health / Stress / Emotional Balance", "🧠", "Find inner peace", "teal", 10),
            ("spiritual", "Spiritual Growth / Purpose", "🙏", "Discover your path", "violet", 11),
            ("legal", "Legal / Conflict / Disputes", "⚖️", "Resolve with clarity", "slate", 12),
            ("meditation", "Meditation & Mindfulness", "🧘", "Cultivate inner stillness", "indigo", 13),
            ("counseling", "Counseling & Life Guidance", "💬", "Professional support for life challenges", "emerald", 14),
        ]
        
        modality_map = {
            "career": ["vedic_astrologer", "numerologist", "life_coach"],
            "money": ["vedic_astrologer", "numerologist", "life_coach"],
            "health": ["vedic_astrologer", "healer", "life_coach", "spiritual_guide"],
            "marriage": ["vedic_astrologer", "marriage_counselor", "relationship_counselor", "palmist"],
            "children": ["vedic_astrologer", "numerologist", "life_coach", "healer"],
            "love": ["vedic_astrologer", "tarot", "relationship_counselor", "psychic"],
            "business": ["vedic_astrologer", "numerologist", "life_coach"],
            "travel": ["vedic_astrologer", "numerologist", "life_coach"],
            "property": ["vedic_astrologer", "numerologist"],
            "mental_health": ["healer", "life_coach", "spiritual_guide", "psychic", "wellness_counselor"],
            "spiritual": ["spiritual_guide", "vedic_astrologer", "healer", "psychic"],
            "legal": ["vedic_astrologer", "numerologist"],
            "meditation": ["meditation_guru", "spiritual_guide", "healer", "life_coach"],
            "counseling": ["wellness_counselor", "life_coach", "relationship_counselor", "spiritual_guide"],
        }
        
        for topic_id, label, icon, tagline, color, order in topics_data:
            self.topics[topic_id] = Topic(
                topic_id=topic_id,
                label=label,
                icon=icon,
                tagline=tagline,
                color_scheme=color,
                expert_modalities=modality_map.get(topic_id, []),
                display_order=order
            )
    
    # =========================================================================
    # SEED EXPERTS - V1.5: Full expert profiles with photos for all topics
    # =========================================================================
    
    def _seed_experts(self):
        """Seed expert profiles - V1.5: All topics with proper photos"""
        
        # Use placeholder images from UI Faces / random user API
        # These are real-looking professional photos
        photo_urls = [
            "https://randomuser.me/api/portraits/men/32.jpg",
            "https://randomuser.me/api/portraits/women/44.jpg",
            "https://randomuser.me/api/portraits/men/52.jpg",
            "https://randomuser.me/api/portraits/women/67.jpg",
            "https://randomuser.me/api/portraits/men/75.jpg",
            "https://randomuser.me/api/portraits/women/79.jpg",
            "https://randomuser.me/api/portraits/men/81.jpg",
            "https://randomuser.me/api/portraits/women/85.jpg",
            "https://randomuser.me/api/portraits/men/86.jpg",
            "https://randomuser.me/api/portraits/women/90.jpg",
            "https://randomuser.me/api/portraits/men/91.jpg",
            "https://randomuser.me/api/portraits/women/92.jpg",
            "https://randomuser.me/api/portraits/men/94.jpg",
            "https://randomuser.me/api/portraits/women/95.jpg",
            "https://randomuser.me/api/portraits/men/97.jpg",
            "https://randomuser.me/api/portraits/women/17.jpg",
            "https://randomuser.me/api/portraits/men/22.jpg",
            "https://randomuser.me/api/portraits/women/28.jpg",
            "https://randomuser.me/api/portraits/men/33.jpg",
            "https://randomuser.me/api/portraits/women/35.jpg",
        ]
        
        # Career experts
        career_experts = [
            ("exp_001", "Pandit Rajesh Sharma", "vedic_astrologer", "Vedic Astrologer", 
             ["Career timing", "Job changes", "Promotion guidance"], 
             "15+ years helping professionals find their true calling through Vedic wisdom.",
             ["Hindi", "English"], 15, 4.9, 500, photo_urls[0]),
            
            ("exp_002", "Dr. Ananya Mehta", "career_coach", "Career Coach",
             ["Career transitions", "Leadership", "Work-life balance"],
             "IIM-trained coach specializing in mid-career pivots and executive coaching.",
             ["English", "Hindi"], 12, 4.8, 350, photo_urls[1]),
            
            ("exp_003", "Acharya Suresh Joshi", "numerologist", "Numerologist",
             ["Name analysis", "Business timing", "Lucky numbers"],
             "Expert in career numerology. Helped 1000+ professionals optimize their path.",
             ["Hindi", "Marathi", "English"], 20, 4.7, 800, photo_urls[2]),
            
            ("exp_004", "Priya Krishnamurthy", "life_coach", "Life Coach",
             ["Goal setting", "Motivation", "Career clarity"],
             "ICF-certified coach helping you unlock your professional potential.",
             ["English", "Tamil"], 8, 4.9, 280, photo_urls[3]),
            
            ("exp_005", "Guru Venkatesh Iyer", "vedic_astrologer", "Vedic Astrologer",
             ["Dasha analysis", "Transit guidance", "Muhurta selection"],
             "Traditional Vedic astrologer with deep expertise in career horoscopes.",
             ["Hindi", "English", "Kannada"], 25, 4.8, 1200, photo_urls[4]),
            
            ("exp_006", "Meera Sundaram", "tarot", "Tarot Reader",
             ["Decision guidance", "Path clarity", "Opportunity insights"],
             "Intuitive tarot reader specializing in career crossroads.",
             ["English", "Tamil"], 10, 4.6, 450, photo_urls[5]),
            
            ("exp_007", "Ramesh Kulkarni", "palmist", "Palmist",
             ["Career lines", "Success timing", "Talent identification"],
             "3rd generation palmist known for accurate career predictions.",
             ["Hindi", "Marathi"], 18, 4.7, 600, photo_urls[6]),
            
            ("exp_008", "Dr. Shalini Rao", "western_astrologer", "Western Astrologer",
             ["Career transits", "Professional cycles", "Opportunity windows"],
             "PhD in psychology with expertise in Western career astrology.",
             ["English"], 14, 4.8, 320, photo_urls[7]),
        ]
        
        idx = 0
        for exp_id, name, modality, modality_label, tags, bio, languages, years, rating, consults, photo in career_experts:
            self.experts[exp_id] = ExpertProfile(
                expert_id=exp_id,
                name=name,
                photo_url=photo,
                modality=modality,
                modality_label=modality_label,
                topics=["career", "business"],  # Career experts can also help with business
                languages=languages,
                best_for_tags=tags,
                short_bio=bio,
                experience_years=years,
                rating=rating,
                total_consultations=consults,
                display_order=idx + 1
            )
            idx += 1
        
        # Money experts
        money_experts = [
            ("exp_101", "Pandit Ashok Trivedi", "vedic_astrologer", "Vedic Astrologer", 
             ["Wealth yoga", "Investment timing", "Property matters"],
             "Expert in Dhana yoga analysis. 18 years of financial astrology experience.",
             ["Hindi", "English"], 18, 4.8, 650, photo_urls[8]),
            ("exp_102", "CA Vikram Desai", "financial_advisor", "Financial Advisor", 
             ["Tax planning", "Investments", "Wealth building"],
             "Chartered Accountant with 15 years experience in personal finance.",
             ["English", "Gujarati", "Hindi"], 15, 4.9, 420, photo_urls[9]),
            ("exp_103", "Lakshmi Narayan", "numerologist", "Numerologist",
             ["Lucky numbers", "Business name", "Financial timing"],
             "Numerology expert specializing in wealth and abundance.",
             ["Hindi", "Telugu"], 12, 4.7, 380, photo_urls[10]),
        ]
        
        for exp_id, name, modality, modality_label, tags, bio, languages, years, rating, consults, photo in money_experts:
            self.experts[exp_id] = ExpertProfile(
                expert_id=exp_id,
                name=name,
                photo_url=photo,
                modality=modality,
                modality_label=modality_label,
                topics=["money", "property", "business"],
                languages=languages,
                best_for_tags=tags,
                short_bio=bio,
                experience_years=years,
                rating=rating,
                total_consultations=consults,
                display_order=idx + 1
            )
            idx += 1
        
        # Love & Relationships experts
        love_experts = [
            ("exp_201", "Madhu Sharma", "tarot", "Tarot Reader", 
             ["Love readings", "Relationship insights", "Soulmate guidance"],
             "Intuitive tarot reader with a gift for relationship clarity.",
             ["Hindi", "English"], 8, 4.8, 520, photo_urls[11]),
            ("exp_202", "Dr. Kavita Nair", "relationship_counselor", "Relationship Counselor", 
             ["Communication", "Conflict resolution", "Intimacy"],
             "Clinical psychologist specializing in couples therapy.",
             ["English", "Malayalam"], 14, 4.9, 380, photo_urls[12]),
            ("exp_203", "Pandit Mohan Das", "vedic_astrologer", "Vedic Astrologer",
             ["Compatibility", "Marriage timing", "Relationship karma"],
             "Vedic astrologer with expertise in 7th house analysis.",
             ["Hindi", "Bengali"], 20, 4.7, 890, photo_urls[13]),
        ]
        
        for exp_id, name, modality, modality_label, tags, bio, languages, years, rating, consults, photo in love_experts:
            self.experts[exp_id] = ExpertProfile(
                expert_id=exp_id,
                name=name,
                photo_url=photo,
                modality=modality,
                modality_label=modality_label,
                topics=["love", "marriage"],
                languages=languages,
                best_for_tags=tags,
                short_bio=bio,
                experience_years=years,
                rating=rating,
                total_consultations=consults,
                display_order=idx + 1
            )
            idx += 1
        
        # Health experts
        health_experts = [
            ("exp_301", "Vaidya Ramakrishna", "healer", "Ayurvedic Healer", 
             ["Holistic health", "Dosha balance", "Natural remedies"],
             "Traditional Ayurvedic practitioner from Kerala lineage.",
             ["Hindi", "Malayalam", "English"], 22, 4.9, 750, photo_urls[14]),
            ("exp_302", "Yogini Lakshmi", "spiritual_guide", "Yoga & Wellness Guide", 
             ["Stress relief", "Mindfulness", "Yoga therapy"],
             "Certified yoga therapist and meditation instructor.",
             ["English", "Hindi"], 10, 4.8, 420, photo_urls[15]),
            ("exp_303", "Dr. Arjun Menon", "vedic_astrologer", "Medical Astrologer",
             ["Health timing", "Disease prevention", "Recovery periods"],
             "Specialized in medical astrology and health predictions.",
             ["English", "Hindi", "Tamil"], 16, 4.7, 580, photo_urls[16]),
        ]
        
        for exp_id, name, modality, modality_label, tags, bio, languages, years, rating, consults, photo in health_experts:
            self.experts[exp_id] = ExpertProfile(
                expert_id=exp_id,
                name=name,
                photo_url=photo,
                modality=modality,
                modality_label=modality_label,
                topics=["health", "mental_health"],
                languages=languages,
                best_for_tags=tags,
                short_bio=bio,
                experience_years=years,
                rating=rating,
                total_consultations=consults,
                display_order=idx + 1
            )
            idx += 1
        
        # Spiritual & Mental Health experts
        spiritual_experts = [
            ("exp_401", "Swami Ananda", "spiritual_guide", "Spiritual Guide", 
             ["Life purpose", "Meditation", "Inner peace"],
             "Spiritual teacher helping seekers find their path.",
             ["Hindi", "English"], 25, 4.9, 1100, photo_urls[17]),
            ("exp_402", "Dr. Nirmala Devi", "psychic", "Psychic Counselor", 
             ["Intuitive guidance", "Energy healing", "Past life"],
             "Gifted psychic with clinical psychology background.",
             ["English", "Hindi"], 18, 4.8, 680, photo_urls[18]),
        ]
        
        for exp_id, name, modality, modality_label, tags, bio, languages, years, rating, consults, photo in spiritual_experts:
            self.experts[exp_id] = ExpertProfile(
                expert_id=exp_id,
                name=name,
                photo_url=photo,
                modality=modality,
                modality_label=modality_label,
                topics=["spiritual", "mental_health"],
                languages=languages,
                best_for_tags=tags,
                short_bio=bio,
                experience_years=years,
                rating=rating,
                total_consultations=consults,
                display_order=idx + 1
            )
            idx += 1
        
        # Marriage & Family experts
        marriage_experts = [
            ("exp_501", "Pandit Rameshwar Shastri", "vedic_astrologer", "Vedic Astrologer", 
             ["Kundli matching", "Marriage muhurat", "Family harmony"],
             "Expert in Kundli matching with 30+ years experience.",
             ["Hindi", "Sanskrit"], 30, 4.9, 2500, photo_urls[19]),
            ("exp_502", "Dr. Seema Kapoor", "marriage_counselor", "Marriage Counselor",
             ["Couples therapy", "Family dynamics", "In-law issues"],
             "Family therapist helping couples build stronger bonds.",
             ["Hindi", "English"], 15, 4.8, 620, photo_urls[0]),
        ]
        
        for exp_id, name, modality, modality_label, tags, bio, languages, years, rating, consults, photo in marriage_experts:
            self.experts[exp_id] = ExpertProfile(
                expert_id=exp_id,
                name=name,
                photo_url=photo,
                modality=modality,
                modality_label=modality_label,
                topics=["marriage", "children"],
                languages=languages,
                best_for_tags=tags,
                short_bio=bio,
                experience_years=years,
                rating=rating,
                total_consultations=consults,
                display_order=idx + 1
            )
            idx += 1
        
        # Travel & Relocation experts  
        travel_experts = [
            ("exp_601", "Astro Pankaj Kumar", "vedic_astrologer", "Vedic Astrologer",
             ["Foreign settlement", "Visa timing", "Travel muhurat"],
             "Specialist in 9th and 12th house analysis for foreign matters.",
             ["Hindi", "English"], 12, 4.7, 380, photo_urls[1]),
        ]
        
        for exp_id, name, modality, modality_label, tags, bio, languages, years, rating, consults, photo in travel_experts:
            self.experts[exp_id] = ExpertProfile(
                expert_id=exp_id,
                name=name,
                photo_url=photo,
                modality=modality,
                modality_label=modality_label,
                topics=["travel"],
                languages=languages,
                best_for_tags=tags,
                short_bio=bio,
                experience_years=years,
                rating=rating,
                total_consultations=consults,
                display_order=idx + 1
            )
            idx += 1
        
        # Legal experts - V2: Astro-focused
        legal_experts = [
            ("exp_701", "Pandit Dharmaraj", "vedic_astrologer", "Vedic Astrologer",
             ["Court timing", "Legal disputes", "Settlement periods"],
             "Vedic astrologer specializing in 6th and 12th house matters for legal issues.",
             ["Hindi", "English"], 20, 4.6, 340, photo_urls[2]),
        ]
        
        for exp_id, name, modality, modality_label, tags, bio, languages, years, rating, consults, photo in legal_experts:
            self.experts[exp_id] = ExpertProfile(
                expert_id=exp_id,
                name=name,
                photo_url=photo,
                modality=modality,
                modality_label=modality_label,
                topics=["legal", "property"],
                languages=languages,
                best_for_tags=tags,
                short_bio=bio,
                experience_years=years,
                rating=rating,
                total_consultations=consults,
                display_order=idx + 1
            )
            idx += 1
        
        # Meditation experts - V2: NEW TOPIC
        meditation_experts = [
            ("exp_801", "Guru Shankarananda", "meditation_guru", "Meditation Guru",
             ["Deep meditation", "Breathwork", "Stress relief"],
             "40+ years practicing and teaching Himalayan meditation traditions.",
             ["Hindi", "English", "Sanskrit"], 40, 4.9, 2200, photo_urls[3]),
            ("exp_802", "Swami Dhyananda", "spiritual_guide", "Spiritual Guide",
             ["Mindfulness", "Inner peace", "Daily practice"],
             "Spiritual teacher trained in Vipassana and Zen traditions.",
             ["English", "Hindi"], 18, 4.8, 980, photo_urls[5]),
            ("exp_803", "Dr. Priya Shankar", "healer", "Wellness Healer",
             ["Chakra meditation", "Sound healing", "Energy work"],
             "PhD in psychology with expertise in meditative healing practices.",
             ["English", "Tamil"], 15, 4.7, 620, photo_urls[7]),
            ("exp_804", "Yogini Kavya", "life_coach", "Mindfulness Coach",
             ["Anxiety relief", "Sleep meditation", "Beginner guidance"],
             "Certified mindfulness instructor helping busy professionals find calm.",
             ["English", "Hindi"], 8, 4.8, 340, photo_urls[9]),
        ]
        
        for exp_id, name, modality, modality_label, tags, bio, languages, years, rating, consults, photo in meditation_experts:
            self.experts[exp_id] = ExpertProfile(
                expert_id=exp_id,
                name=name,
                photo_url=photo,
                modality=modality,
                modality_label=modality_label,
                topics=["meditation", "spiritual", "mental_health"],
                languages=languages,
                best_for_tags=tags,
                short_bio=bio,
                experience_years=years,
                rating=rating,
                total_consultations=consults,
                display_order=idx + 1
            )
            idx += 1
        
        # Counseling experts - V2: NEW TOPIC
        counseling_experts = [
            ("exp_901", "Dr. Meena Iyer", "wellness_counselor", "Wellness Counselor",
             ["Life transitions", "Emotional support", "Personal growth"],
             "Clinical psychologist with holistic approach to wellbeing.",
             ["English", "Hindi", "Malayalam"], 16, 4.9, 890, photo_urls[11]),
            ("exp_902", "Swami Prakashananda", "spiritual_guide", "Spiritual Counselor",
             ["Purpose discovery", "Life direction", "Spiritual crisis"],
             "Spiritual guide helping seekers navigate life's deeper questions.",
             ["Hindi", "English"], 25, 4.8, 1450, photo_urls[13]),
            ("exp_903", "Sunita Devi", "life_coach", "Life Coach",
             ["Goal clarity", "Decision making", "Confidence building"],
             "ICF-certified coach with intuitive counseling abilities.",
             ["English", "Hindi", "Gujarati"], 12, 4.7, 560, photo_urls[15]),
            ("exp_904", "Dr. Rahul Nair", "relationship_counselor", "Relationship Counselor",
             ["Family dynamics", "Communication", "Conflict resolution"],
             "Family therapist combining psychology with astrological insights.",
             ["English", "Malayalam"], 14, 4.8, 720, photo_urls[17]),
        ]
        
        for exp_id, name, modality, modality_label, tags, bio, languages, years, rating, consults, photo in counseling_experts:
            self.experts[exp_id] = ExpertProfile(
                expert_id=exp_id,
                name=name,
                photo_url=photo,
                modality=modality,
                modality_label=modality_label,
                topics=["counseling", "mental_health", "spiritual"],
                languages=languages,
                best_for_tags=tags,
                short_bio=bio,
                experience_years=years,
                rating=rating,
                total_consultations=consults,
                display_order=idx + 1
            )
            idx += 1
    
    # =========================================================================
    # SEED SCENARIOS
    # =========================================================================
    
    def _seed_scenarios(self):
        """Seed scenario chips for all topics"""
        
        scenarios_data = {
            "career": [
                ("sc_c01", "Job change", "high", "plus"),
                ("sc_c02", "Promotion stuck", "medium", "plus"),
                ("sc_c03", "Career switch", "high", "pro"),
                ("sc_c04", "Starting a business", "high", "pro"),
                ("sc_c05", "Timing questions", "medium", "plus"),
                ("sc_c06", "Work-life balance", "low", "starter"),
                ("sc_c07", "Skill uncertainty", "low", "starter"),
                ("sc_c08", "Layoff concerns", "high", "plus"),
            ],
            "money": [
                ("sc_m01", "Debt stress", "high", "plus"),
                ("sc_m02", "Investment timing", "medium", "plus"),
                ("sc_m03", "Business losses", "high", "pro"),
                ("sc_m04", "Salary negotiation", "medium", "starter"),
                ("sc_m05", "Property decisions", "high", "plus"),
                ("sc_m06", "Inheritance matters", "medium", "pro"),
            ],
            "love": [
                ("sc_l01", "Breakup recovery", "high", "plus"),
                ("sc_l02", "Marriage decision", "high", "pro"),
                ("sc_l03", "Compatibility doubts", "medium", "plus"),
                ("sc_l04", "Communication issues", "medium", "starter"),
                ("sc_l05", "Family opposition", "high", "plus"),
                ("sc_l06", "Long distance", "medium", "starter"),
            ],
            "health": [
                ("sc_h01", "Chronic illness", "high", "pro"),
                ("sc_h02", "Energy/fatigue", "medium", "plus"),
                ("sc_h03", "Sleep issues", "medium", "starter"),
                ("sc_h04", "Stress/anxiety", "high", "plus"),
                ("sc_h05", "Lifestyle change", "low", "starter"),
            ],
            "marriage": [
                ("sc_mr01", "Compatibility issues", "high", "plus"),
                ("sc_mr02", "Communication breakdown", "high", "pro"),
                ("sc_mr03", "In-law conflicts", "medium", "plus"),
                ("sc_mr04", "Intimacy concerns", "medium", "plus"),
                ("sc_mr05", "Separation thoughts", "high", "pro"),
            ],
            "children": [
                ("sc_ch01", "Education decisions", "medium", "plus"),
                ("sc_ch02", "Child behavior", "medium", "plus"),
                ("sc_ch03", "Career guidance for child", "low", "starter"),
                ("sc_ch04", "Learning difficulties", "high", "pro"),
            ],
            "business": [
                ("sc_b01", "Startup timing", "high", "pro"),
                ("sc_b02", "Partnership issues", "high", "plus"),
                ("sc_b03", "Expansion decisions", "medium", "plus"),
                ("sc_b04", "Cash flow problems", "high", "pro"),
            ],
            "travel": [
                ("sc_t01", "Relocation decision", "high", "plus"),
                ("sc_t02", "Foreign settlement", "high", "pro"),
                ("sc_t03", "Visa timing", "medium", "plus"),
                ("sc_t04", "Job abroad", "high", "plus"),
            ],
            "property": [
                ("sc_p01", "Buy/sell timing", "high", "plus"),
                ("sc_p02", "Legal disputes", "high", "pro"),
                ("sc_p03", "Construction timing", "medium", "plus"),
                ("sc_p04", "Vastu concerns", "medium", "starter"),
            ],
            "mental_health": [
                ("sc_mh01", "Anxiety", "high", "plus"),
                ("sc_mh02", "Depression", "high", "pro"),
                ("sc_mh03", "Stress management", "medium", "starter"),
                ("sc_mh04", "Life transitions", "medium", "plus"),
                ("sc_mh05", "Burnout", "high", "plus"),
            ],
            "spiritual": [
                ("sc_sp01", "Purpose seeking", "medium", "plus"),
                ("sc_sp02", "Spiritual practices", "low", "starter"),
                ("sc_sp03", "Karma understanding", "medium", "plus"),
                ("sc_sp04", "Meditation guidance", "low", "starter"),
            ],
            "legal": [
                ("sc_lg01", "Divorce proceedings", "high", "pro"),
                ("sc_lg02", "Property disputes", "high", "pro"),
                ("sc_lg03", "Business conflicts", "high", "plus"),
                ("sc_lg04", "Court timing", "high", "plus"),
            ],
            "meditation": [
                ("sc_med01", "Starting meditation", "low", "starter"),
                ("sc_med02", "Deep practice guidance", "medium", "plus"),
                ("sc_med03", "Anxiety/stress relief", "high", "plus"),
                ("sc_med04", "Sleep improvement", "medium", "plus"),
                ("sc_med05", "Advanced techniques", "medium", "pro"),
            ],
            "counseling": [
                ("sc_coun01", "Life direction", "high", "plus"),
                ("sc_coun02", "Relationship guidance", "high", "plus"),
                ("sc_coun03", "Personal growth", "medium", "starter"),
                ("sc_coun04", "Career counseling", "high", "plus"),
                ("sc_coun05", "Family dynamics", "high", "pro"),
                ("sc_coun06", "Emotional healing", "high", "pro"),
            ],
        }
        
        for topic_id, scenarios in scenarios_data.items():
            for idx, (sc_id, label, urgency, tier) in enumerate(scenarios):
                self.scenarios[sc_id] = ScenarioChip(
                    scenario_id=sc_id,
                    topic_id=topic_id,
                    label=label,
                    urgency_hint=urgency,
                    recommended_tier=tier,
                    display_order=idx + 1
                )
    
    # =========================================================================
    # SEED TIERS (Starter/Plus/Pro for all topics)
    # =========================================================================
    
    def _seed_tiers(self):
        """Seed pack tiers for all topics"""
        
        tier_templates = [
            ("starter", "Starter", 2999, 4, False, AccessPolicy(
                chat_sla_hours=24,
                calls_enabled=False,
                calls_per_month=0,
                max_active_expert_threads=1,
                free_tools_access=False
            ), [
                "Unlimited expert chat (24hr response)",
                "1 expert at a time",
                "4 weeks validity",
            ]),
            ("plus", "Plus", 4999, 8, True, AccessPolicy(
                chat_sla_hours=24,
                calls_enabled=True,
                calls_per_month=2,
                call_duration_minutes=60,
                max_active_expert_threads=3,
                free_tools_access=True
            ), [
                "Unlimited expert chat (24hr response)",
                "Up to 3 experts",
                "2 video calls/month (60 min each)",
                "Access to free tools",
                "8 weeks validity",
            ]),
            ("pro", "Pro", 7999, 12, False, AccessPolicy(
                chat_sla_hours=24,
                calls_enabled=True,
                calls_per_month=4,
                call_duration_minutes=60,
                max_active_expert_threads=-1,  # Unlimited
                free_tools_access=True
            ), [
                "Unlimited expert chat (24hr response)",
                "Unlimited experts",
                "4 video calls/month (60 min each)",
                "Access to free tools",
                "Priority support",
                "12 weeks validity",
            ]),
        ]
        
        for topic_id in self.topics.keys():
            topic = self.topics[topic_id]
            for tier_level, tier_name, price, weeks, is_rec, policy, features in tier_templates:
                tier_id = f"{topic_id}_{tier_level}"
                self.tiers[tier_id] = PackTier(
                    tier_id=tier_id,
                    topic_id=topic_id,
                    tier_level=tier_level,
                    name=f"{topic.label.split(' ')[0]} {tier_name}",
                    tagline=f"{tier_name} access to {topic.label.lower()} experts",
                    price_inr=price,
                    validity_weeks=weeks,
                    is_recommended=is_rec,
                    access_policy=policy,
                    features=features,
                    display_order=["starter", "plus", "pro"].index(tier_level) + 1,
                    catalog_version=CATALOG_VERSION
                )
        
        # =========================================================================
        # V5 TILE-BASED TIERS (Frontend tile IDs)
        # =========================================================================
        v5_tile_tiers = [
            # Relationship Clarity & Commitment
            ("relationship_healing", "love", "Relationship Healing", 6999, 8, 
             "Full astrology report about Love & Relationships",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "3×20 min follow-ups", "Unlimited chat", "30-Day Repair Plan", "Communication Script Pack"]),
            
            ("family_relationships", "marriage", "Family Relationships", 5999, 8,
             "Full astrology report about Family Relationships", 
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "4×30 min follow-ups", "Unlimited chat", "Family Harmony Toolkit", "Communication Guidelines"]),
            
            ("dating_compatibility", "love", "Dating & Compatibility", 4999, 8,
             "Full astrology report about Dating & Compatibility",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "3×20 min follow-ups", "Unlimited chat", "Compatibility Checklist", "Dating Timeline"]),
            
            ("marriage_planning", "marriage", "Marriage Planning", 7999, 12,
             "Full astrology report about Marriage & Partnership",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "5×20 min follow-ups", "Unlimited chat", "Kundli Matching Report", "Muhurat Calendar"]),
            
            # Career Direction & Stability
            ("career_clarity", "career", "Career Clarity", 4999, 8,
             "Full report about Career, Opportunities & Money",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "3×20 min follow-ups", "Unlimited chat", "Role Fit Map", "Skill Focus Plan"]),
            
            ("job_transition", "career", "Job Transition", 7999, 12,
             "Full report about Career, Opportunities & Money",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "5×15 min follow-ups", "Unlimited chat", "Timing Window", "Offer Decision Checklist"]),
            
            ("money_stability", "money", "Money Stability", 2999, 4,
             "Full report about Career, Opportunities & Money",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "2×15 min follow-ups", "Unlimited chat", "Wealth Timeline", "Savings Discipline Plan"]),
            
            # Business & Money
            ("business_decision", "business", "Business Decisions", 4999, 8,
             "Full report about Business, Growth & Money",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "3×20 min follow-ups", "Unlimited chat", "Business Muhurat Pack", "Decision Risk Scan"]),
            
            ("financial_growth", "business", "Financial Growth", 7999, 12,
             "Full report about Business, Growth & Money",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "5×15 min follow-ups", "Unlimited chat", "Wealth Leakage Scan", "Growth Window"]),
            
            ("timing_move", "business", "Timing Your Next Move", 2999, 4,
             "Full report about Business, Growth & Money",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "2×15 min follow-ups", "Unlimited chat", "Next 90/180 Day Timeline", "Action Calendar"]),
            
            # Family & Kids
            ("fertility", "children", "Fertility Support", 5999, 8,
             "Full Astrology report about Parenthood",
             ["1 Vedic Astrologer consultation", "3 Tarot Card Readings (5 Qs each)", "3×20 min follow-ups", "Unlimited Chat", "Conception Timing Pack", "Mira Q&A List"]),
            
            ("baby_naming", "children", "Baby Naming & Muhurat", 4999, 12,
             "Child's Kundli, name options and life report",
             ["1 Vedic Astrologer consultation", "3 Tarot Card Readings (5 Qs each)", "5×15 min follow-ups", "Unlimited Chat", "Baby Naming Pack", "Childbirth Muhurat Pack"]),
            
            ("child_development", "children", "Child Development", 4999, 8,
             "Child's Kundli and life report",
             ["1 Vedic Astrologer consultation", "3 Tarot Card Readings (5 Qs each)", "3×20 min follow-ups", "Unlimited Chat", "Kids Kundli Snapshot", "Learning Style Guide"]),
            
            # Health & Wellness
            ("healing_journey", "health", "Healing Journey", 4999, 8,
             "Full astrology report about Health",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "3×20 min follow-ups", "Unlimited chat", "Healing Window Timing", "14-Day Recovery Routine"]),
            
            ("stress_management", "mental_health", "Stress Management", 7999, 12,
             "Full astrology report about Health",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "5×15 min follow-ups", "Unlimited chat", "Stress Driver Diagnosis", "Sleep Reset Plan"]),
            
            ("energy_balance", "health", "Energy & Balance", 4999, 8,
             "Full astrology report about Health",
             ["1 Vedic astrologer consultation", "1 Tarot reading (5 Qs)", "3×20 min follow-ups", "Unlimited chat", "Energy Pattern Scan", "14-Day Vitality Plan"]),
        ]
        
        for tier_id, topic_id, name, price, weeks, tagline, features in v5_tile_tiers:
            self.tiers[tier_id] = PackTier(
                tier_id=tier_id,
                topic_id=topic_id,
                tier_level="v5_pack",
                name=name,
                tagline=tagline,
                price_inr=price,
                validity_weeks=weeks,
                is_recommended=True,
                access_policy=AccessPolicy(
                    chat_sla_hours=24,
                    calls_enabled=True,
                    calls_per_month=2,
                    call_duration_minutes=60,
                    max_active_expert_threads=3,
                    free_tools_access=True
                ),
                features=features,
                display_order=1,
                catalog_version=CATALOG_VERSION
            )
        
        # =========================================================================
        # V5 18 SUB-TOPIC TIERS (3 tiers per sub-topic: Focussed, Supported, Comprehensive)
        # =========================================================================
        v5_subtopic_tiers = [
            # ==================== LOVE SUB-TOPICS (6) ====================
            # Relationship Healing
            ("relationship-healing_focussed", "love", "Relationship Healing - Focussed", 6999, 8),
            ("relationship-healing_supported", "love", "Relationship Healing - Supported", 8999, 8),
            ("relationship-healing_comprehensive", "love", "Relationship Healing - Comprehensive", 10999, 8),
            
            # Family Relationships
            ("family-relationships_focussed", "marriage", "Family Relationships - Focussed", 5999, 8),
            ("family-relationships_supported", "marriage", "Family Relationships - Supported", 7999, 8),
            ("family-relationships_comprehensive", "marriage", "Family Relationships - Comprehensive", 9999, 8),
            
            # Dating & Compatibility
            ("dating-compatibility_focussed", "love", "Dating & Compatibility - Focussed", 4999, 8),
            ("dating-compatibility_supported", "love", "Dating & Compatibility - Supported", 6999, 8),
            ("dating-compatibility_comprehensive", "love", "Dating & Compatibility - Comprehensive", 8999, 8),
            
            # Marriage Planning
            ("marriage-planning_focussed", "marriage", "Marriage Planning - Focussed", 7999, 12),
            ("marriage-planning_supported", "marriage", "Marriage Planning - Supported", 9999, 12),
            ("marriage-planning_comprehensive", "marriage", "Marriage Planning - Comprehensive", 11999, 12),
            
            # Communication & Trust
            ("communication-trust_focussed", "love", "Communication & Trust - Focussed", 5999, 8),
            ("communication-trust_supported", "love", "Communication & Trust - Supported", 7999, 8),
            ("communication-trust_comprehensive", "love", "Communication & Trust - Comprehensive", 9999, 8),
            
            # Breakup & Closure
            ("breakup-closure_focussed", "love", "Breakup & Closure - Focussed", 4999, 8),
            ("breakup-closure_supported", "love", "Breakup & Closure - Supported", 6999, 8),
            ("breakup-closure_comprehensive", "love", "Breakup & Closure - Comprehensive", 8999, 8),
            
            # ==================== CAREER SUB-TOPICS (6) ====================
            # Career Clarity
            ("career-clarity_focussed", "career", "Career Clarity - Focussed", 4999, 8),
            ("career-clarity_supported", "career", "Career Clarity - Supported", 6999, 8),
            ("career-clarity_comprehensive", "career", "Career Clarity - Comprehensive", 8999, 8),
            
            # Job Transition
            ("job-transition_focussed", "career", "Job Transition - Focussed", 7999, 12),
            ("job-transition_supported", "career", "Job Transition - Supported", 9999, 12),
            ("job-transition_comprehensive", "career", "Job Transition - Comprehensive", 11999, 12),
            
            # Money Stability
            ("money-stability_focussed", "money", "Money Stability - Focussed", 2999, 4),
            ("money-stability_supported", "money", "Money Stability - Supported", 4999, 4),
            ("money-stability_comprehensive", "money", "Money Stability - Comprehensive", 6999, 4),
            
            # Work Stress
            ("work-stress_focussed", "career", "Work Stress - Focussed", 4999, 8),
            ("work-stress_supported", "career", "Work Stress - Supported", 6999, 8),
            ("work-stress_comprehensive", "career", "Work Stress - Comprehensive", 8999, 8),
            
            # Office Politics
            ("office-politics_focussed", "career", "Office Politics - Focussed", 4999, 8),
            ("office-politics_supported", "career", "Office Politics - Supported", 6999, 8),
            ("office-politics_comprehensive", "career", "Office Politics - Comprehensive", 8999, 8),
            
            # Big Decision Timing
            ("big-decision-timing_focussed", "career", "Big Decision Timing - Focussed", 2999, 4),
            ("big-decision-timing_supported", "career", "Big Decision Timing - Supported", 4999, 4),
            ("big-decision-timing_comprehensive", "career", "Big Decision Timing - Comprehensive", 6999, 4),
            
            # ==================== HEALTH SUB-TOPICS (6) ====================
            # Healing Journey
            ("healing-journey_focussed", "health", "Healing Journey - Focussed", 4999, 8),
            ("healing-journey_supported", "health", "Healing Journey - Supported", 6999, 8),
            ("healing-journey_comprehensive", "health", "Healing Journey - Comprehensive", 8999, 8),
            
            # Stress Management
            ("stress-management_focussed", "mental_health", "Stress Management - Focussed", 7999, 12),
            ("stress-management_supported", "mental_health", "Stress Management - Supported", 9999, 12),
            ("stress-management_comprehensive", "mental_health", "Stress Management - Comprehensive", 11999, 12),
            
            # Energy & Balance
            ("energy-balance_focussed", "health", "Energy & Balance - Focussed", 4999, 8),
            ("energy-balance_supported", "health", "Energy & Balance - Supported", 6999, 8),
            ("energy-balance_comprehensive", "health", "Energy & Balance - Comprehensive", 8999, 8),
            
            # Sleep Reset
            ("sleep-reset_focussed", "health", "Sleep Reset - Focussed", 4999, 8),
            ("sleep-reset_supported", "health", "Sleep Reset - Supported", 6999, 8),
            ("sleep-reset_comprehensive", "health", "Sleep Reset - Comprehensive", 8999, 8),
            
            # Emotional Recovery
            ("emotional-recovery_focussed", "mental_health", "Emotional Recovery - Focussed", 4999, 8),
            ("emotional-recovery_supported", "mental_health", "Emotional Recovery - Supported", 6999, 8),
            ("emotional-recovery_comprehensive", "mental_health", "Emotional Recovery - Comprehensive", 8999, 8),
            
            # Women's Wellness
            ("womens-wellness_focussed", "health", "Women's Wellness - Focussed", 4999, 8),
            ("womens-wellness_supported", "health", "Women's Wellness - Supported", 6999, 8),
            ("womens-wellness_comprehensive", "health", "Women's Wellness - Comprehensive", 8999, 8),
        ]
        
        # Define access policies for each tier level
        tier_policies = {
            "focussed": AccessPolicy(
                chat_sla_hours=48,
                calls_enabled=True,
                calls_per_month=1,
                call_duration_minutes=60,
                max_active_expert_threads=1,
                free_tools_access=True
            ),
            "supported": AccessPolicy(
                chat_sla_hours=24,
                calls_enabled=True,
                calls_per_month=3,
                call_duration_minutes=60,
                max_active_expert_threads=2,
                free_tools_access=True
            ),
            "comprehensive": AccessPolicy(
                chat_sla_hours=24,
                calls_enabled=True,
                calls_per_month=5,
                call_duration_minutes=60,
                max_active_expert_threads=-1,
                free_tools_access=True
            )
        }
        
        tier_features = {
            "focussed": [
                "1× 60-min video call",
                "7 days async chat",
                "1 follow-up check-in",
                "Basic clarity report"
            ],
            "supported": [
                "3 sessions (1×60-min + 2×30-min)",
                "Unlimited chat for full duration",
                "2 follow-ups included",
                "Extended guidance report"
            ],
            "comprehensive": [
                "5 sessions (2×60-min + 3×30-min)",
                "Unlimited chat + priority response",
                "Multiple expert perspectives",
                "Comprehensive life report"
            ]
        }
        
        for tier_id, topic_id, name, price, weeks in v5_subtopic_tiers:
            # Determine tier level from ID
            if "_focussed" in tier_id:
                tier_level = "focussed"
                display_order = 1
                is_recommended = False
            elif "_supported" in tier_id:
                tier_level = "supported"
                display_order = 2
                is_recommended = True  # Supported tier is always recommended
            else:
                tier_level = "comprehensive"
                display_order = 3
                is_recommended = False
            
            self.tiers[tier_id] = PackTier(
                tier_id=tier_id,
                topic_id=topic_id,
                tier_level=tier_level,
                name=name,
                tagline=f"{tier_level.capitalize()} guidance package",
                price_inr=price,
                validity_weeks=weeks,
                is_recommended=is_recommended,
                access_policy=tier_policies[tier_level],
                features=tier_features[tier_level],
                display_order=display_order,
                catalog_version=CATALOG_VERSION
            )
    
    # =========================================================================
    # SEED FREE TOOLS
    # =========================================================================
    
    def _seed_tools(self):
        """Seed free tools for all topics (Plus/Pro only)"""
        
        tools_data = {
            "career": [
                ("tool_c01", "Career Decision Framework", "framework", "Structured approach to evaluate career options"),
                ("tool_c02", "Timing Explainer", "explainer", "Understand auspicious timing for career moves"),
                ("tool_c03", "Career Values Quiz", "quiz", "Discover what matters most in your career"),
            ],
            "money": [
                ("tool_m01", "Spending Audit Prompts", "prompts", "Questions to review your spending patterns"),
                ("tool_m02", "Risk Tolerance Quiz", "quiz", "Understand your investment risk profile"),
                ("tool_m03", "Financial Goals Worksheet", "worksheet", "Plan your financial milestones"),
            ],
            "love": [
                ("tool_l01", "Relationship Clarity Questions", "prompts", "Deep questions for relationship insight"),
                ("tool_l02", "Conflict Resolution Checklist", "checklist", "Steps to resolve relationship conflicts"),
                ("tool_l03", "Compatibility Prompts", "prompts", "Explore compatibility dimensions"),
            ],
            "health": [
                ("tool_h01", "Lifestyle Audit", "checklist", "Review your daily health habits"),
                ("tool_h02", "Stress Check Prompts", "prompts", "Identify your stress triggers"),
                ("tool_h03", "Wellness Goals Worksheet", "worksheet", "Plan your health journey"),
            ],
            "marriage": [
                ("tool_mr01", "Communication Checklist", "checklist", "Improve your couple communication"),
                ("tool_mr02", "Alignment Prompts", "prompts", "Discuss important life topics together"),
            ],
            "children": [
                ("tool_ch01", "Education Fit Quiz", "quiz", "Find the right education path"),
                ("tool_ch02", "Parenting Style Prompts", "prompts", "Reflect on your parenting approach"),
            ],
            "business": [
                ("tool_b01", "Business Timing Guide", "explainer", "Auspicious times for business decisions"),
                ("tool_b02", "Partnership Checklist", "checklist", "Evaluate business partnerships"),
            ],
            "travel": [
                ("tool_t01", "Relocation Checklist", "checklist", "Complete guide to planning a move"),
                ("tool_t02", "Travel Timing Guide", "explainer", "Best times for travel and moves"),
            ],
            "property": [
                ("tool_p01", "Property Decision Framework", "framework", "Evaluate property options"),
                ("tool_p02", "Vastu Quick Check", "checklist", "Basic Vastu assessment"),
            ],
            "mental_health": [
                ("tool_mh01", "Stress Management Prompts", "prompts", "Daily prompts for mental wellness"),
                ("tool_mh02", "Self-Care Checklist", "checklist", "Essential self-care practices"),
            ],
            "spiritual": [
                ("tool_sp01", "Purpose Discovery Prompts", "prompts", "Questions to find your purpose"),
                ("tool_sp02", "Meditation Guide", "explainer", "Getting started with meditation"),
            ],
            "legal": [
                ("tool_lg01", "Document Checklist", "checklist", "Essential legal documents"),
                ("tool_lg02", "Dispute Resolution Guide", "explainer", "Steps to resolve conflicts"),
            ],
            "meditation": [
                ("tool_med01", "Beginner Meditation Guide", "explainer", "Start your meditation journey"),
                ("tool_med02", "Daily Practice Checklist", "checklist", "Build a consistent practice"),
                ("tool_med03", "Breathing Exercises", "framework", "Essential pranayama techniques"),
            ],
            "counseling": [
                ("tool_coun01", "Life Goals Worksheet", "worksheet", "Clarify your life direction"),
                ("tool_coun02", "Self-Reflection Prompts", "prompts", "Deep questions for growth"),
                ("tool_coun03", "Emotional Check-in Guide", "framework", "Track your emotional wellbeing"),
            ],
        }
        
        for topic_id, tools in tools_data.items():
            for idx, (tool_id, title, tool_type, desc) in enumerate(tools):
                self.tools[tool_id] = TopicFreeTool(
                    tool_id=tool_id,
                    topic_id=topic_id,
                    title=title,
                    short_desc=desc,
                    tool_type=tool_type,
                    access="plus_pro_only",
                    display_order=idx + 1
                )
    
    # =========================================================================
    # QUERY METHODS
    # =========================================================================
    
    def get_all_topics(self) -> List[Topic]:
        """Get all active topics"""
        return sorted(
            [t for t in self.topics.values() if t.is_active],
            key=lambda x: x.display_order
        )
    
    def get_topic(self, topic_id: str) -> Optional[Topic]:
        """Get topic by ID"""
        return self.topics.get(topic_id)
    
    def get_experts_for_topic(self, topic_id: str) -> List[ExpertProfile]:
        """Get all experts for a topic"""
        return sorted(
            [e for e in self.experts.values() if topic_id in e.topics and e.is_active],
            key=lambda x: x.display_order
        )
    
    def get_expert(self, expert_id: str) -> Optional[ExpertProfile]:
        """Get expert by ID"""
        return self.experts.get(expert_id)
    
    def get_scenarios_for_topic(self, topic_id: str) -> List[ScenarioChip]:
        """Get all scenarios for a topic"""
        return sorted(
            [s for s in self.scenarios.values() if s.topic_id == topic_id and s.is_active],
            key=lambda x: x.display_order
        )
    
    def get_tiers_for_topic(self, topic_id: str) -> List[PackTier]:
        """Get all tiers for a topic"""
        return sorted(
            [t for t in self.tiers.values() if t.topic_id == topic_id and t.is_active],
            key=lambda x: x.display_order
        )
    
    def get_tier(self, tier_id: str) -> Optional[PackTier]:
        """Get tier by ID"""
        return self.tiers.get(tier_id)
    
    def get_tools_for_topic(self, topic_id: str) -> List[TopicFreeTool]:
        """Get all tools for a topic"""
        return sorted(
            [t for t in self.tools.values() if t.topic_id == topic_id and t.is_active],
            key=lambda x: x.display_order
        )
    
    def get_tool(self, tool_id: str) -> Optional[TopicFreeTool]:
        """Get tool by ID"""
        return self.tools.get(tool_id)
    
    def get_recommended_tier(self, topic_id: str, scenario_ids: List[str] = None) -> str:
        """Get recommended tier based on selected scenarios"""
        if not scenario_ids:
            return "plus"  # Default recommendation
        
        # Check if any high-urgency scenario selected
        tier_scores = {"starter": 0, "plus": 0, "pro": 0}
        for sc_id in scenario_ids:
            scenario = self.scenarios.get(sc_id)
            if scenario:
                tier_scores[scenario.recommended_tier] += 1
        
        # Return tier with highest score, defaulting to plus
        if tier_scores["pro"] > 0:
            return "pro"
        elif tier_scores["plus"] > 0 or tier_scores["starter"] == 0:
            return "plus"
        return "starter"
    
    def get_unlimited_conditions(self) -> UnlimitedAccessConditions:
        """Get unlimited access conditions for display"""
        return self.unlimited_conditions


# Singleton instance
_catalog: Optional[SimplifiedCatalog] = None


def get_simplified_catalog() -> SimplifiedCatalog:
    """Get or create catalog singleton"""
    global _catalog
    if _catalog is None:
        _catalog = SimplifiedCatalog()
    return _catalog
