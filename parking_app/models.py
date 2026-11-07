from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import random
import string

def generate_booking_reference():
    digits = ''.join(random.choices(string.digits, k=6))
    return f"PK-{digits}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('staff', 'Parking Staff / Operator'),
        ('admin', 'Administrator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    vehicle_plate = models.CharField(max_length=20, blank=True)
    vehicle_model = models.CharField(max_length=50, blank=True)
    vehicle_type = models.CharField(max_length=20, default='sedan')
    loyalty_points = models.IntegerField(default=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def loyalty_tier(self):
        if self.loyalty_points >= 500:
            return "Gold Member"
        elif self.loyalty_points >= 200:
            return "Silver Member"
        return "Classic Member"


class ParkingFacility(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=150, unique=True)
    tagline = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.FloatField(default=40.7128)
    longitude = models.FloatField(default=-74.0060)
    
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, default=5.00)
    daily_rate = models.DecimalField(max_digits=6, decimal_places=2, default=35.00)
    currency = models.CharField(max_length=5, default='$')
    
    image_url = models.URLField(max_length=500, blank=True)
    gallery_images = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    
    is_24_7 = models.BooleanField(default=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    rating = models.FloatField(default=4.8)
    review_count = models.IntegerField(default=24)
    
    amenities = models.JSONField(default=list, blank=True)
    ev_charging_available = models.BooleanField(default=True)
    ev_charger_types = models.CharField(max_length=100, default="Type 2 & CCS2 Fast Charge")
    cancellation_hours_before = models.IntegerField(default=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Parking Facilities"
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return f"{self.name} - {self.city}"

    @property
    def total_slots_count(self):
        return self.slots.count()

    @property
    def available_slots_count(self):
        return self.slots.filter(status='available').count()

    @property
    def occupancy_percentage(self):
        total = self.total_slots_count
        if total == 0:
            return 0
        occupied = total - self.available_slots_count
        return int((occupied / total) * 100)


class ParkingFloor(models.Model):
    facility = models.ForeignKey(ParkingFacility, on_delete=models.CASCADE, related_name='floors')
    floor_name = models.CharField(max_length=50) # e.g. "Ground Level (P1)"
    floor_number = models.IntegerField(default=1)

    class Meta:
        ordering = ['floor_number']

    def __str__(self):
        return f"{self.facility.name} - {self.floor_name}"


class ParkingSlot(models.Model):
    VEHICLE_TYPES = [
        ('compact', 'Compact / Hatchback'),
        ('sedan', 'Standard Sedan'),
        ('suv', 'SUV / Luxury 4x4'),
        ('ev', 'Electric Vehicle (EV)'),
        ('motorcycle', 'Motorcycle / Scooter'),
        ('handicap', 'Accessible / Handicap'),
    ]

    SLOT_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Maintenance'),
    ]

    facility = models.ForeignKey(ParkingFacility, on_delete=models.CASCADE, related_name='slots')
    floor = models.ForeignKey(ParkingFloor, on_delete=models.SET_NULL, null=True, blank=True, related_name='slots')
    slot_number = models.CharField(max_length=15)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='sedan')
    has_ev_charger = models.BooleanField(default=False)
    is_handicap = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=SLOT_STATUS, default='available')
    price_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)

    class Meta:
        ordering = ['slot_number']
        unique_together = ('facility', 'slot_number')

    def __str__(self):
        return f"{self.slot_number} ({self.facility.name})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed & Paid'),
        ('checked_in', 'Checked In (Parked)'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled & Refunded'),
    ]

    reference_code = models.CharField(max_length=20, unique=True, default=generate_booking_reference, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    # Guest / Driver info
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)
    
    facility = models.ForeignKey(ParkingFacility, on_delete=models.CASCADE, related_name='bookings')
    floor = models.ForeignKey(ParkingFloor, on_delete=models.SET_NULL, null=True, blank=True)
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='bookings')
    
    vehicle_plate = models.CharField(max_length=25)
    vehicle_type = models.CharField(max_length=30, default='sedan')
    vehicle_model = models.CharField(max_length=60, blank=True)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_hours = models.FloatField(default=2.0)
    
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    service_fee = models.DecimalField(max_digits=6, decimal_places=2, default=1.50)
    tax_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    qr_data = models.TextField(blank=True)
    qr_image_base64 = models.TextField(blank=True)
    
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_code} - {self.guest_name} ({self.facility.name})"

    @property
    def is_active(self):
        return self.status in ['confirmed', 'checked_in']

    @property
    def get_vehicle_type_display(self):
        type_map = {
            'compact': 'Compact / Hatchback',
            'sedan': 'Standard Sedan',
            'suv': 'SUV / Luxury 4x4',
            'ev': 'Electric Vehicle (EV)',
            'motorcycle': 'Motorcycle / Scooter',
            'handicap': 'Accessible / Handicap',
        }
        return type_map.get(self.vehicle_type, self.vehicle_type.title() if self.vehicle_type else 'Sedan')

    @property
    def can_cancel(self):
        if self.status != 'confirmed':
            return False
        # Allow cancellation if current time is before start time or within reasonable window
        return timezone.now() < self.start_time


class Payment(models.Model):
    STATUS_CHOICES = [
        ('successful', 'Successful'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    payment_method = models.CharField(max_length=30, default='Credit/Debit Card')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='successful')
    provider = models.CharField(max_length=50, default='ParkEase Secure Pay (Demo/Razorpay Test)')
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - ${self.amount} ({self.status})"


class Review(models.Model):
    facility = models.ForeignKey(ParkingFacility, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.facility.name} ({self.rating}★)"


class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    points = models.IntegerField()
    action = models.CharField(max_length=50) # 'Booking Bonus', 'Redemption', 'Welcome Bonus'
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.points:+d} ({self.action})"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    facility = models.ForeignKey(ParkingFacility, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'facility')

    def __str__(self):
        return f"{self.user.username} -> {self.facility.name}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Msg from {self.name} - {self.subject}"
