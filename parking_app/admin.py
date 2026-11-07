from django.contrib import admin
from .models import (
    UserProfile, ParkingFacility, ParkingFloor, ParkingSlot,
    Booking, Payment, Review, Reward, Favorite, ContactMessage
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'vehicle_plate', 'loyalty_points')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'vehicle_plate')

class ParkingSlotInline(admin.TabularInline):
    model = ParkingSlot
    extra = 1

class ParkingFloorInline(admin.TabularInline):
    model = ParkingFloor
    extra = 1

@admin.register(ParkingFacility)
class ParkingFacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'hourly_rate', 'daily_rate', 'is_active', 'is_featured', 'ev_charging_available')
    list_filter = ('city', 'is_active', 'is_featured', 'ev_charging_available')
    search_fields = ('name', 'city', 'address')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ParkingFloorInline]

@admin.register(ParkingFloor)
class ParkingFloorAdmin(admin.ModelAdmin):
    list_display = ('facility', 'floor_name', 'floor_number')
    list_filter = ('facility',)
    inlines = [ParkingSlotInline]

@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('slot_number', 'facility', 'floor', 'vehicle_type', 'status', 'has_ev_charger', 'is_handicap')
    list_filter = ('status', 'vehicle_type', 'has_ev_charger', 'is_handicap', 'facility')
    search_fields = ('slot_number', 'facility__name')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('reference_code', 'guest_name', 'facility', 'slot', 'vehicle_plate', 'start_time', 'total_price', 'status')
    list_filter = ('status', 'facility', 'created_at')
    search_fields = ('reference_code', 'guest_name', 'guest_email', 'vehicle_plate')
    readonly_fields = ('reference_code', 'created_at', 'updated_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'booking', 'amount', 'currency', 'payment_method', 'status', 'paid_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('transaction_id', 'booking__reference_code')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('facility', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'facility')

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'action', 'description', 'created_at')
    list_filter = ('action',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
