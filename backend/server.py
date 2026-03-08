import sys
from pathlib import Path
# Add parent directory to path to support relative imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# IMPORTANT: Load environment variables FIRST before any imports that need them
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Fix for Python 3.9 importlib.metadata compatibility
try:
    from importlib.metadata import packages_distributions
except (ImportError, AttributeError):
    try:
        from importlib_metadata import packages_distributions
    except ImportError:
        def packages_distributions():
            return {}

from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Header, Query, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import time
from typing import List, Optional
from datetime import datetime, timezone

# Import our custom modules
from backend.models import (
    User, UserCreate,
    Transaction, TransactionCreate, MockPaymentVerify,
    Report, ReportRequest, ReportResponse, ReportStatus,
    FollowUpQuestion, FollowUpResponse,
    PriceConfig, PriceUpdate, ReportType, PaymentStatus
)
from backend.gemini_agent import GeminiAgent
from backend.sandbox_executor import get_sandbox_executor
from backend.pdf_generator import AstroPrescriptionPDF
from backend.prompt_templates import build_code_generation_prompt
from backend.vedic_api_client import VedicAstroClient
from backend.gemini_astro_calculator import GeminiAstroCalculator
from backend.advanced_prompts import build_user_context
from backend.visual_data_extractor import VisualDataExtractor
from backend.time_parser import TimeParser
from backend.city_service import CityService, IndianCityService
from backend.chat_agent import AstroChatAgent
from backend.chat_models import ChatRequest, ChatResponse, ChatMessage, ChatSession, ChatRole
from backend.niro_models import NiroChatRequest, NiroChatResponse
from backend.niro_agent import NiroChatAgent

# Import the conversation orchestrator (both legacy and enhanced)
from backend.conversation import (
    ConversationOrchestrator,
    EnhancedOrchestrator,
    create_enhanced_orchestrator,
    ChatRequest as OrchestratorChatRequest,
    ChatResponse as OrchestratorChatResponse,
    BirthDetails as OrchestratorBirthDetails,
    InMemorySessionStore
)

# Import auth service
from backend.auth.auth_service import get_auth_service

# Import astro_client components for direct access
from backend.astro_client import (
    Topic,
    classify_topic,
    get_astro_profile
)

# Import auth and profile routers
from backend.auth.routes import router as auth_router
from backend.profile import router as profile_router
from backend.routes.google_oauth_direct import router as google_auth_router

# Import new astro refactoring routers
from backend.routes.astro_routes import router as astro_router
from backend.routes.debug_routes import router as debug_router
from backend.services.astro_database import get_astro_db

# Import NIRO V2 routes and storage
from backend.niro_v2.routes import router as niro_v2_router
from backend.niro_v2.storage import init_niro_v2_storage, get_niro_v2_storage

# Import NIRO Simplified routes and storage
from backend.niro_simplified.routes import router as simplified_router
from backend.niro_simplified.storage import init_simplified_storage, get_simplified_storage

# Import Admin and Remedies routes
from backend.routes.admin import router as admin_router
from backend.routes.remedies import router as remedies_router
from backend.routes.bookings import router as bookings_router
from backend.routes.whatsapp_otp import router as whatsapp_otp_router

# Ensure workspace-local logs directory exists for runtime logs
(ROOT_DIR / "logs").mkdir(parents=True, exist_ok=True)

# MongoDB connection
mongo_url = os.getenv('MONGO_URL')
if not mongo_url:
    print("WARNING: MONGO_URL not set; MongoDB features disabled")
    client = None
    db = None
else:
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'niro')]

# Configuration for calculation source (must be set before initialization)
ASTRO_CALC_SOURCE = os.environ.get('ASTRO_CALCULATION_SOURCE', 'vedic_api')

# Configure logging (early, before initializing other components)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize core components
try:
    gemini_agent = GeminiAgent()
    logger.info("✓ Gemini Agent initialized")
except ValueError:
    logger.warning("⚠ Gemini API key not found - running in stub mode")
    gemini_agent = None
sandbox_executor = get_sandbox_executor(use_docker=True)  # Use Docker for production
pdf_generator = AstroPrescriptionPDF(output_dir=str(ROOT_DIR / "reports"))
vedic_client = VedicAstroClient()  # VedicAstroAPI client (accurate)
try:
    gemini_calculator = GeminiAstroCalculator()  # Gemini LLM calculator (experimental)
except ValueError:
    logger.warning("⚠ GeminiAstroCalculator not available - stub mode")
    gemini_calculator = None
visual_extractor = VisualDataExtractor()  # Visual data extraction for charts
time_parser = TimeParser()  # Smart time parsing
city_service = CityService()  # City autocomplete with GeoNames
indian_city_service = IndianCityService()  # Comprehensive Indian cities database
try:
    chat_agent = AstroChatAgent()  # Chat-based astrology agent
    logger.info("✓ AstroChatAgent initialized")
except (ValueError, ImportError, Exception) as e:
    logger.warning(f"⚠ AstroChatAgent failed to initialize: {e} - running in degraded mode")
    chat_agent = None
try:
    niro_agent = NiroChatAgent()  # NIRO chat agent (initialized after dotenv)
    logger.info("✓ NiroChatAgent initialized")
except (ValueError, ImportError, Exception) as e:
    logger.warning(f"⚠ NiroChatAgent failed to initialize: {e} - running in degraded mode")
    niro_agent = None

# Initialize the conversation orchestrators
try:
    conversation_orchestrator = ConversationOrchestrator()  # Legacy orchestrator
    logger.info("✓ ConversationOrchestrator initialized")
except Exception as e:
    logger.warning(f"⚠ ConversationOrchestrator failed to initialize: {e}")
    conversation_orchestrator = None

try:
    enhanced_orchestrator = create_enhanced_orchestrator()  # New enhanced orchestrator
    logger.info("✓ EnhancedOrchestrator initialized")
except Exception as e:
    logger.warning(f"⚠ EnhancedOrchestrator failed to initialize: {e}")
    enhanced_orchestrator = None

# Create the main app without a prefix
app = FastAPI(title="Astro-Trust Engine API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============= HEALTH CHECK =============

@api_router.get("/")
async def root():
    return {
        "message": "Astro-Trust Engine API",
        "version": "1.0.0",
        "status": "operational",
        "astro_calculation_source": ASTRO_CALC_SOURCE
    }

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "gemini_configured": bool(os.environ.get('GEMINI_API_KEY')),
        "vedic_api_configured": bool(os.environ.get('VEDIC_API_KEY')),
        "astro_calculation_source": ASTRO_CALC_SOURCE,
        "database": "connected"
    }

# ============= UTILITY ENDPOINTS =============

@api_router.get("/utils/check-gemini-quota")
async def check_gemini_quota():
    """
    Test Gemini API quota by making a small request
    Returns quota status and any errors
    """
    try:
        test_prompt = "Reply with: OK"
        response = gemini_agent._call_model(
            gemini_agent.flash_model,  # Use flash for quota check (cheaper)
            test_prompt,
            temperature=0.1
        )
        
        return {
            "status": "available",
            "message": "Gemini API is working",
            "model_tested": "gemini-2.5-flash",
            "response": response[:100]
        }
    except Exception as e:
        error_msg = str(e)
        
        if "ResourceExhausted" in error_msg or "quota" in error_msg.lower():
            return {
                "status": "quota_exceeded",
                "message": "Gemini API quota exceeded",
                "error": error_msg,
                "solution": "Upgrade your Gemini API key at https://aistudio.google.com/app/apikey or wait for quota reset"
            }
        else:
            return {
                "status": "error",
                "message": "Gemini API error",
                "error": error_msg
            }

@api_router.post("/utils/parse-time")
async def parse_time_endpoint(request: dict):
    """
    Parse and validate flexible time input
    
    Body: {"time_input": "2:35 PM"}
    Returns: {"success": true, "normalized_time": "14:35", "display_time": "2:35 PM"}
    """
    time_input = request.get('time_input', '')
    success, normalized_time, error_message = time_parser.parse_time(time_input)
    
    if success:
        display_time = time_parser.convert_to_display_format(normalized_time)
        return {
            "success": True,
            "normalized_time": normalized_time,
            "display_time": display_time,
            "error_message": None
        }
    else:
        return {
            "success": False,
            "normalized_time": None,
            "display_time": None,
            "error_message": error_message
        }

