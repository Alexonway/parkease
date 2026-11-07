import qrcode
import io
import base64
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

def generate_qr_code_base64(data_text):
    """Generates a high-quality QR code as a base64 encoded PNG data URI."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(data_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#064e3b", back_color="#ffffff")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def calculate_parking_quote(facility, slot, start_dt, end_dt):
    """
    Server-side price calculation:
    - Duration in hours (minimum 1 hour)
    - Base rate * multiplier * hours
    - Service fee ($1.50)
    - Sales/City tax (8%)
    """
    if start_dt >= end_dt:
        end_dt = start_dt + timedelta(hours=2)
    
    duration_seconds = (end_dt - start_dt).total_seconds()
    duration_hours = max(1.0, round(duration_seconds / 3600.0, 1))
    
    hourly_rate = facility.hourly_rate * (slot.price_multiplier if slot else Decimal('1.00'))
    base_price = round(Decimal(str(duration_hours)) * hourly_rate, 2)
    
    service_fee = Decimal('1.50')
    tax_amount = round((base_price + service_fee) * Decimal('0.08'), 2)
    total_price = base_price + service_fee + tax_amount
    
    return {
        'duration_hours': duration_hours,
        'hourly_rate': hourly_rate,
        'base_price': base_price,
        'service_fee': service_fee,
        'tax_amount': tax_amount,
        'total_price': total_price,
    }
