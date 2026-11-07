from django.conf import settings

def brand_context(request):
    return {
        'BRAND_NAME': getattr(settings, 'BRAND_NAME', 'ParkEase'),
        'BRAND_TAGLINE': getattr(settings, 'BRAND_TAGLINE', 'Find a space. Book ahead. Arrive relaxed.'),
        'DEMO_PAYMENT_MODE': getattr(settings, 'DEMO_PAYMENT_MODE', True),
        'CURRENCY_SYMBOL': getattr(settings, 'CURRENCY_SYMBOL', '$'),
    }