@api_router.post("/utils/compare-calculations")
async def compare_calculations(request: dict):
    """
    Compare VedicAPI vs Gemini LLM calculations
    For testing and quality assessment
    
    Body: {
        "dob": "15-08-1990",
        "tob": "14:30",
        "lat": 28.6139,
        "lon": 77.2090,
        "location": "Delhi, India"
    }
    """
    try:
        dob = request.get('dob')
        tob = request.get('tob')
        lat = request.get('lat')
        lon = request.get('lon')
        location = request.get('location', 'Unknown')
        timezone = request.get('timezone', 5.5)
        
        # Method 1: VedicAstroAPI
        logger.info("Fetching from VedicAstroAPI...")
        vedic_response = vedic_client.get_planet_details(dob, tob, lat, lon, timezone)
        
        # Method 2: Gemini LLM
        logger.info("Calculating with Gemini LLM...")
        gemini_success, gemini_data, gemini_error = gemini_calculator.calculate_houses_and_planets(
            dob, tob, lat, lon, location, timezone
        )
        
        return {
            "vedic_api": {
                "success": vedic_response.get('success'),
                "data": vedic_response.get('data', {}),
                "error": vedic_response.get('error'),
                "source": "VedicAstroAPI (Astronomical Calculations)"
            },
            "gemini_llm": {
                "success": gemini_success,
                "data": gemini_data if gemini_success else {},
                "error": gemini_error,
                "source": "Gemini LLM (AI-Generated, Experimental)"
            },
            "comparison_notes": "VedicAPI uses Swiss Ephemeris for accurate astronomical calculations. Gemini LLM generates estimates and may not be astronomically accurate."
        }
        
    except Exception as e:
        logger.error(f"Comparison failed: {str(e)}")
        return {"error": str(e)}

