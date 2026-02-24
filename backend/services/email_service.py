"""
Email service for sending transactional emails using Resend API.
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize Resend API
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
BOOKING_EMAIL = os.environ.get('BOOKING_EMAIL', 'booking@getniro.ai')


def is_email_configured() -> bool:
    """Check if email service is properly configured."""
    return bool(RESEND_API_KEY)


async def send_email(
    recipient_email: str,
    subject: str,
    html_content: str
) -> Dict[str, Any]:
    """
    Send an email using Resend API.
    
    Args:
        recipient_email: Email address to send to
        subject: Email subject line
        html_content: HTML content of the email
        
    Returns:
        Dict with status and email_id on success
    """
    if not is_email_configured():
        logger.warning("Email service not configured. RESEND_API_KEY is missing.")
        return {"status": "skipped", "reason": "Email service not configured"}
    
    try:
        import resend
        resend.api_key = RESEND_API_KEY
        
        params = {
            "from": SENDER_EMAIL,
            "to": [recipient_email],
            "subject": subject,
            "html": html_content
        }
        
        # Run sync SDK in thread to keep FastAPI non-blocking
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent successfully to {recipient_email}, id: {email.get('id')}")
        
        return {
            "status": "success",
            "message": f"Email sent to {recipient_email}",
            "email_id": email.get("id")
        }
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return {"status": "error", "reason": str(e)}


ADMIN_EMAILS = [
    os.environ.get('ADMIN_EMAIL_1', 'sharad@getniro.ai'),
    os.environ.get('ADMIN_EMAIL_2', 'manu@getniro.ai'),
]


async def send_booking_confirmation(
    booking_id: str,
    customer_name: str,
    customer_email: str,
    customer_phone: str,
    expert_id: str,
    scheduled_date: datetime,
    topic_id: str,
    questions: list,
) -> None:
    """
    Send booking confirmation emails to 3 parties:
    1. Admin team (Sharad + Manu)
    2. Customer
    """
    time_str = scheduled_date.strftime("%B %d, %Y at %I:%M %p IST") if scheduled_date else "TBD"
    questions_html = "".join(
        f"<li style='margin:4px 0;'>{q}</li>" for q in questions if q
    ) or "<li style='color:#999;'>No questions provided</li>"

    # --- Admin email ---
    admin_html = f"""
    <!DOCTYPE html><html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:0 auto;padding:20px;">
    <div style="background:linear-gradient(135deg,#3E827A,#5A9A92);padding:24px;border-radius:10px 10px 0 0;">
      <h1 style="color:#fff;margin:0;font-size:22px;">New Free Call Booking</h1>
      <p style="color:rgba(255,255,255,0.85);margin:6px 0 0;">Booking ID: {booking_id}</p>
    </div>
    <div style="background:#f5f5f5;padding:24px;border-radius:0 0 10px 10px;">
      <h2 style="color:#3E827A;margin-top:0;">Customer Details</h2>
      <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:8px 0;border-bottom:1px solid #ddd;"><b>Name</b></td><td style="padding:8px 0;border-bottom:1px solid #ddd;">{customer_name}</td></tr>
        <tr><td style="padding:8px 0;border-bottom:1px solid #ddd;"><b>Email</b></td><td style="padding:8px 0;border-bottom:1px solid #ddd;">{customer_email}</td></tr>
        <tr><td style="padding:8px 0;border-bottom:1px solid #ddd;"><b>Phone</b></td><td style="padding:8px 0;border-bottom:1px solid #ddd;">{customer_phone or 'Not provided'}</td></tr>
        <tr><td style="padding:8px 0;border-bottom:1px solid #ddd;"><b>Expert ID</b></td><td style="padding:8px 0;border-bottom:1px solid #ddd;">{expert_id or 'Any'}</td></tr>
        <tr><td style="padding:8px 0;border-bottom:1px solid #ddd;"><b>Topic ID</b></td><td style="padding:8px 0;border-bottom:1px solid #ddd;">{topic_id or 'N/A'}</td></tr>
        <tr><td style="padding:8px 0;"><b>Scheduled</b></td><td style="padding:8px 0;">{time_str}</td></tr>
      </table>
      <h2 style="color:#3E827A;margin-top:24px;">Customer's Questions</h2>
      <ul style="background:#fff;padding:12px 12px 12px 28px;border-radius:8px;">{questions_html}</ul>
      <div style="margin-top:20px;padding:12px;background:#fff3e0;border-radius:8px;border-left:4px solid #ff9800;">
        <b style="color:#e65100;">Action:</b> Assign an astrologer and confirm the call via WhatsApp.
      </div>
    </div>
    </body></html>
    """

    # --- Customer email ---
    customer_html = f"""
    <!DOCTYPE html><html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:0 auto;padding:20px;">
    <div style="background:linear-gradient(135deg,#3E827A,#5A9A92);padding:24px;border-radius:10px 10px 0 0;">
      <h1 style="color:#fff;margin:0;font-size:22px;">Your Free Consultation is Confirmed!</h1>
    </div>
    <div style="background:#f9f9f9;padding:24px;border-radius:0 0 10px 10px;">
      <p style="font-size:16px;">Hi {customer_name},</p>
      <p>Your free 10-minute consultation call with Niro has been successfully scheduled.</p>
      <div style="background:#fff;border-radius:10px;padding:20px;margin:16px 0;border:1px solid #e0e0e0;">
        <h3 style="color:#3E827A;margin-top:0;">Call Details</h3>
        <p><b>Date & Time:</b> {time_str}</p>
        <p><b>Duration:</b> 10 minutes</p>
        <p><b>Booking ID:</b> <code style="background:#f0f0f0;padding:2px 6px;border-radius:4px;">{booking_id}</code></p>
      </div>
      <p style="color:#555;">You'll receive your astrologer's details and call confirmation on WhatsApp before the scheduled time. Please keep your phone nearby!</p>
      <p style="color:#555;">If you need to reschedule or have questions, reply to this email and we'll be happy to help.</p>
      <p style="margin-top:24px;">Warm regards,<br><b>The Niro Team</b></p>
    </div>
    </body></html>
    """

    # Send to admins and customer concurrently
    tasks = [
        send_email(admin_email, f"New Free Call — {customer_name}", admin_html)
        for admin_email in ADMIN_EMAILS
    ]
    if customer_email:
        tasks.append(send_email(customer_email, "Your free consultation is confirmed ✓", customer_html))

    import asyncio
    await asyncio.gather(*tasks, return_exceptions=True)


async def send_booking_notification(
    user_email: str,
    user_name: str,
    user_phone: Optional[str],
    package_name: str,
    package_tier: str,
    package_price: float,
    topic_name: str,
    transaction_id: str,
    payment_method: str = "Razorpay",
    additional_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send a booking notification email to booking@getniro.ai when a user purchases a package.
    
    Args:
        user_email: Customer's email
        user_name: Customer's name
        user_phone: Customer's phone (optional)
        package_name: Name of the package purchased
        package_tier: Tier level (Focussed/Supported/Comprehensive)
        package_price: Price paid
        topic_name: Topic/category of the package
        transaction_id: Payment transaction ID
        payment_method: Payment method used
        additional_info: Any additional details to include (order_id, plan_id, birth details, etc.)
        
    Returns:
        Dict with status of email send
    """
    current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    # Extract additional info
    order_id = additional_info.get('order_id', 'N/A') if additional_info else 'N/A'
    plan_id = additional_info.get('plan_id', 'N/A') if additional_info else 'N/A'
    user_id = additional_info.get('user_id', 'N/A') if additional_info else 'N/A'
    validity_weeks = additional_info.get('validity_weeks', 'N/A') if additional_info else 'N/A'
    scenarios = additional_info.get('scenarios', []) if additional_info else []
    
    # Birth details
    dob = additional_info.get('dob', 'Not provided') if additional_info else 'Not provided'
    tob = additional_info.get('tob', 'Not provided') if additional_info else 'Not provided'
    pob = additional_info.get('pob', 'Not provided') if additional_info else 'Not provided'
    gender = additional_info.get('gender', 'Not provided') if additional_info else 'Not provided'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>New Booking - NIRO</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #3E827A 0%, #5A9A92 100%); padding: 30px; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">🌟 New Booking Received!</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 14px;">{current_time}</p>
        </div>
        
        <div style="background: #f5f5f5; padding: 30px; border-radius: 0 0 10px 10px;">
            
            <!-- IDs Section -->
            <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #2e7d32; margin: 0 0 10px 0; font-size: 14px;">📋 Order & Plan IDs</h3>
                <p style="margin: 5px 0; font-size: 13px;"><strong>User ID:</strong> <code style="background: #fff; padding: 2px 6px; border-radius: 4px;">{user_id}</code></p>
                <p style="margin: 5px 0; font-size: 13px;"><strong>Order ID:</strong> <code style="background: #fff; padding: 2px 6px; border-radius: 4px;">{order_id}</code></p>
                <p style="margin: 5px 0; font-size: 13px;"><strong>Plan ID:</strong> <code style="background: #fff; padding: 2px 6px; border-radius: 4px;">{plan_id}</code></p>
            </div>
            
            <h2 style="color: #3E827A; margin-top: 0;">👤 Customer Details</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Name:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{user_name or 'Not provided'}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Email:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{user_email}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Phone:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{user_phone or 'Not provided'}</td>
                </tr>
            </table>
            
            <h2 style="color: #3E827A; margin-top: 30px;">🔒 Birth Details</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Date of Birth:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{dob}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Time of Birth:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{tob}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Place of Birth:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{pob}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Gender:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{gender}</td>
                </tr>
            </table>
            
            <h2 style="color: #3E827A; margin-top: 30px;">📦 Package Details</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Topic:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{topic_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Package:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{package_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Tier:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{package_tier}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Price:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong style="color: #2e7d32;">₹{package_price:,.0f}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Validity:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{validity_weeks} weeks</td>
                </tr>
            </table>
            
            {f'<div style="margin-top: 15px;"><strong>Selected Topics:</strong><ul style="margin: 5px 0;">' + ''.join([f'<li>{s}</li>' for s in scenarios]) + '</ul></div>' if scenarios else ''}
            
            <h2 style="color: #3E827A; margin-top: 30px;">💳 Payment Details</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Transaction ID:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><code style="background: #fff3e0; padding: 2px 6px; border-radius: 4px;">{transaction_id}</code></td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Payment Method:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{payment_method}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;"><strong>Date & Time:</strong></td>
                    <td style="padding: 10px 0; border-bottom: 1px solid #ddd;">{current_time}</td>
                </tr>
            </table>
            
            <div style="margin-top: 30px; padding: 15px; background: #fff3e0; border-radius: 8px; border-left: 4px solid #ff9800;">
                <p style="margin: 0; color: #e65100; font-size: 14px;">
                    <strong>⚡ Action Required:</strong> Please follow up with the customer to schedule their consultation session.
                </p>
            </div>
            
            <p style="margin-top: 20px; color: #666; font-size: 12px; text-align: center;">
                This is an automated notification from NIRO Astrology Platform.
            </p>
        </div>
    </body>
    </html>
    """
    
    subject = f"🌟 New Booking: {topic_name} - {package_tier} (₹{package_price:,.0f})"
    
    return await send_email(BOOKING_EMAIL, subject, html_content)
