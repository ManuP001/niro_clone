"""NIRO V2 - Solution-led platform for life guidance

Controlled chat-as-recommender with catalog-based offerings.
Features:
- Package & Remedy Catalog
- Rules-based Recommendation Engine
- Razorpay Payment Integration
- MongoDB Persistence
- Telemetry & Analytics
"""

from .models import (
    Package,
    Remedy,
    ConsultPolicy,
    SelfGuidedItem,
    AdditionalService,
    ChatHandoffPayload,
    ChatRecommendationResponse,
    ValidatedRecommendation,
    ValidationError,
    UserPlan,
    UserPlanTask,
    UserRemedyAddon,
    SituationIntake,
)

from .catalog import (
    CatalogService,
    get_catalog_service,
)

from .recommendation_engine import (
    RecommendationEngine,
    get_recommendation_engine,
)

from .telemetry import (
    TelemetryService,
    get_telemetry_service,
)

from .payment_service import (
    PaymentService,
    get_payment_service,
)

from .storage import (
    NiroV2Storage,
    get_niro_v2_storage,
    init_niro_v2_storage,
)

__all__ = [
    # Models
    'Package',
    'Remedy', 
    'ConsultPolicy',
    'SelfGuidedItem',
    'AdditionalService',
    'ChatHandoffPayload',
    'ChatRecommendationResponse',
    'ValidatedRecommendation',
    'ValidationError',
    'UserPlan',
    'UserPlanTask',
    'UserRemedyAddon',
    'SituationIntake',
    # Services
    'CatalogService',
    'get_catalog_service',
    'RecommendationEngine',
    'get_recommendation_engine',
    'TelemetryService',
    'get_telemetry_service',
    'PaymentService',
    'get_payment_service',
    'NiroV2Storage',
    'get_niro_v2_storage',
    'init_niro_v2_storage',
]