@api_router.get("/utils/search-cities")
async def search_cities_endpoint(query: str, max_results: int = 10):
    """
    Search cities with autocomplete - uses Vedic API geo-search for comprehensive coverage.
    
    Query params:
    - query: Search query (min 2 characters)
    - max_results: Max results to return (default 10)
    
    Returns: List of cities with lat, lon, timezone
    
    Data sources (in order):
    1. Vedic API /utilities/geo-search (comprehensive worldwide coverage)
    2. Local Indian cities database (fast fallback)
    3. GeoNames API (international fallback)
    """
    if len(query) < 2:
        return {"cities": []}
    
    try:
        # PRIMARY: Use Vedic API geo-search for comprehensive coverage
        vedic_api_key = os.environ.get('VEDIC_API_KEY')
        if vedic_api_key:
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    'api_key': vedic_api_key,
                    'city': query,
                    'max_rows': max_results * 2  # Get more to filter
                }
                
                resp = await client.get(
                    'https://api.vedicastroapi.com/v3-json/utilities/geo-search',
                    params=params
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get('status') == 200:
                        results = data.get('response', [])
                        
                        # Transform Vedic API response to our format
                        cities = []
                        for r in results[:max_results]:
                            coords = r.get('coordinates', [])
                            lat = float(coords[0]) if coords and len(coords) > 0 else None
                            lon = float(coords[1]) if coords and len(coords) > 1 else None
                            
                            if lat and lon:  # Only include results with valid coordinates
                                cities.append({
                                    'id': f"vedic_{r.get('name', '').lower().replace(' ', '_')}",
                                    'name': r.get('name', ''),
                                    'country': r.get('country_name', ''),
                                    'country_code': r.get('country', ''),
                                    'state': r.get('full_name', '').split(', ')[1] if ', ' in r.get('full_name', '') else '',
                                    'lat': lat,
                                    'lon': lon,
                                    'timezone': r.get('tzone', ['UTC'])[0] if r.get('tzone') else 'UTC',
                                    'tz_offset': r.get('tz', 0),
                                    'display_name': r.get('full_name', r.get('name', ''))
                                })
                        
                        if cities:
                            logger.info(f"Vedic API geo-search found {len(cities)} cities for: {query}")
                            return {"cities": cities}
        
        # FALLBACK 1: Use Indian city database (fast, reliable for major cities)
        cities = indian_city_service.search_cities(query, max_results)
        
        if cities:
            logger.info(f"Local Indian DB found {len(cities)} cities for: {query}")
            return {"cities": cities}
        
        # FALLBACK 2: Try GeoNames for international cities
        logger.info("No results in local database, trying GeoNames")
        cities = city_service.search_cities(query, max_results)
        
        return {"cities": cities}
        
    except Exception as e:
        logger.error(f"City search error: {str(e)}")
        # Use Indian database as fallback on any error
        cities = indian_city_service.search_cities(query, max_results)
        return {"cities": cities}

# ============= PLACES AUTOCOMPLETE =============

@api_router.get("/places/search")
async def search_places(q: str):
    """
    Search for places of birth with autocomplete.
    
    Query params:
    - q: Search query (city name, state, country)
    
    Returns: List of matching places with normalized response format
    [
      {"label":"Rohtak, Haryana, India","place_id":"...","lat":28.9,"lon":76.6,"tz":"Asia/Kolkata"}
    ]
    """
    if not q or len(q) < 2:
        return {"places": []}
    
    try:
        from backend.places_data import search_places as search_places_db
        results = search_places_db(q, limit=10)
        return {"places": results}
    except Exception as e:
        logger.error(f"Places search error: {str(e)}")
        return {"places": [], "error": str(e)}

# ============= USER MANAGEMENT =============

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user with birth details"""
    user = User(**user_data.model_dump())
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['birth_details'] = doc['birth_details']  # Keep as dict
    
    await db.users.insert_one(doc)
    logger.info(f"Created user: {user.user_id}")
    return user

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user details"""
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return user_doc

# ============= PRICING MANAGEMENT =============

@api_router.get("/pricing", response_model=List[PriceConfig])
async def get_pricing():
    """Get current pricing for all report types"""
    prices = await db.pricing.find({"is_active": True}, {"_id": 0}).to_list(100)
    
    # If no prices exist, create defaults
    if not prices:
        default_prices = [
            {"report_type": "yearly_prediction", "current_price_inr": 499.0},
            {"report_type": "love_marriage", "current_price_inr": 599.0},
            {"report_type": "career_job", "current_price_inr": 549.0},
            {"report_type": "retro_check", "current_price_inr": 399.0}  # NEW: Past verification
        ]
        
        for price_data in default_prices:
            price = PriceConfig(**price_data)
            doc = price.model_dump()
            doc['updated_at'] = doc['updated_at'].isoformat()
            await db.pricing.insert_one(doc)
            prices.append(price.model_dump())
    
    return prices

@api_router.post("/pricing/update")
async def update_pricing(price_update: PriceUpdate):
    """Update pricing for a report type (Admin function)"""
    price = PriceConfig(
        report_type=price_update.report_type,
        current_price_inr=price_update.new_price_inr
    )
    
    doc = price.model_dump()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    # Update existing or insert new
    await db.pricing.update_one(
        {"report_type": price_update.report_type},
        {"$set": doc},
        upsert=True
    )
    
    logger.info(f"Updated pricing for {price_update.report_type}: ₹{price_update.new_price_inr}")
    return {"success": True, "message": "Pricing updated"}

# ============= PAYMENT/TRANSACTION =============

@api_router.post("/transactions/create", response_model=Transaction)
async def create_transaction(trans_data: TransactionCreate):
    """Create a payment transaction"""
    # Get current price
    price_doc = await db.pricing.find_one({"report_type": trans_data.report_type}, {"_id": 0})
    if not price_doc:
        raise HTTPException(status_code=404, detail="Price not found for this report type")
    
    transaction = Transaction(
        user_id=trans_data.user_id,
        report_type=trans_data.report_type,
        amount=price_doc['current_price_inr']
    )
    
    doc = transaction.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.transactions.insert_one(doc)
    logger.info(f"Created transaction: {transaction.transaction_id}")
    return transaction

@api_router.post("/transactions/verify")
async def verify_payment(payment_verify: MockPaymentVerify):
    """Mock payment verification (for MVP)"""
    transaction_doc = await db.transactions.find_one(
        {"transaction_id": payment_verify.transaction_id},
        {"_id": 0}
    )
    
    if not transaction_doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Mock verification - always succeed for MVP
    if payment_verify.payment_success:
        await db.transactions.update_one(
            {"transaction_id": payment_verify.transaction_id},
            {"$set": {"payment_status": "completed", "completed_at": time.time()}}
        )
        logger.info(f"Payment verified for transaction: {payment_verify.transaction_id}")
        return {"success": True, "message": "Payment verified"}
    else:
        await db.transactions.update_one(
            {"transaction_id": payment_verify.transaction_id},
            {"$set": {"payment_status": "failed"}}
        )
        return {"success": False, "message": "Payment failed"}

# ============= CORE REPORT GENERATION =============

async def generate_report_background(report: Report, request: ReportRequest):
    """Background task for report generation"""
    start_time = time.time()
    
    try:
        # Step 1: Update status to PROCESSING
        await db.reports.update_one(
            {"report_id": report.report_id},
            {"$set": {"status": "processing"}}
        )
        
        logger.info(f"Starting report generation for {report.report_id}")
        
        # Step 2: Fetch astrological data (VedicAPI or Gemini LLM based on config)
        bd = request.birth_details
        
        if ASTRO_CALC_SOURCE == 'gemini_llm':
            logger.info("Using Gemini LLM for astrological calculations (EXPERIMENTAL)")
            success, raw_json, error_msg = gemini_calculator.calculate_houses_and_planets(
                dob=bd.dob,
                tob=bd.tob,
                lat=bd.lat,
                lon=bd.lon,
                location=bd.location,
                timezone=bd.timezone
            )
            
            if not success:
                logger.error(f"Gemini calculation failed: {error_msg}")
                await db.reports.update_one(
                    {"report_id": report.report_id},
                    {"$set": {
                        "status": "failed",
                        "code_execution_success": False,
                        "code_execution_error": f"Gemini LLM calculation failed: {error_msg}"
                    }}
                )
                return
            
            # Format for interpretation
            raw_json = gemini_calculator.format_for_interpretation(raw_json)
            
        else:
            # Default: Use VedicAstroAPI (accurate, reliable)
            logger.info("Fetching data from VedicAstroAPI (accurate astronomical calculations)")
            raw_response = vedic_client.get_planet_details(
                dob=bd.dob,
                tob=bd.tob,
                lat=bd.lat,
                lon=bd.lon,
                tz=bd.timezone
            )
            
            if not raw_response.get('success'):
                error_msg = raw_response.get('error', 'Unknown API error')
                logger.error(f"VedicAstroAPI failed: {error_msg}")
                await db.reports.update_one(
                    {"report_id": report.report_id},
                    {"$set": {
                        "status": "failed",
                        "code_execution_success": False,
                        "code_execution_error": error_msg
                    }}
                )
                return
            
            raw_json = raw_response.get('data', {})
        
        # Save raw JSON
        await db.reports.update_one(
            {"report_id": report.report_id},
            {"$set": {
                "raw_json": raw_json,
                "code_execution_success": True,
                "generated_code": "Direct API call (MVP mode)"
            }}
        )
        
        # Step 5: Build user context for gender-neutral interpretation
        user_doc = await db.users.find_one({"user_id": request.user_id}, {"_id": 0})
        user_context = build_user_context({
            'name': user_doc.get('name', 'User') if user_doc else 'User',
            'gender': user_doc.get('gender', 'prefer_not_to_say') if user_doc else 'prefer_not_to_say',
            'occupation': user_doc.get('occupation') if user_doc else None,
            'relationship_status': user_doc.get('relationship_status') if user_doc else None
        })
        
        # Step 6: Interpret results with Gemini (with advanced prompts)
        # Note: Using appropriate model based on quota availability
        logger.info("Interpreting report with Gemini AI (advanced prompts)...")
        try:
            interpreted_text = gemini_agent.interpret_report(
                raw_json=raw_json,
                report_type=request.report_type,
                user_context=user_context
            )
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini interpretation failed: {error_msg}")
            
            # Check if it's a quota error
            if "ResourceExhausted" in error_msg or "quota" in error_msg.lower():
                await db.reports.update_one(
                    {"report_id": report.report_id},
                    {"$set": {
                        "status": "failed",
                        "code_execution_error": "Gemini API quota exceeded. Please upgrade your Gemini API key or wait for quota reset. Visit: https://aistudio.google.com/app/apikey"
                    }}
                )
            else:
                await db.reports.update_one(
                    {"report_id": report.report_id},
                    {"$set": {
                        "status": "failed",
                        "code_execution_error": f"Report interpretation failed: {error_msg}"
                    }}
                )
            return
        
        # Step 7: Extract visual data for charts
        logger.info("Extracting visual data...")
        visual_data = visual_extractor.extract_visual_data(
            raw_json=raw_json,
            interpreted_text=interpreted_text,
            report_type=request.report_type
        )
        
        # Save interpretation and visual data
        await db.reports.update_one(
            {"report_id": report.report_id},
            {"$set": {
                "interpreted_text": interpreted_text,
                "visual_data": visual_data.model_dump()
            }}
        )
        
        # Step 8: Generate PDF
        logger.info("Generating PDF...")
        
        pdf_data = {
            'report_id': report.report_id,
            'report_type': request.report_type,
            'user_name': user_doc.get('name', 'User') if user_doc else 'User',
            'birth_details': request.birth_details.model_dump(),
            'interpreted_text': interpreted_text,
            'raw_json': raw_json
        }
        
        pdf_path = pdf_generator.generate_pdf(pdf_data)
        pdf_url = pdf_generator.get_pdf_url(pdf_path)
        
        # Step 9: Mark as completed
        processing_time = time.time() - start_time
        
        await db.reports.update_one(
            {"report_id": report.report_id},
            {"$set": {
                "status": "completed",
                "pdf_url": pdf_url,
                "completed_at": time.time(),
                "processing_time_seconds": processing_time
            }}
        )
        
        logger.info(f"Report generation completed in {processing_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}", exc_info=True)
        await db.reports.update_one(
            {"report_id": report.report_id},
            {"$set": {
                "status": "failed",
                "code_execution_error": str(e)
            }}
        )

@api_router.post("/reports/generate", response_model=ReportResponse)
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """
    Main endpoint for generating astrological reports
    Flow:
    1. Verify payment (transaction must be completed)
    2. Create report record
    3. Generate code with Gemini Pro (background)
    4. Execute code in sandbox (background)
    5. Interpret with Gemini Pro (background)
    6. Generate PDF (background)
    """
    
    # Verify payment
    transaction_doc = await db.transactions.find_one(
        {"transaction_id": request.transaction_id},
        {"_id": 0}
    )
    
    if not transaction_doc:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction_doc['payment_status'] != 'completed':
        raise HTTPException(status_code=400, detail="Payment not completed")
    
    # Check if report already exists for this transaction
    existing_report = await db.reports.find_one(
        {"transaction_id": request.transaction_id},
        {"_id": 0}
    )
    
    if existing_report:
        return ReportResponse(**existing_report)
    
    # Create report record
    report = Report(
        user_id=request.user_id,
        transaction_id=request.transaction_id,
        report_type=request.report_type,
        status=ReportStatus.PENDING
    )
    
    doc = report.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.reports.insert_one(doc)
    logger.info(f"Created report: {report.report_id}")
    
    # Start background processing
    background_tasks.add_task(generate_report_background, report, request)
    
    return ReportResponse(
        report_id=report.report_id,
        status=report.status,
        report_type=report.report_type,
        processing_time_seconds=None
    )

@api_router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    """Get report status and details"""
    report_doc = await db.reports.find_one({"report_id": report_id}, {"_id": 0})
    
    if not report_doc:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return ReportResponse(**report_doc)

@api_router.get("/reports/download/{filename}")
async def download_report(filename: str):
    """Download PDF report"""
    filepath = f"/app/backend/reports/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        filepath,
        media_type='application/pdf',
        filename=filename
    )

# ============= FOLLOW-UP QUESTIONS =============

