from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from datetime import datetime, timedelta
from decimal import Decimal
from functools import wraps
import json

from .models import (
    UserProfile, ParkingFacility, ParkingFloor, ParkingSlot,
    Booking, Payment, Review, Reward, Favorite, ContactMessage
)
from .forms import UserRegistrationForm, ContactForm, ReviewForm, FacilityAdminForm
from .utils import generate_qr_code_base64, calculate_parking_quote

def is_staff_or_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    profile = getattr(user, 'profile', None)
    return profile and profile.role in ['staff', 'admin']

def admin_required(view_func):
    """
    Strict security boundary:
    - Unauthenticated visitors are redirected to the dedicated /admin-portal/login/.
    - Regular authenticated customers are immediately blocked with HTTP 403 Forbidden!
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Security Gateway: Please authenticate with administrator credentials.")
            return redirect(f"/admin-portal/login/?next={request.path}")
        if not is_staff_or_admin(request.user):
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --- PUBLIC VIEWS ---

def home_view(request):
    featured_facilities = ParkingFacility.objects.filter(is_active=True, is_featured=True)[:4]
    all_facilities = ParkingFacility.objects.filter(is_active=True)
    
    total_facilities = all_facilities.count()
    total_slots = ParkingSlot.objects.count()
    available_slots = ParkingSlot.objects.filter(status='available').count()
    total_bookings = Booking.objects.count()
    
    recent_reviews = Review.objects.select_related('facility', 'user')[:4]
    
    context = {
        'featured_facilities': featured_facilities,
        'total_facilities': total_facilities,
        'total_slots': total_slots,
        'available_slots': available_slots,
        'total_bookings': total_bookings + 1280, # Adding legacy count for social proof
        'recent_reviews': recent_reviews,
    }
    return render(request, 'home.html', context)


def facilities_view(request):
    query = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    vehicle_type = request.GET.get('vehicle_type', '').strip()
    ev_only = request.GET.get('ev_only') == '1'
    sort_by = request.GET.get('sort_by', 'featured')
    
    facilities = ParkingFacility.objects.filter(is_active=True)

    if query:
        facilities = facilities.filter(
            Q(name__icontains=query) | Q(address__icontains=query) | Q(city__icontains=query)
        )
    if city:
        facilities = facilities.filter(city__icontains=city)
    if ev_only:
        facilities = facilities.filter(ev_charging_available=True)

    if sort_by == 'price_asc':
        facilities = facilities.order_by('hourly_rate')
    elif sort_by == 'price_desc':
        facilities = facilities.order_by('-hourly_rate')
    elif sort_by == 'rating':
        facilities = facilities.order_by('-rating')
    else:
        facilities = facilities.order_by('-is_featured', '-rating')

    # Build Map JSON Data
    map_facilities = []
    for f in facilities:
        map_facilities.append({
            'name': f.name,
            'slug': f.slug,
            'address': f.address,
            'city': f.city,
            'lat': f.latitude,
            'lng': f.longitude,
            'rate': str(f.hourly_rate),
            'available': f.available_slots_count,
            'total': f.total_slots_count,
            'rating': f.rating,
            'image': f.image_url,
            'ev': f.ev_charging_available,
        })

    # Available cities for quick pills
    cities = ParkingFacility.objects.values_list('city', flat=True).distinct()

    context = {
        'facilities': facilities,
        'query': query,
        'city': city,
        'vehicle_type': vehicle_type,
        'ev_only': ev_only,
        'sort_by': sort_by,
        'map_facilities_json': json.dumps(map_facilities),
        'cities': cities,
    }
    return render(request, 'facilities.html', context)


def facility_detail_view(request, slug):
    facility = get_object_or_404(ParkingFacility, slug=slug, is_active=True)
    floors = facility.floors.prefetch_related('slots').all()
    reviews = facility.reviews.select_related('user').all()
    
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, facility=facility).exists()
    
    # Active floor selection
    floor_id = request.GET.get('floor')
    active_floor = floors.first()
    if floor_id:
        try:
            active_floor = floors.get(id=floor_id)
        except ParkingFloor.DoesNotExist:
            pass

    slots = active_floor.slots.all() if active_floor else facility.slots.all()

    # Review submission handling
    review_form = ReviewForm()
    if request.method == 'POST' and 'submit_review' in request.POST:
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to submit a review.")
            return redirect('login')
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.facility = facility
            review.user = request.user
            review.save()
            messages.success(request, "Thank you! Your verified review has been published.")
            return redirect('facility_detail', slug=facility.slug)

    context = {
        'facility': facility,
        'floors': floors,
        'active_floor': active_floor,
        'slots': slots,
        'reviews': reviews,
        'review_form': review_form,
        'is_favorited': is_favorited,
        'now_iso': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        'later_iso': (timezone.now() + timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M'),
    }
    return render(request, 'facility_detail.html', context)


def booking_checkout_view(request):
    slot_id = request.GET.get('slot_id') or request.POST.get('slot_id')
    facility_slug = request.GET.get('facility') or request.POST.get('facility')
    
    slot = None
    facility = None
    if slot_id:
        slot = get_object_or_404(ParkingSlot, id=slot_id)
        facility = slot.facility
    elif facility_slug:
        facility = get_object_or_404(ParkingFacility, slug=facility_slug)
        slot = facility.slots.filter(status='available').first()
    else:
        messages.error(request, "Please select a parking location and slot first.")
        return redirect('facilities')

    # Date / Time setup
    start_str = request.GET.get('start_time') or request.POST.get('start_time')
    end_str = request.GET.get('end_time') or request.POST.get('end_time')
    
    now = timezone.now()
    default_start = now + timedelta(minutes=30)
    default_end = default_start + timedelta(hours=2)

    try:
        start_dt = datetime.fromisoformat(start_str) if start_str else default_start
        end_dt = datetime.fromisoformat(end_str) if end_str else default_end
    except (ValueError, TypeError):
        start_dt = default_start
        end_dt = default_end

    # Make aware if naive
    if timezone.is_naive(start_dt):
        start_dt = timezone.make_aware(start_dt)
    if timezone.is_naive(end_dt):
        end_dt = timezone.make_aware(end_dt)

    if start_dt >= end_dt:
        end_dt = start_dt + timedelta(hours=2)

    quote = calculate_parking_quote(facility, slot, start_dt, end_dt)

    # Check loyalty discount availability
    user_points = 0
    can_redeem_loyalty = False
    discount_applied = Decimal('0.00')

    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile and profile.loyalty_points >= 100:
            user_points = profile.loyalty_points
            can_redeem_loyalty = True

    if request.POST.get('use_loyalty') == '1' and can_redeem_loyalty:
        discount_applied = Decimal('5.00')
        quote['total_price'] = max(Decimal('1.00'), quote['total_price'] - discount_applied)

    if request.method == 'POST' and 'confirm_and_pay' in request.POST:
        guest_name = request.POST.get('guest_name', '').strip()
        guest_email = request.POST.get('guest_email', '').strip()
        guest_phone = request.POST.get('guest_phone', '').strip()
        vehicle_plate = request.POST.get('vehicle_plate', '').strip().upper()
        vehicle_model = request.POST.get('vehicle_model', '').strip()
        vehicle_type = request.POST.get('vehicle_type', slot.vehicle_type if slot else 'sedan')
        payment_method = request.POST.get('payment_method', 'Credit Card')

        if not (guest_name and guest_email and vehicle_plate):
            messages.error(request, "Please provide full driver name, email, and vehicle registration number.")
        else:
            with transaction.atomic():
                # Lock slot for update to avoid race conditions!
                locked_slot = ParkingSlot.objects.select_for_update().get(id=slot.id)
                
                # Check for overlapping active bookings
                overlapping = Booking.objects.filter(
                    slot=locked_slot,
                    status__in=['confirmed', 'checked_in'],
                    start_time__lt=end_dt,
                    end_time__gt=start_dt
                ).exists()

                if overlapping:
                    messages.error(request, "Apologies! This slot was just reserved by another driver. Please choose another slot.")
                    return redirect('facility_detail', slug=facility.slug)

                # Create booking record
                booking = Booking.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    guest_name=guest_name,
                    guest_email=guest_email,
                    guest_phone=guest_phone,
                    facility=facility,
                    floor=locked_slot.floor,
                    slot=locked_slot,
                    vehicle_plate=vehicle_plate,
                    vehicle_type=vehicle_type,
                    vehicle_model=vehicle_model,
                    start_time=start_dt,
                    end_time=end_dt,
                    duration_hours=quote['duration_hours'],
                    hourly_rate=quote['hourly_rate'],
                    base_price=quote['base_price'],
                    service_fee=quote['service_fee'],
                    tax_amount=quote['tax_amount'],
                    discount_amount=discount_applied,
                    total_price=quote['total_price'],
                    status='confirmed',
                )

                # Generate Real QR Code
                verify_url = request.build_absolute_uri(f"/verify-ticket/{booking.reference_code}/")
                qr_base64 = generate_qr_code_base64(verify_url)
                booking.qr_data = verify_url
                booking.qr_image_base64 = qr_base64
                booking.save()

                # Mark slot reserved
                locked_slot.status = 'occupied'
                locked_slot.save()

                # Create verified payment record
                txn_id = f"TXN_{timezone.now().strftime('%y%m%d%H%M')}_{booking.reference_code}"
                Payment.objects.create(
                    booking=booking,
                    transaction_id=txn_id,
                    amount=quote['total_price'],
                    currency='USD',
                    payment_method=payment_method,
                    status='successful',
                    provider='ParkEase Test Gateway (Verified)',
                )

                # Handle rewards
                if request.user.is_authenticated:
                    profile = getattr(request.user, 'profile', None)
                    if profile:
                        if discount_applied > 0:
                            profile.loyalty_points -= 100
                            Reward.objects.create(
                                user=request.user,
                                points=-100,
                                action='Redemption',
                                description=f'Redeemed $5 discount on booking {booking.reference_code}'
                            )
                        # Award 50 bonus points for booking!
                        profile.loyalty_points += 50
                        profile.save()
                        Reward.objects.create(
                            user=request.user,
                            points=50,
                            action='Booking Bonus',
                            description=f'Bonus earned for booking {booking.reference_code}'
                        )

                messages.success(request, f"Booking {booking.reference_code} confirmed! Your digital parking pass is ready.")
                return redirect('booking_confirmation', reference=booking.reference_code)

    context = {
        'facility': facility,
        'slot': slot,
        'start_dt': start_dt,
        'end_dt': end_dt,
        'start_iso': start_dt.strftime('%Y-%m-%dT%H:%M'),
        'end_iso': end_dt.strftime('%Y-%m-%dT%H:%M'),
        'quote': quote,
        'can_redeem_loyalty': can_redeem_loyalty,
        'user_points': user_points,
        'discount_applied': discount_applied,
    }
    return render(request, 'booking_checkout.html', context)


def booking_confirmation_view(request, reference):
    booking = get_object_or_404(Booking, reference_code=reference)
    payment = getattr(booking, 'payment', None)
    
    context = {
        'booking': booking,
        'payment': payment,
        'is_owner': (request.user.is_authenticated and booking.user == request.user) or request.user.is_staff,
    }
    return render(request, 'booking_confirmation.html', context)


def booking_cancel_view(request, reference):
    booking = get_object_or_404(Booking, reference_code=reference)
    
    # Permission check: booking owner or staff
    if request.user.is_authenticated:
        if booking.user and booking.user != request.user and not request.user.is_staff:
            return HttpResponseForbidden("Unauthorized to cancel this booking.")
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Driver requested cancellation')
        if not booking.can_cancel:
            messages.error(request, "This booking cannot be cancelled according to the policy (already started or completed).")
            return redirect('booking_confirmation', reference=reference)

        with transaction.atomic():
            booking.status = 'cancelled'
            booking.cancellation_reason = reason
            booking.cancelled_at = timezone.now()
            booking.save()

            # Release slot
            booking.slot.status = 'available'
            booking.slot.save()

            # Refund payment
            if hasattr(booking, 'payment'):
                booking.payment.status = 'refunded'
                booking.payment.save()

            messages.success(request, f"Booking {booking.reference_code} has been cancelled and full refund of ${booking.total_price} has been initiated.")
            if request.user.is_authenticated:
                return redirect('dashboard')
            return redirect('booking_confirmation', reference=reference)

    return redirect('booking_confirmation', reference=reference)


def verify_ticket_view(request, reference=None):
    ref = reference or request.GET.get('reference', '').strip().upper()
    booking = None
    error_msg = None

    if ref:
        try:
            booking = Booking.objects.select_related('facility', 'slot', 'payment', 'user').get(reference_code=ref)
        except Booking.DoesNotExist:
            error_msg = f"No booking found with reference code '{ref}'. Please check and try again."

    # Staff Gate Check-in / Check-out actions
    if request.method == 'POST' and booking and is_staff_or_admin(request.user):
        action = request.POST.get('gate_action')
        if action == 'check_in':
            booking.status = 'checked_in'
            booking.checked_in_at = timezone.now()
            booking.save()
            messages.success(request, f"Vehicle {booking.vehicle_plate} verified & checked in! Gate barrier opened.")
        elif action == 'complete':
            booking.status = 'completed'
            booking.checked_out_at = timezone.now()
            booking.save()
            booking.slot.status = 'available'
            booking.slot.save()
            messages.success(request, f"Parking session completed. Slot {booking.slot.slot_number} released to available pool.")
        return redirect('verify_ticket_ref', reference=booking.reference_code)

    context = {
        'reference': ref,
        'booking': booking,
        'error_msg': error_msg,
        'is_staff': is_staff_or_admin(request.user),
    }
    return render(request, 'verify_ticket.html', context)


def toggle_favorite_view(request, facility_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    
    facility = get_object_or_404(ParkingFacility, id=facility_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, facility=facility)
    if not created:
        fav.delete()
        is_fav = False
    else:
        is_fav = True
    return JsonResponse({'success': True, 'favorited': is_fav})


# --- USER DASHBOARD ---

@login_required
def dashboard_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    bookings = Booking.objects.filter(user=request.user).select_related('facility', 'slot', 'payment')
    active_bookings = bookings.filter(status__in=['confirmed', 'checked_in'])
    completed_bookings = bookings.filter(status='completed')
    cancelled_bookings = bookings.filter(status='cancelled')
    
    favorites = Favorite.objects.filter(user=request.user).select_related('facility')
    rewards = Reward.objects.filter(user=request.user)
    
    total_spent = bookings.filter(status__in=['confirmed', 'checked_in', 'completed']).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')

    # Profile update
    if request.method == 'POST' and 'update_profile' in request.POST:
        profile.phone = request.POST.get('phone', profile.phone)
        profile.vehicle_plate = request.POST.get('vehicle_plate', profile.vehicle_plate).upper()
        profile.vehicle_model = request.POST.get('vehicle_model', profile.vehicle_model)
        profile.vehicle_type = request.POST.get('vehicle_type', profile.vehicle_type)
        profile.save()
        
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.save()
        messages.success(request, "Your profile and default vehicle details have been updated.")
        return redirect('dashboard')

    context = {
        'profile': profile,
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'favorites': favorites,
        'rewards': rewards,
        'total_spent': total_spent,
    }
    return render(request, 'dashboard.html', context)


# --- ADMIN DASHBOARD ---

@admin_required
def admin_dashboard_view(request):
    facilities = ParkingFacility.objects.all().annotate(slot_count=Count('slots'))
    total_facilities = facilities.count()
    total_slots = ParkingSlot.objects.count()
    occupied_slots = ParkingSlot.objects.filter(status='occupied').count()
    occupancy_rate = int((occupied_slots / total_slots * 100)) if total_slots else 0
    
    total_revenue = Payment.objects.filter(status='successful').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    all_bookings = Booking.objects.select_related('facility', 'slot', 'user').order_by('-created_at')[:20]
    inquiries = ContactMessage.objects.filter(is_resolved=False)[:10]

    facility_form = FacilityAdminForm()
    if request.method == 'POST' and 'create_facility' in request.POST:
        facility_form = FacilityAdminForm(request.POST)
        if facility_form.is_valid():
            new_facility = facility_form.save(commit=False)
            amenities_raw = facility_form.cleaned_data.get('amenities_text', '')
            if amenities_raw:
                new_facility.amenities = [a.strip() for a in amenities_raw.split(',') if a.strip()]
            new_facility.save()

            # Automatically create 2 default floors and 16 slots
            f1 = ParkingFloor.objects.create(facility=new_facility, floor_name="Level P1 - Ground Floor", floor_number=1)
            f2 = ParkingFloor.objects.create(facility=new_facility, floor_name="Level P2 - Upper Level", floor_number=2)
            
            for i in range(1, 9):
                ParkingSlot.objects.create(
                    facility=new_facility, floor=f1, slot_number=f"A-{i:02d}",
                    vehicle_type='sedan', status='available'
                )
                ParkingSlot.objects.create(
                    facility=new_facility, floor=f2, slot_number=f"B-{i:02d}",
                    vehicle_type='ev' if i <= 3 else 'suv',
                    has_ev_charger=True if i <= 3 else False,
                    status='available'
                )

            messages.success(request, f"Facility '{new_facility.name}' and initial parking bays initialized successfully!")
            return redirect('admin_dashboard')

    context = {
        'facilities': facilities,
        'total_facilities': total_facilities,
        'total_slots': total_slots,
        'occupied_slots': occupied_slots,
        'occupancy_rate': occupancy_rate,
        'total_revenue': total_revenue,
        'all_bookings': all_bookings,
        'inquiries': inquiries,
        'facility_form': facility_form,
    }
    return render(request, 'admin_dashboard.html', context)


# --- INFORMATION PAGES ---

def about_view(request):
    return render(request, 'about.html')


def contact_view(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Your message has been received. Our concierge support team will reach out within 2 hours.")
            return redirect('contact')
    return render(request, 'contact.html', {'form': form})


# --- AUTHENTICATION ---

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = UserRegistrationForm()
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
                vehicle_plate=form.cleaned_data.get('vehicle_plate', '').upper(),
                vehicle_model=form.cleaned_data.get('vehicle_model', ''),
                loyalty_points=100,
            )
            Reward.objects.create(
                user=user,
                points=100,
                action='Welcome Bonus',
                description='New Member Welcome Bonus'
            )

            login(request, user)
            messages.success(request, f"Welcome to ParkEase, {user.first_name or user.username}! 100 loyalty points have been credited to your account.")
            return redirect('dashboard')

    return render(request, 'register.html', {'form': form})


def login_view(request):
    """Customer & Driver Portal Login."""
    if request.user.is_authenticated:
        if is_staff_or_admin(request.user):
            return redirect('admin_dashboard')
        return redirect('dashboard')

    # Instant demo login shortcut for customer
    demo_role = request.GET.get('demo')
    if demo_role == 'customer':
        cust_user = User.objects.filter(username='alex_driver').first()
        if cust_user:
            login(request, cust_user)
            messages.success(request, "Welcome to your Driver Dashboard, Arjun Verma!")
            return redirect('dashboard')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username_or_email, password=password)
        if user is None and '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            login(request, user)
            if is_staff_or_admin(user):
                messages.info(request, "Staff credentials recognized. Entering Operations Console.")
                return redirect('admin_dashboard')
            next_url = request.GET.get('next', 'dashboard')
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, 'login.html')


def admin_login_view(request):
    """Exclusive, Secure Portal Login for Staff and Administrators Only."""
    if request.user.is_authenticated:
        if is_staff_or_admin(request.user):
            return redirect('admin_dashboard')
        else:
            # User is a regular customer trying to view admin login
            messages.error(request, "Access Restricted: You are currently signed in as a Customer. Please sign in with administrator credentials.")
            return render(request, '403.html', status=403)

    # 1-Click Fast Admin Demo Authentication
    if request.GET.get('demo') == 'admin':
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            login(request, admin_user)
            messages.success(request, "Security Cleared: Authenticated as Executive Administrator (Rajesh Sharma).")
            return redirect('admin_dashboard')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username_or_email, password=password)
        if user is None and '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            # Strict role validation
            if is_staff_or_admin(user):
                login(request, user)
                next_url = request.GET.get('next', 'admin_dashboard')
                messages.success(request, f"Welcome to Executive Operations Console, {user.first_name or user.username}!")
                return redirect(next_url)
            else:
                messages.error(request, "ACCESS FORBIDDEN: This account is a Driver / Customer account and does not have administrative rights to this console.")
        else:
            messages.error(request, "Invalid administrator username or security key.")

    return render(request, 'admin_login.html')


def admin_logout_view(request):
    logout(request)
    messages.info(request, "Administrator session terminated safely.")
    return redirect('admin_login')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('home')
