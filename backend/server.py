from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
import time
from typing import List, Optional

# Import our custom modules
from models import (
    User, UserCreate,
    Transaction, TransactionCreate, MockPaymentVerify,
    Report, ReportRequest, ReportResponse, ReportStatus,
    FollowUpQuestion, FollowUpResponse,
    PriceConfig, PriceUpdate, ReportType, PaymentStatus
)
from gemini_agent import GeminiAgent
from sandbox_executor import get_sandbox_executor
from pdf_generator import AstroPrescriptionPDF
from prompt_templates import build_code_generation_prompt
from vedic_api_client import VedicAstroClient
from gemini_astro_calculator import GeminiAstroCalculator
from advanced_prompts import build_user_context
from visual_data_extractor import VisualDataExtractor
from time_parser import TimeParser
from city_service import CityService, IndianCityService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize core components
gemini_agent = GeminiAgent()
sandbox_executor = get_sandbox_executor(use_docker=True)  # Use Docker for production
pdf_generator = AstroPrescriptionPDF(output_dir="/app/backend/reports")
vedic_client = VedicAstroClient()  # Direct API client for MVP
visual_extractor = VisualDataExtractor()  # Visual data extraction for charts
time_parser = TimeParser()  # Smart time parsing
city_service = CityService()  # City autocomplete with GeoNames
indian_city_service = IndianCityService()  # Comprehensive Indian cities database

# Create the main app without a prefix
app = FastAPI(title="Astro-Trust Engine API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= HEALTH CHECK =============

@api_router.get("/")
async def root():
    return {
        "message": "Astro-Trust Engine API",
        "version": "1.0.0",
        "status": "operational"
    }

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "gemini_configured": bool(os.environ.get('GEMINI_API_KEY')),
        "vedic_api_configured": bool(os.environ.get('VEDIC_API_KEY')),
        "database": "connected"
    }

# ============= UTILITY ENDPOINTS =============

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

@api_router.get("/utils/search-cities")
async def search_cities_endpoint(query: str, max_results: int = 10):
    """
    Search cities with autocomplete
    
    Query params:
    - query: Search query (min 3 characters)
    - max_results: Max results to return (default 10)
    
    Returns: List of cities with lat, lon, timezone
    """
    if len(query) < 3:
        return {"cities": []}
    
    try:
        # Use Indian city database as primary source (fast, reliable, comprehensive)
        cities = indian_city_service.search_cities(query, max_results)
        
        # If no results found in Indian database, try GeoNames for international cities
        if not cities:
            logger.info("No results in Indian database, trying GeoNames")
            cities = city_service.search_cities(query, max_results)
        
        return {"cities": cities}
        
    except Exception as e:
        logger.error(f"City search error: {str(e)}")
        # Use Indian database as fallback on any error
        cities = indian_city_service.search_cities(query, max_results)
        return {"cities": cities}

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
        
        # Step 2: Fetch data from VedicAstroAPI (using direct client for MVP reliability)
        logger.info("Fetching data from VedicAstroAPI...")
        bd = request.birth_details
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
        
        # Step 6: Interpret results with Gemini Pro (with advanced prompts)
        logger.info("Interpreting report with Gemini Pro (advanced prompts)...")
        interpreted_text = gemini_agent.interpret_report(
            raw_json=raw_json,
            report_type=request.report_type,
            user_context=user_context
        )
        
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

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Application shutdown")