@api_router.post("/reports/clarify", response_model=FollowUpResponse)
async def clarify_question(question: FollowUpQuestion):
    """
    Answer follow-up questions using Gemini Flash (fast & cheap)
    """
    # Get original report
    report_doc = await db.reports.find_one({"report_id": question.report_id}, {"_id": 0})
    
    if not report_doc:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report_doc['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Report not yet completed")
    
    # Use Gemini Flash for clarification
    answer = gemini_agent.clarify_question(
        original_report=report_doc.get('interpreted_text', ''),
        user_question=question.question
    )
    
    response = FollowUpResponse(
        report_id=question.report_id,
        question=question.question,
        answer=answer
    )
    
    # Optionally save to database
    doc = response.model_dump()
    doc['answered_at'] = doc['answered_at'].isoformat()
    await db.followup_questions.insert_one(doc)
    
    return response

# ============= CHAT SYSTEM =============

@api_router.post("/chat/message", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """
    Send a message in chat conversation
    Handles NLP extraction, validation, and interpretation
    """
    # Get or create session
    session_id = request.session_id
    if not session_id:
        # Create new session
        session = ChatSession(user_id=request.user_id)
        session_id = session.session_id
        
        # Save session
        session_doc = session.model_dump()
        session_doc['created_at'] = session_doc['created_at'].isoformat()
        session_doc['updated_at'] = session_doc['updated_at'].isoformat()
        await db.chat_sessions.insert_one(session_doc)
        
        logger.info(f"Created new chat session: {session_id}")
    else:
        # Load existing session
        session_doc = await db.chat_sessions.find_one({"session_id": session_id}, {"_id": 0})
        if not session_doc:
            raise HTTPException(status_code=404, detail="Session not found")
    
    # Save user message
    user_message = ChatMessage(
        session_id=session_id,
        role=ChatRole.USER,
        content=request.message
    )
    
    msg_doc = user_message.model_dump()
    msg_doc['timestamp'] = msg_doc['timestamp'].isoformat()
    await db.chat_messages.insert_one(msg_doc)
    
    # Get conversation history
    history_docs = await db.chat_messages.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(100)
    
    conversation_history = [
        {"role": msg['role'], "content": msg['content']} 
        for msg in history_docs
    ]
    
    # Extract birth details using NLP
    with open("/tmp/chat_debug.log", "a") as f:
        f.write(f"About to extract from: '{request.message}'\n")
    
    extracted_data = chat_agent.extract_birth_details(
        request.message,
        conversation_history[:-1]  # Exclude current message
    )
    
    with open("/tmp/chat_debug.log", "a") as f:
        f.write(f"Extraction done - confidence={extracted_data.confidence_score}, user={extracted_data.user is not None}, missing={extracted_data.missing_fields}\n")
    
    # If city is extracted but no lat/lon, look it up
    if extracted_data.user and extracted_data.user.place_of_birth:
        place = extracted_data.user.place_of_birth
        if place.city and not place.latitude:
            logger.info(f"Looking up coordinates for city: {place.city}")
            try:
                # Try Indian cities first
                cities = indian_city_service.search_cities(place.city, max_results=1)
                if not cities:
                    # Try international search
                    cities = city_service.search_cities(place.city, max_results=1)
                
                if cities:
                    # Pydantic models are immutable by default, so we need to create a new one
                    from chat_models import PlaceData
                    new_place = PlaceData(
                        city=place.city,
                        region=place.region,
                        country=place.country,
                        latitude=cities[0]['lat'],
                        longitude=cities[0]['lon']
                    )
                    extracted_data.user.place_of_birth = new_place
                    logger.info(f"Found coordinates: {new_place.latitude}, {new_place.longitude}")
            except Exception as e:
                logger.warning(f"Failed to lookup city coordinates: {str(e)}")
    
    # Check if we have enough data
    if extracted_data.confidence_score < 0.6 or extracted_data.missing_fields or not extracted_data.user:
        # Need more information
        followup = chat_agent.generate_followup_question(extracted_data)
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=session_id,
            role=ChatRole.ASSISTANT,
            content=followup,
            extracted_data=extracted_data
        )
        
        msg_doc = assistant_message.model_dump()
        msg_doc['timestamp'] = msg_doc['timestamp'].isoformat()
        if msg_doc.get('extracted_data'):
            msg_doc['extracted_data'] = extracted_data.model_dump()
        await db.chat_messages.insert_one(msg_doc)
        
        # Update session
        await db.chat_sessions.update_one(
            {"session_id": session_id},
            {"$set": {"extracted_data": extracted_data.model_dump(), "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return ChatResponse(
            session_id=session_id,
            message=followup,
            extracted_data=extracted_data,
            requires_followup=True,
            followup_question=followup
        )
    
    # We have enough data - call VedicAstroAPI
    logger.info("Sufficient data extracted, calling VedicAstroAPI...")
    
    bd = extracted_data.user.place_of_birth
    with open("/tmp/chat_debug.log", "a") as f:
        f.write(f"Calling VedicAPI with: dob={extracted_data.user.date_of_birth}, tob={extracted_data.user.time_of_birth}, lat={bd.latitude}, lon={bd.longitude}\n")
    
    # Convert date from YYYY-MM-DD to DD/MM/YYYY for VedicAPI
    dob_obj = datetime.strptime(extracted_data.user.date_of_birth, "%Y-%m-%d")
    dob_formatted = dob_obj.strftime("%d/%m/%Y")
    
    api_response = vedic_client.get_planet_details(
        dob=dob_formatted,
        tob=extracted_data.user.time_of_birth or "12:00",
        lat=bd.latitude or 28.6139,  # Default to Delhi if not available
        lon=bd.longitude or 77.2090,
        tz=5.5
    )
    
    with open("/tmp/chat_debug.log", "a") as f:
        f.write(f"VedicAPI response success: {api_response.get('success')}\n")
        if not api_response.get('success'):
            f.write(f"VedicAPI error: {api_response.get('error')}\n")
    
    if not api_response.get('success'):
        return ChatResponse(
            session_id=session_id,
            message="I encountered an issue fetching your astrological data. Could you please verify your birth details?",
            requires_followup=True
        )
    
    # Generate interpretation
    logger.info("Generating interpretation...")
    interpretation, confidence_metadata = chat_agent.generate_interpretation(
        api_response.get('data', {}),
        extracted_data,
        extracted_data.context.request_type
    )
    
    # Save assistant message
    assistant_message = ChatMessage(
        session_id=session_id,
        role=ChatRole.ASSISTANT,
        content=interpretation,
        confidence_metadata=confidence_metadata
    )
    
    msg_doc = assistant_message.model_dump()
    msg_doc['timestamp'] = msg_doc['timestamp'].isoformat()
    if msg_doc.get('confidence_metadata'):
        msg_doc['confidence_metadata'] = confidence_metadata.model_dump()
    await db.chat_messages.insert_one(msg_doc)
    
    # Update session
    await db.chat_sessions.update_one(
        {"session_id": session_id},
        {"$set": {
            "status": "completed",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return ChatResponse(
        session_id=session_id,
        message=interpretation,
        extracted_data=extracted_data,
        requires_followup=False,
        confidence_metadata=confidence_metadata
    )

@api_router.get("/chat/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Get chat session with message history"""
    
    session = await db.chat_sessions.find_one({"session_id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = await db.chat_messages.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    
    return {
        "session": session,
        "messages": messages
    }

# ============= NIRO CHAT ENDPOINT (Enhanced Orchestrator) =============

@api_router.post("/chat", response_model=OrchestratorChatResponse)
async def niro_chat(request: OrchestratorChatRequest, authorization: Optional[str] = Header(None)):
    """
    NIRO AI Vedic Astrology Chat Endpoint
    
    This endpoint uses the Enhanced Conversation Orchestrator for:
    - Session state management
    - Mode/topic routing with rich taxonomy
    - Vedic API integration for astro profiles and transits
    - Topic-specific chart lever mapping
    - NIRO LLM with structured astro_features
    
    Request body:
    - sessionId: Unique session identifier
    - message: User message or quick reply chip label
    - actionId: Optional action ID when user clicks a chip
    
    Optional Headers:
    - Authorization: Bearer <token> (for authenticated user context with saved birth details)
    
    Returns structured response with:
    - reply: { rawText, summary, reasons[], remedies[] }
    - mode: Conversation mode (BIRTH_COLLECTION, PAST_THEMES, FOCUS_READING, etc.)
    - focus: Topic (career, romantic_relationships, money, health_energy, etc.)
    - suggestedActions: Quick reply chips for follow-up
    - requestId: Checklist report ID for debugging
    """
    import uuid
    
    # Generate unique request ID for this chat session
    request_id = str(uuid.uuid4())[:8]
    
    try:
        # If user is authenticated, load their profile from token context
        user_id = None
        user_profile = None
        if authorization:
            try:
                parts = authorization.split()
                if len(parts) == 2 and parts[0].lower() == 'bearer':
                    token = parts[1]
                    from backend.auth.auth_service import get_auth_service
                    auth_service = get_auth_service()
                    payload = auth_service.verify_token(token)
                    if payload:
                        user_id = payload.get('user_id')
                        user_profile = auth_service.get_profile(user_id)
                        if user_profile:
                            logger.info(f"Chat request authenticated - user: {user_id}, profile_complete: True")
            except Exception as e:
                logger.debug(f"Could not load user profile from token: {e}")
        
        logger.info(f"NIRO Enhanced Orchestrator request - session: {request.sessionId}, request_id: {request_id}, action: {request.actionId}, user: {user_id}")
        
        # Log user profile for debugging
        if user_profile:
            logger.info(f"User profile loaded: name={user_profile.get('name')}, dob={user_profile.get('dob')}, location={user_profile.get('location')}")
        else:
            logger.info(f"No user profile loaded for user_id={user_id}")
        
        # If user has a complete profile, don't ask for birth details again
        if user_profile and user_profile.get('dob') and user_profile.get('tob') and user_profile.get('location'):
            # Override request subjectData with user's saved profile
            request.subjectData = {
                'name': user_profile.get('name', ''),
                'birthDetails': {  # Use the correct key format for enhanced orchestrator
                    'dob': user_profile.get('dob'),
                    'tob': user_profile.get('tob'),
                    'location': user_profile.get('location'),
                    'latitude': user_profile.get('birth_place_lat'),
                    'longitude': user_profile.get('birth_place_lon'),
                    'timezone': user_profile.get('birth_place_tz', 5.5)
                }
            }
        
        # Process message through the enhanced orchestrator
        response = await enhanced_orchestrator.process_message(request)
        
        # Add request ID to response for checklist tracking
        response.requestId = request_id
        
        # Store message in database for history
        niro_message_doc = {
            "session_id": request.sessionId,
            "request_id": request_id,
            "user_id": user_id,  # Track authenticated user if available
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_message": request.message,
            "action_id": request.actionId,
            "response": response.model_dump(),
            "mode": response.mode,
            "topic": response.focus  # Store as topic for new schema
        }
        await db.niro_messages.insert_one(niro_message_doc)
        
        # Generate checklist report for debugging/observability
        try:
            from backend.observability.checklist_report import ChecklistReport
            checklist_gen = ChecklistReport()
            
            # Extract birth details from request for checklist
            birth_details_for_checklist = None
            if request.subjectData and request.subjectData.get('birthDetails'):
                bd = request.subjectData.get('birthDetails', {})
                birth_details_for_checklist = {
                    "dob": bd.get('dob'),
                    "tob": bd.get('tob'),
                    "location": bd.get('location'),
                    "lat": bd.get('latitude'),
                    "lon": bd.get('longitude'),
                    "tz": bd.get('timezone', 5.5)
                }
            
            checklist_gen.generate_report(
                request_id=request_id,
                session_id=request.sessionId,
                user_input=request.message,
                birth_details=birth_details_for_checklist,
                intent_data={"topic": response.focus, "mode": response.mode, "action_id": request.actionId},
                api_calls=[],  # Will be populated if we track API calls
                reading_pack={},  # Will be populated if we track astro features
                llm_metadata={"model": "niro"},  # Placeholder
                llm_response={
                    "summary": response.reply.summary if response.reply else "",
                    "reasons": response.reply.reasons if response.reply else [],
                    "remedies": response.reply.remedies if response.reply else []
                },
                errors=None,
                final_response=response.model_dump()
            )
            logger.info(f"Checklist report generated for request {request_id}")
        except Exception as report_err:
            logger.error(f"Failed to generate checklist report for {request_id}: {report_err}", exc_info=True)
        
        logger.info(f"NIRO Enhanced response - mode: {response.mode}, topic: {response.focus}")
        
        # ============= STRUCTURED LOGGING =============
        # Log the full pipeline for observability
        if hasattr(response, '_pipeline_metadata') and response._pipeline_metadata:
            from niro_logging.niro_logger import (
                log_pipeline_event,
                summarize_astro_profile,
                summarize_astro_transits,
                summarize_astro_features,
                summarize_llm_payload,
                summarize_llm_response
            )
            
            metadata = response._pipeline_metadata
            
            pipeline_log = {
                "timestamp": datetime.now(timezone.utc).isoformat() + 'Z',
                "session_id": request.sessionId,
                "user_id": request.sessionId,  # Using session as user ID for now
                "user_message": request.message[:200],
                "action_id": request.actionId,
                "mode": response.mode,
                "topic_classification": metadata.get('topic_classification', {}),
                "astro_profile": summarize_astro_profile(metadata.get('astro_profile')),
                "astro_transits": summarize_astro_transits(metadata.get('astro_transits')),
                "astro_features_summary": summarize_astro_features(metadata.get('astro_features')),
                "llm_payload_summary": summarize_llm_payload(
                    response.mode,
                    response.focus or "unknown",
                    bool(metadata.get('astro_features'))
                ),
                "llm_response_summary": summarize_llm_response(metadata.get('llm_response'))
            }
            
            log_pipeline_event(pipeline_log)
        
        return response
        
    except Exception as e:
        logger.error(f"NIRO Enhanced Orchestrator error: {str(e)}", exc_info=True)
        
        # Return graceful error response with actual error details
        from backend.conversation.models import NiroReply, SuggestedAction
        
        error_message = str(e)
        # Check if it's a Vedic API error
        if 'VEDIC_API' in error_message or 'VedicApiError' in error_message:
            summary = "The Vedic API service is temporarily unavailable. Please try again in a moment."
        elif 'profile' in error_message.lower():
            summary = "Please complete your birth details first to get personalized readings."
        else:
            summary = f"I encountered an issue: {error_message}. Please try again."
        
        error_reply = NiroReply(
            rawText=summary,
            summary=summary,
            reasons=[
                error_message[:100]
            ],
            remedies=[]
        )
        
        # Try to generate error checklist report
        try:
            from backend.observability.checklist_report import ChecklistReport
            checklist_gen = ChecklistReport()
            checklist_gen.generate_report(
                request_id=request_id,
                session_id=request.sessionId,
                user_input=request.message,
                intent_data={"action_id": request.actionId},
                errors=[error_message],
                final_response={"error": summary, "mode": "ERROR"}
            )
            logger.info(f"Error checklist report generated for request {request_id}")
        except Exception as report_err:
            logger.warning(f"Failed to generate error checklist: {report_err}")
        
        return OrchestratorChatResponse(
            reply=error_reply,
            mode="ERROR",
            focus=None,
            suggestedActions=[
                SuggestedAction(id="retry", label="Try again"),
                SuggestedAction(id="focus_career", label="Career"),
                SuggestedAction(id="focus_relationship", label="Relationships")
            ],
            requestId=request_id
        )


# ============= NIRO SESSION MANAGEMENT ENDPOINTS =============

@api_router.get("/chat/session/{session_id}")
async def get_niro_session(session_id: str):
    """
    Get current session state for debugging and monitoring.
    """
    state = enhanced_orchestrator.get_session_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Try to get astro profile info if available
    astro_info = await enhanced_orchestrator.get_astro_profile(session_id)
    
    return {
        "session_id": state.session_id,
        "mode": state.mode,
        "topic": state.focus,  # topic stored in focus field
        "has_birth_details": state.birth_details is not None,
        "has_done_retro": state.has_done_retro,
        "message_count": state.message_count,
        "created_at": state.created_at.isoformat(),
        "updated_at": state.updated_at.isoformat(),
        "astro_profile": astro_info
    }


@api_router.post("/chat/session/{session_id}/birth-details")
async def set_niro_birth_details(session_id: str, birth_details: OrchestratorBirthDetails):
    """
    Manually set birth details for a session.
    Useful for pre-populating from user profile.
    """
    success = enhanced_orchestrator.set_birth_details(session_id, birth_details)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True, "message": "Birth details updated"}


@api_router.delete("/chat/session/{session_id}")
async def reset_niro_session(session_id: str):
    """
    Reset a session to initial state.
    """
    success = enhanced_orchestrator.reset_session(session_id)
    return {"success": success, "message": "Session reset" if success else "Session not found"}


# ============= NIRO TOPIC TAXONOMY ENDPOINT =============

@api_router.get("/chat/topics")
async def get_niro_topics():
    """
    Get the full topic taxonomy supported by NIRO.
    """
    return {
        "topics": [
            {"id": Topic.SELF_PSYCHOLOGY.value, "label": "Self & Psychology", "description": "Personality, identity, life purpose"},
            {"id": Topic.CAREER.value, "label": "Career", "description": "Job, profession, work life"},
            {"id": Topic.MONEY.value, "label": "Money & Finances", "description": "Income, investments, wealth"},
            {"id": Topic.ROMANTIC_RELATIONSHIPS.value, "label": "Romantic Relationships", "description": "Dating, love, attraction"},
            {"id": Topic.MARRIAGE_PARTNERSHIP.value, "label": "Marriage & Partnership", "description": "Spouse, marriage, commitment"},
            {"id": Topic.FAMILY_HOME.value, "label": "Family & Home", "description": "Parents, children, household"},
            {"id": Topic.FRIENDS_SOCIAL.value, "label": "Friends & Social", "description": "Friendships, networking, community"},
            {"id": Topic.LEARNING_EDUCATION.value, "label": "Education", "description": "Studies, exams, learning"},
            {"id": Topic.HEALTH_ENERGY.value, "label": "Health & Energy", "description": "Physical health, wellness, vitality"},
            {"id": Topic.SPIRITUALITY.value, "label": "Spirituality", "description": "Inner growth, karma, dharma"},
            {"id": Topic.TRAVEL_RELOCATION.value, "label": "Travel & Relocation", "description": "Foreign travel, moving, immigration"},
            {"id": Topic.LEGAL_CONTRACTS.value, "label": "Legal & Contracts", "description": "Court cases, agreements, disputes"},
            {"id": Topic.DAILY_GUIDANCE.value, "label": "Daily Guidance", "description": "Today's cosmic weather"},
            {"id": Topic.GENERAL.value, "label": "General", "description": "Overall life guidance"},
        ]
    }


# ============= MICRO-FEEDBACK ENDPOINT =============

class FeedbackRequest(BaseModel):
    """Request model for micro-feedback"""
    response_id: str = Field(..., description="ID of the AI response being rated")
    session_id: str = Field(..., description="Session identifier")
    feedback: str = Field(..., description="Feedback value: 'positive' or 'negative'")
    message_preview: Optional[str] = Field(None, description="Preview of the message being rated")


@api_router.post("/chat/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit micro-feedback for an AI response.
    
    Used to collect "Does this feel accurate?" feedback (👍/👎).
    """
    import logging
    feedback_logger = logging.getLogger("niro_feedback")
    
    # Log feedback
    feedback_logger.info(
        f"[FEEDBACK] response_id={request.response_id} "
        f"session_id={request.session_id} "
        f"feedback={request.feedback} "
        f"preview={request.message_preview[:50] if request.message_preview else 'N/A'}"
    )
    
    # Store in database (optional - for analytics)
    try:
        feedback_doc = {
            "response_id": request.response_id,
            "session_id": request.session_id,
            "feedback": request.feedback,
            "message_preview": request.message_preview,
            "timestamp": datetime.utcnow().isoformat()
        }
        await db.niro_feedback.insert_one(feedback_doc)
    except Exception as e:
        logger.warning(f"Could not store feedback in database: {e}")
    
    return {
        "success": True,
        "message": "Thank you for your feedback!"
    }


# ============= PERSONALIZED WELCOME MESSAGE ENDPOINT =============

@api_router.get("/profile/welcome")
async def get_personalized_welcome(authorization: Optional[str] = Header(None)):
    """
    Get personalized welcome message based on user's astrological profile.
    
    Uses the Confidence-Aware Welcome Engine to generate:
    - Personality anchor (Moon sign + Ascendant traits)
    - Current life phase insight (Mahadasha/Antardasha)
    
    Requires authentication via JWT token.
    
    Response:
    {
        "ok": true,
        "welcome_message": "Welcome, Sharad. With Moon in Gemini...",
        "confidence_map": { "personality": "high", "past_theme": null, "current_phase": "high" },
        "suggested_questions": ["What does my career look like?", ...]
    }
    """
    try:
        # Extract and verify JWT token
        if not authorization:
            return {
                "ok": False,
                "error": "Authentication required",
                "welcome_message": "Welcome! Please complete your birth details to get personalized insights."
            }
        
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return {
                "ok": False,
                "error": "Invalid authorization format",
                "welcome_message": "Welcome! Please complete your birth details to get personalized insights."
            }
        
        token = parts[1]
        
        # Verify token
        auth_service = get_auth_service()
        payload = auth_service.verify_token(token)
        if not payload:
            return {
                "ok": False,
                "error": "Invalid token",
                "welcome_message": "Welcome! Please complete your birth details to get personalized insights."
            }
        
        user_id = payload.get('user_id')
        user_profile = auth_service.get_profile(user_id)
        
        if not user_profile:
            return {
                "ok": False,
                "error": "Profile not found",
                "welcome_message": "Welcome! Please complete your birth details to get personalized insights."
            }
        
        # Check if birth details are complete
        if not user_profile.get('dob') or not user_profile.get('tob') or not user_profile.get('location'):
            return {
                "ok": False,
                "error": "Incomplete birth details",
                "welcome_message": "Welcome! Please complete your birth details to get personalized insights."
            }
        
        # Fetch astrological profile
        from backend.astro_client.vedic_api import vedic_api_client
        from backend.astro_client.models import BirthDetails
        from backend.conversation.welcome_builder import generate_welcome_message
        
        # Parse birth details
        dob_str = user_profile.get('dob')
        if isinstance(dob_str, str):
            from datetime import datetime as dt, date
            # Handle various date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    dob = dt.strptime(dob_str, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                dob = date.today()  # Fallback
        else:
            dob = dob_str
        
        birth = BirthDetails(
            dob=dob,
            tob=user_profile.get('tob', '12:00'),
            location=user_profile.get('location', ''),
            latitude=user_profile.get('birth_place_lat'),
            longitude=user_profile.get('birth_place_lon'),
            timezone=user_profile.get('birth_place_tz', 5.5)
        )
        
        # Fetch full astro profile
        try:
            astro_profile = await vedic_api_client.fetch_full_profile(birth, user_id=user_id)
        except Exception as e:
            logger.error(f"Failed to fetch astro profile for welcome: {e}")
            return {
                "ok": False,
                "error": f"Could not generate astrological profile: {str(e)}",
                "welcome_message": f"Welcome, {user_profile.get('name', '')}! I'm ready to explore your questions."
            }
        
        # Generate personalized welcome message using NEW Welcome Builder
        user_name = user_profile.get('name', '').split()[0] if user_profile.get('name') else None
        welcome_result = await generate_welcome_message(
            first_name=user_name or "there",
            astro_profile=astro_profile.model_dump() if hasattr(astro_profile, 'model_dump') else dict(astro_profile),
            signals=None  # Optional signals for past theme detection
        )
        
        # Generate suggested questions based on current dasha
        suggested_questions = []
        if astro_profile.current_mahadasha:
            maha_planet = astro_profile.current_mahadasha.planet
            
            # Planet-specific question suggestions (5 questions each)
            planet_questions = {
                "Sun": ["How can I step into leadership roles?", "What recognition can I expect this year?", "What's my career outlook?", "How can I boost my confidence?", "What creative projects should I pursue?"],
                "Moon": ["How can I improve my emotional well-being?", "What's the outlook for my home life?", "How can I nurture my relationships?", "What about my family dynamics?", "How can I trust my intuition more?"],
                "Mars": ["Is this a good time for bold career moves?", "How should I channel my energy?", "What challenges should I prepare for?", "How can I be more assertive?", "What physical activities would benefit me?"],
                "Mercury": ["What skills should I develop now?", "How's my communication outlook?", "What learning opportunities await?", "How can I improve my networking?", "What business ideas should I explore?"],
                "Jupiter": ["What opportunities are coming my way?", "Is this good for higher education?", "How can I expand my horizons?", "What about my spiritual growth?", "How can I attract more abundance?"],
                "Venus": ["What's my relationship outlook?", "How can I attract more abundance?", "What creative pursuits should I explore?", "How can I enhance my social life?", "What about love and romance?"],
                "Saturn": ["What long-term goals should I focus on?", "How can I build lasting foundations?", "What discipline do I need to develop?", "How can I overcome obstacles?", "What career stability can I expect?"],
                "Rahu": ["What unconventional paths should I explore?", "Where is my ambition leading me?", "What new experiences await?", "How can I break free from limitations?", "What foreign opportunities exist?"],
                "Ketu": ["What should I let go of?", "How can I deepen my spiritual practice?", "What past patterns need healing?", "How can I find inner peace?", "What wisdom am I gaining?"]
            }
            
            suggested_questions = planet_questions.get(maha_planet, [
                "What does my career look like?",
                "What's my relationship outlook?",
                "How's my health and energy?",
                "What opportunities are coming?",
                "How can I grow spiritually?"
            ])
        else:
            suggested_questions = [
                "What does my career look like?",
                "What's my relationship outlook?",
                "How's my health and energy?",
                "What opportunities are coming?",
                "How can I grow spiritually?"
            ]
        
        logger.info(f"Generated personalized welcome for user {user_id} with confidence: {welcome_result['confidence_map']}")
        
        return {
            "ok": True,
            "welcome_message": welcome_result['welcome_message'],
            "confidence_map": welcome_result['confidence_map'],
            "word_count": welcome_result['word_count'],
            "sections_included": welcome_result['sections_included'],
            "suggested_questions": suggested_questions
        }
        
    except Exception as e:
        logger.error(f"Error generating personalized welcome: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "ok": False,
            "error": str(e),
            "welcome_message": "Welcome! I'm ready to explore your astrological questions."
        }


# ============= KUNDLI ENDPOINT =============

@api_router.get("/kundli")
async def get_kundli(
    request: Request,
    authorization: Optional[str] = Header(None),
    style: Optional[str] = Query(default="north", description="Chart style: 'north' or 'south'")
):
    """
    Get Kundli chart (birth chart) as SVG + structured data.
    
    Requires authentication via JWT token in Authorization header OR session cookie.
    
    Query Parameters:
    - style: 'north' (default) or 'south' - Chart rendering style
        - North Indian: Diamond layout, houses are fixed positions, signs move
        - South Indian: Square layout, signs are fixed positions, houses move
    
    Response:
    {
        "ok": true,
        "svg": "<svg>...</svg>",
        "profile": { "name": "...", "dob": "...", "tob": "...", "location": "..." },
        "structured": {
            "ascendant": { "sign": "...", "degree": 0.0, "house": 1 },
            "houses": [ ... ],
            "planets": [ ... ]
        },
        "source": { "vendor": "VedicAstroAPI", "chart_type": "birth_chart", "format": "svg", "style": "north" }
    }
    """
    try:
        # Validate style parameter
        chart_style = style.lower() if style else "north"
        if chart_style not in ["north", "south"]:
            chart_style = "north"
        
        # Try Google OAuth session auth first (cookie or header)
        user_id = None
        profile_data = None
        
        # Check for session token in cookie
        session_token = request.cookies.get("session_token")
        
        # Fallback to Authorization header
        if not session_token and authorization:
            parts = authorization.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                session_token = parts[1]
        
        if session_token:
            # Try new Google OAuth session
            session_doc = await db.user_sessions.find_one(
                {"session_token": session_token},
                {"_id": 0}
            )
            
            if session_doc:
                from datetime import datetime, timezone
                expires_at = session_doc.get("expires_at")
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at)
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                if expires_at > datetime.now(timezone.utc):
                    user_id = session_doc["user_id"]
                    # Get profile from users collection
                    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
                    if user_doc:
                        profile_data = {
                            "name": user_doc.get("name", ""),
                            "dob": user_doc.get("dob"),
                            "tob": user_doc.get("tob"),
                            "location": user_doc.get("pob") or user_doc.get("location", {})
                        }
        
        # Fallback to old JWT auth if no session found
        if not user_id and authorization:
            parts = authorization.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
                auth_service = get_auth_service()
                payload = auth_service.verify_token(token)
                if payload:
                    user_id = payload.get('user_id')
                    user_info = auth_service.get_user_info(user_id)
                    if user_info and user_info.get('profile_complete'):
                        profile_data = auth_service.get_profile(user_id)
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        if not profile_data or not profile_data.get('dob') or not profile_data.get('tob'):
            return {
                "ok": False,
                "error": "PROFILE_INCOMPLETE",
                "message": "Complete your profile with birth details to view Kundli"
            }
        
        # Parse birth details
        from backend.astro_client.models import BirthDetails
        try:
            birth_details = BirthDetails(
                dob=datetime.strptime(profile_data['dob'], '%Y-%m-%d').date(),
                tob=profile_data['tob'],
                location=profile_data['location'],
                timezone=5.5  # Default to IST
            )
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse birth details: {e}")
            return {
                "ok": False,
                "error": "KUNDLI_FETCH_FAILED",
                "message": "Invalid birth details format"
            }
        
        # Fetch raw chart data from Vedic API
        from backend.astro_client.vedic_api import vedic_api_client
        
        # Get planet-details API data
        api_params = {
            'dob': birth_details.dob.strftime("%d/%m/%Y"),
            'tob': birth_details.tob,
            'lat': birth_details.latitude or 28.6139,
            'lon': birth_details.longitude or 77.2090,
            'tz': birth_details.timezone,
        }
        
        try:
            # Fetch planet details from API
            planet_details = await vedic_api_client._get('/horoscope/planet-details', api_params.copy())
            
            # Use STRICT template-based renderer (Astrosage reference)
            from backend.astro_client.kundli_normalize import normalize_kundli_data, NormalizationError, sign_num_to_name
            from backend.astro_client.kundli_render import render_kundli_chart, RenderingError
            
            # Normalize the API response with STRICT validation
            try:
                normalized = normalize_kundli_data({'response': planet_details})
            except NormalizationError as e:
                logger.error(f"[KUNDLI] Normalization failed: {e}")
                return {
                    "ok": False,
                    "error": "NORMALIZATION_FAILED",
                    "message": str(e)
                }
            
            # Get user name for title
            user_name = profile_data.get('name', 'User')
            
            # Render SVG using STRICT template-based renderer
            try:
                svg = render_kundli_chart(normalized, style=chart_style, title=f"{user_name} - Kundli")
            except RenderingError as e:
                logger.error(f"[KUNDLI] Rendering failed: {e}")
                return {
                    "ok": False,
                    "error": "RENDERING_FAILED",
                    "message": str(e)
                }
            
            # Build structured data for frontend
            structured = {
                "ascendant": {
                    "sign": normalized["ascendant_sign"],
                    "sign_num": normalized["ascendant_sign_num"],
                    "degree": normalized["ascendant_degree"],
                    "house": 1
                },
                "houses": [
                    {
                        "house": h["house"],
                        "sign": h["sign"],
                        "sign_num": h["sign_num"],
                        "sign_code": h["sign_code"]
                    }
                    for h in normalized["houses"]
                ],
                "planets": [
                    {
                        "name": p["code"],
                        "full_name": p["name"],
                        "sign": p["sign"],
                        "sign_num": p["sign_num"],
                        "degree": p["degree"],
                        "house": p["house"],
                        "is_retrograde": p["is_retrograde"]
                    }
                    for p in normalized["planets"]
                ]
            }
            
            logger.info(f"[KUNDLI] session={user_id} ok=true style={chart_style} svg_bytes={len(svg)} planets={len(normalized['planets'])}")
            
            return {
                "ok": True,
                "svg": svg,
                "profile": {
                    "name": profile_data.get('name', 'User'),
                    "dob": profile_data.get('dob'),
                    "tob": profile_data.get('tob'),
                    "location": profile_data.get('location')
                },
                "structured": structured,
                "source": {
                    "vendor": "VedicAstroAPI",
                    "chart_type": "birth_chart",
                    "format": "svg",
                    "style": chart_style
                }
            }
            
        except Exception as api_error:
            logger.error(f"Vedic API error: {api_error}")
            return {
                "ok": False,
                "error": "VEDIC_API_ERROR",
                "message": str(api_error)
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_kundli: {e}", exc_info=True)
        logger.error(f"[KUNDLI] session=unknown ok=false error={str(e)}")
        raise HTTPException(status_code=502, detail="Failed to fetch Kundli")


def _get_planet_full_name(abbr: str) -> str:
    """Get full planet name from abbreviation."""
    names = {
        'Su': 'Sun', 'Mo': 'Moon', 'Ma': 'Mars', 'Me': 'Mercury',
        'Ju': 'Jupiter', 'Ve': 'Venus', 'Sa': 'Saturn', 'Ra': 'Rahu', 'Ke': 'Ketu'
    }
    return names.get(abbr, abbr)


# ============= DEBUG KUNDLI RENDER ENDPOINT =============

@api_router.get("/debug/render_kundli")
async def debug_render_kundli(
    style: str = Query(default="north", description="Chart style: 'north' or 'south'"),
    dob: str = Query(default="24/01/1986", description="Date of birth (DD/MM/YYYY)"),
    tob: str = Query(default="06:32", description="Time of birth (HH:MM)"),
    lat: float = Query(default=28.89, description="Latitude"),
    lon: float = Query(default=76.57, description="Longitude"),
    tz: float = Query(default=5.5, description="Timezone offset"),
    name: str = Query(default="Test User", description="Name for title")
):
    """
    Debug endpoint to render kundli chart directly from birth details.
    No authentication required - for testing only.
    
    Returns SVG directly with content-type image/svg+xml
    
    Uses STRICT normalization and rendering following Astrosage reference.
    """
    from fastapi.responses import Response
    import httpx
    import os
    
    try:
        from backend.astro_client.kundli_normalize import normalize_kundli_data, NormalizationError
        from backend.astro_client.kundli_render import render_kundli_chart, RenderingError
        
        # Fetch from Vedic API
        api_key = os.environ.get('VEDIC_API_KEY')
        if not api_key:
            return {"ok": False, "error": "VEDIC_API_KEY not configured"}
        
        url = 'https://api.vedicastroapi.com/v3-json/horoscope/planet-details'
        params = {
            'api_key': api_key,
            'dob': dob,
            'tob': tob,
            'lat': str(lat),
            'lon': str(lon),
            'tz': str(tz),
            'lang': 'en'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30)
            api_data = response.json()
        
        if api_data.get('status') != 200:
            return {"ok": False, "error": "API_ERROR", "details": api_data}
        
        # Normalize with STRICT validation
        try:
            normalized = normalize_kundli_data(api_data)
        except NormalizationError as e:
            return {"ok": False, "error": "NORMALIZATION_FAILED", "message": str(e)}
        
        # Render with STRICT validation
        try:
            svg = render_kundli_chart(normalized, style=style, title=f"{name} - Kundli")
        except RenderingError as e:
            return {"ok": False, "error": "RENDERING_FAILED", "message": str(e)}
        
        return Response(content=svg, media_type="image/svg+xml")
        
    except Exception as e:
        logger.error(f"Debug render error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


# ============= CHECKLIST & PROCESSING ENDPOINTS =============

@api_router.get("/processing/checklist/{request_id}")
async def get_processing_checklist(request_id: str, authorization: Optional[str] = Header(None)):
    """
    Retrieve structured checklist/processing report for a request as JSON.
    
    Requires optional JWT token (for multi-tenant safety in future).
    
    Response format:
    {
        "ok": true,
        "request_id": "...",
        "timestamp": "...",
        "user_input": { "message": "..." },
        "birth_details": { "name": "...", "dob": "...", "tob": "...", "place": "..." },
        "api_calls": [ { "name": "extended-kundli-details", "status": "ok", "duration_ms": 123 } ],
        "reading_pack": { "signals_kept": 6, "timing_windows": 2, "data_gaps": 0 },
        "llm": { "model": "niro", "tokens_in": null, "tokens_out": null },
        "final": { "status": "ok" }
    }
    """
    try:
        from backend.observability.checklist_report import ChecklistReport
        import json
        from pathlib import Path
        
        checklist_service = ChecklistReport()
        
        # Try to find and parse the checklist metadata (if stored alongside HTML)
        checklist_file = checklist_service.checklists_dir / f"{request_id}.html"
        metadata_file = checklist_service.checklists_dir / f"{request_id}.json"
        
        # Check if we have metadata JSON
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                return {
                    "ok": True,
                    "request_id": request_id,
                    "timestamp": metadata.get('timestamp', ''),
                    "user_input": {
                        "message": metadata.get('user_input', ''),
                        "topic": metadata.get('topic', ''),
                        "mode": metadata.get('mode', '')
                    },
                    "birth_details": metadata.get('birth_details', {}),
                    "api_calls": metadata.get('api_calls', []),
                    "reading_pack": {
                        "signals_kept": metadata.get('reading_pack', {}).get('signals_kept', 0),
                        "timing_windows": metadata.get('reading_pack', {}).get('timing_windows', 0),
                        "data_gaps": metadata.get('reading_pack', {}).get('data_gaps', 0),
                    },
                    "llm": {
                        "model": metadata.get('llm', {}).get('model', 'niro'),
                        "tokens_in": metadata.get('llm', {}).get('tokens_in'),
                        "tokens_out": metadata.get('llm', {}).get('tokens_out'),
                    },
                    "final": {
                        "status": metadata.get('final', {}).get('status', 'unknown'),
                        "summary": metadata.get('final', {}).get('summary', '')
                    }
                }
            except Exception as e:
                logger.error(f"Failed to parse metadata for {request_id}: {e}")
        
        # Fallback: If no metadata, return minimal response with empty data
        if checklist_file.exists():
            return {
                "ok": True,
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_input": {
                    "message": "Unknown",
                    "topic": "general",
                    "mode": "ERROR"
                },
                "birth_details": {
                    "name": "Unknown",
                    "dob": "Unknown",
                    "tob": "Unknown",
                    "place": "Unknown",
                    "lat": 0,
                    "lon": 0,
                    "tz": 5.5
                },
                "api_calls": [],
                "reading_pack": {
                    "signals_kept": 0,
                    "timing_windows": 0,
                    "data_gaps": 0
                },
                "llm": {
                    "model": "niro",
                    "tokens_in": None,
                    "tokens_out": None
                },
                "final": {
                    "status": "ok",
                    "summary": "Checklist available"
                }
            }
        
        # Not found
        raise HTTPException(status_code=404, detail=f"Checklist for request {request_id} not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching checklist {request_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch checklist")


# ============= DEBUG & OBSERVABILITY ENDPOINTS =============

@api_router.get("/debug/checklist/{request_id}")
async def get_checklist_report(request_id: str):
    """
    Retrieve checklist/debug report for a request.
    
    Response:
    - Content-Type: text/html
    - Body: Formatted HTML checklist with full request context
    
    Use case: User clicks "+ Invite alia to see this report" → Opens this endpoint in new tab
    """
    from backend.observability.checklist_report import get_checklist_report
    from fastapi.responses import HTMLResponse
    
    checklist_service = get_checklist_report()
    html_content = checklist_service.read_report(request_id)
    
    if not html_content:
        raise HTTPException(
            status_code=404,
            detail=f"Checklist report not found for request {request_id}"
        )
    
    return HTMLResponse(content=html_content, status_code=200)


# Include the router in the main app
@app.on_event("startup")
async def init_astro_db():
    """Initialize astro database on startup"""
    import asyncio as _asyncio
    try:
        astro_db = await _asyncio.wait_for(get_astro_db(), timeout=15)
        await _asyncio.wait_for(astro_db.init(), timeout=15)
        logger.info("✅ Astro database initialized")
    except _asyncio.TimeoutError:
        logger.warning("⚠ Astro database init timed out — skipping")
    except Exception as e:
        logger.error(f"Failed to initialize astro database: {e}")

@app.on_event("startup")
async def init_niro_v2_db():
    """Initialize NIRO V2 MongoDB storage on startup"""
    import asyncio as _asyncio
    try:
        if db is not None:
            niro_storage = await _asyncio.wait_for(init_niro_v2_storage(db), timeout=20)
            app.state.niro_v2_storage = niro_storage
            app.state.db = db  # Make database available to Google auth router

            # Also set db for profile module
            from backend.profile import set_db
            set_db(db)

            logger.info("✅ NIRO V2 storage initialized with MongoDB")
        else:
            logger.warning("⚠ NIRO V2 storage not initialized - MongoDB not available")
    except _asyncio.TimeoutError:
        logger.warning("⚠ NIRO V2 MongoDB init timed out — server will still start")
        if db is not None:
            app.state.db = db
    except Exception as e:
        logger.error(f"Failed to initialize NIRO V2 storage: {e}")

@app.on_event("startup")
async def init_simplified_db():
    """Initialize NIRO Simplified MongoDB storage on startup"""
    import asyncio as _asyncio
    try:
        if db is not None:
            simplified_storage = await _asyncio.wait_for(init_simplified_storage(db), timeout=20)
            app.state.simplified_storage = simplified_storage
            logger.info("✅ NIRO Simplified storage initialized with MongoDB")
        else:
            logger.warning("⚠ NIRO Simplified storage not initialized - MongoDB not available")
    except _asyncio.TimeoutError:
        logger.warning("⚠ NIRO Simplified MongoDB init timed out — server will still start")
    except Exception as e:
        logger.error(f"Failed to initialize NIRO Simplified storage: {e}")

logger.info(f"Including API router (legacy): {api_router}")
app.include_router(api_router)
# IMPORTANT: Google auth router MUST be before legacy auth router
# to ensure session tokens are validated before JWT tokens
logger.info(f"Including Google auth router: {google_auth_router}")
app.include_router(google_auth_router, prefix="/api")
logger.info(f"Including auth router (legacy): {auth_router}")
app.include_router(auth_router)
logger.info(f"Including profile router: {profile_router}")
app.include_router(profile_router)
logger.info(f"Including astro router: {astro_router}")
app.include_router(astro_router)
logger.info(f"Including debug router: {debug_router}")
app.include_router(debug_router)
logger.info(f"Including NIRO V2 router: {niro_v2_router}")
app.include_router(niro_v2_router)
logger.info(f"Including NIRO Simplified router: {simplified_router}")
app.include_router(simplified_router)
logger.info(f"Including Admin router: {admin_router}")
app.include_router(admin_router)
logger.info(f"Including Remedies router: {remedies_router}")
app.include_router(remedies_router)
logger.info(f"Including Bookings router: {bookings_router}")
app.include_router(bookings_router)
logger.info(f"Including WhatsApp OTP router: {whatsapp_otp_router}")
app.include_router(whatsapp_otp_router)
logger.info(f"✅ All routers included. Total routes: {len(app.routes)}")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client is not None:
        client.close()
    logger.info("Application shutdown")
