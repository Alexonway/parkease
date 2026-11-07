from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

from parking_app.models import (
    UserProfile, ParkingFacility, ParkingFloor, ParkingSlot,
    Booking, Payment, Review, Reward, Favorite, ContactMessage
)
from parking_app.utils import generate_qr_code_base64

class Command(BaseCommand):
    help = 'Seeds realistic Indian parking facilities (Delhi, UP, Haryana: Malls, Hospitals, Railway, Airports).'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Indian locations (Delhi, UP, Haryana) into database...")

        # 1. Create / Update Users
        admin_user, _ = User.objects.get_or_create(username='admin')
        admin_user.first_name = 'Rajesh'
        admin_user.last_name = 'Sharma'
        admin_user.email = 'admin@parkease.in'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('Admin123!')
        admin_user.save()
        UserProfile.objects.update_or_create(
            user=admin_user,
            defaults={
                'phone': '+91 98110 23456',
                'role': 'admin',
                'loyalty_points': 1500,
            }
        )

        customer_user, _ = User.objects.get_or_create(username='alex_driver')
        customer_user.first_name = 'Arjun'
        customer_user.last_name = 'Verma'
        customer_user.email = 'arjun.verma@example.in'
        customer_user.set_password('Password123!')
        customer_user.save()
        UserProfile.objects.update_or_create(
            user=customer_user,
            defaults={
                'phone': '+91 98765 43210',
                'vehicle_plate': 'DL-01-CZ-7842',
                'vehicle_model': 'Tata Nexon EV Max',
                'vehicle_type': 'ev',
                'role': 'customer',
                'loyalty_points': 450,
            }
        )

        # 2. Indian Facilities Across Delhi, UP, and Haryana (Airport, Mall, Hospital, Railway, Corporate Hubs)
        facilities_data = [
            # 1. AIRPORT - Delhi
            {
                'name': 'IGI Airport Terminal 3 SkyPark Multi-Level Car Parking (MLCP)',
                'slug': 'igi-airport-t3-skypark',
                'tagline': 'World-class 24/7 multi-level terminal parking with direct skywalk to T3 departures.',
                'address': 'Terminal 3, Indira Gandhi International Airport, Palam',
                'city': 'New Delhi (Delhi)',
                'postal_code': '110037',
                'latitude': 28.5562,
                'longitude': 77.1000,
                'hourly_rate': Decimal('100.00'),
                'daily_rate': Decimal('600.00'),
                'image_url': 'https://images.unsplash.com/photo-1506521781263-d8422e82f27a?auto=format&fit=crop&w=1200&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1506521781263-d8422e82f27a?auto=format&fit=crop&w=1200&q=80',
                    'https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?auto=format&fit=crop&w=1200&q=80',
                ],
                'description': 'The official multi-level automated facility for Delhi International Airport Terminal 3. Equipped with automated number plate recognition (ANPR), flight information display screens, 24/7 CISF security surveillance, and fast EV superchargers.',
                'is_24_7': True,
                'is_featured': True,
                'rating': 4.9,
                'review_count': 428,
                'amenities': ['Direct Skywalk to T3', '24/7 CISF Security Patrol', 'Flight Status Screens', '60kW Fast DC EV Chargers', 'Baggage Trolleys Available', 'Wheelchair Assistance'],
                'ev_charging_available': True,
                'ev_charger_types': 'CCS2 & Bharat DC-001 (60 kW Fast Charge)',
            },
            # 2. MALL - Noida (UP)
            {
                'name': 'DLF Mall of India Smart Multi-Deck Garage',
                'slug': 'dlf-mall-of-india-noida',
                'tagline': 'Indias largest mall parking deck with automated bay guidance and valet.',
                'address': 'Sector 18, Noida Express Highway, Gautam Buddha Nagar',
                'city': 'Noida (UP)',
                'postal_code': '201301',
                'latitude': 28.5677,
                'longitude': 77.3211,
                'hourly_rate': Decimal('50.00'),
                'daily_rate': Decimal('280.00'),
                'image_url': 'https://images.unsplash.com/photo-1590674899484-d5640e854abe?auto=format&fit=crop&w=1200&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1590674899484-d5640e854abe?auto=format&fit=crop&w=1200&q=80',
                ],
                'description': 'A massive 7-tier multi-level parking facility situated at Sector 18 Noida. Features real-time floor availability indicators, premium valet services, direct escalator connectivity into fashion courts, and fast EV chargers.',
                'is_24_7': False,
                'is_featured': True,
                'rating': 4.8,
                'review_count': 356,
                'amenities': ['7-Level Covered Garage', 'Direct Escalator Access to Mall', 'Tata Power EV Fast Hub', 'Premium Valet Parking', 'CCTV High-Definition', 'Spacious SUV Bays'],
                'ev_charging_available': True,
                'ev_charger_types': 'Tata Power EZ Charge (CCS2 & Type 2)',
            },
            # 3. MALL - Saket, Delhi
            {
                'name': 'Select CITYWALK & DLF Avenue Underground Deck',
                'slug': 'select-citywalk-saket',
                'tagline': 'Luxury underground shopping and dining parking in South Delhi.',
                'address': 'A-3, District Centre, Saket, South Delhi',
                'city': 'South Delhi (Delhi)',
                'postal_code': '110017',
                'latitude': 28.5284,
                'longitude': 77.2185,
                'hourly_rate': Decimal('60.00'),
                'daily_rate': Decimal('350.00'),
                'image_url': 'https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=80',
                ],
                'description': 'Underground climate-controlled executive parking serving the premier shopping district of South Delhi. High-clearance bays, 24/7 security marshals, optical QR barrier gates, and complimentary battery jump assistance.',
                'is_24_7': True,
                'is_featured': True,
                'rating': 4.9,
                'review_count': 289,
                'amenities': ['Climate Controlled Bays', 'Contactless QR Boom Gates', 'Executive Valet Service', 'EV Superchargers', 'Wheelchair Friendly Elevators'],
                'ev_charging_available': True,
                'ev_charger_types': 'Statiq & Kazam (CCS2 & AC Type 2)',
            },
            # 4. HOSPITAL - Delhi
            {
                'name': 'AIIMS New Delhi Emergency & OPD Multi-Level Facility',
                'slug': 'aiims-new-delhi-parking',
                'tagline': 'Dedicated priority medical parking with stretcher-friendly elevator bays.',
                'address': 'Sri Aurobindo Marg, Ansari Nagar East, New Delhi',
                'city': 'New Delhi (Delhi)',
                'postal_code': '110029',
                'latitude': 28.5672,
                'longitude': 77.2100,
                'hourly_rate': Decimal('30.00'),
                'daily_rate': Decimal('180.00'),
                'image_url': 'https://images.unsplash.com/photo-1573348722427-f1d6819fdf98?auto=format&fit=crop&w=1200&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1573348722427-f1d6819fdf98?auto=format&fit=crop&w=1200&q=80',
                ],
                'description': 'Designed specifically for patients, doctors, and visitors at the premier All India Institute of Medical Sciences. Clear ambulance corridors, priority handicap access bays, 24/7 security assistance, and immediate emergency clinic access.',
                'is_24_7': True,
                'is_featured': True,
                'rating': 4.7,
                'review_count': 512,
                'amenities': ['24/7 Emergency Priority Clearance', 'Ambulance Free Corridor', 'Direct OPD Ramps', 'Stretcher Accessible Elevators', 'Guarded Round-the-Clock'],
                'ev_charging_available': False,
                'ev_charger_types': 'None',
            },
            # 5. HOSPITAL - Gurugram (Haryana)
            {
                'name': 'Medanta The Medicity Super-Specialty Hospital Deck',
                'slug': 'medanta-the-medicity-gurugram',
                'tagline': 'Hassle-free sheltered hospital parking right by the main admission lobby.',
                'address': 'CH Bakhtawar Singh Road, Sector 38, Gurugram',
                'city': 'Gurugram (Haryana)',
                'postal_code': '122001',
                'latitude': 28.4393,
                'longitude': 77.0425,
                'hourly_rate': Decimal('40.00'),
                'daily_rate': Decimal('220.00'),
                'image_url': 'https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=1200&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=1200&q=80',
                ],
                'description': 'Multi-story modern car parking facility adjacent to Medanta hospital towers. Dedicated patient drop-off lanes, golf-cart transfer shuttles for senior citizens, and quick automated boom barrier exit.',
                'is_24_7': True,
                'is_featured': False,
                'rating': 4.8,
                'review_count': 195,
                'amenities': ['Senior Citizen Buggy Shuttle', 'Covered Multi-Story Shelter', 'Emergency Wheelchairs', '24/7 Patient Concierge', 'Spacious Bays'],
                'ev_charging_available': True,
                'ev_charger_types': 'Jio-bp Pulse (CCS2 50kW)',
            },
            # 6. RAILWAY STATION - Delhi
            {
                'name': 'New Delhi Railway Station (NDLS) Ajmeri Gate Executive Parking',
                'slug': 'ndls-ajmeri-gate-parking',
                'tagline': 'Guaranteed rail commuter parking steps away from Platform 16 and Airport Express Metro.',
                'address': 'Bhavbhuti Marg, Ajmeri Gate Side, New Delhi Railway Station',
                'city': 'Central Delhi (Delhi)',
                'postal_code': '110006',
                'latitude': 28.6415,
                'longitude': 77.2210,
                'hourly_rate': Decimal('40.00'),
                'daily_rate': Decimal('240.00'),
                'image_url': 'https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?auto=format&fit=crop&w=1200&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?auto=format&fit=crop&w=1200&q=80',
                ],
                'description': 'Strategically situated on the Ajmeri Gate side of New Delhi Railway Station, providing direct foot-over-bridge access to all 16 platforms and the Orange Line Airport Express Metro. Safe overnight stay with 24/7 security guards.',
                'is_24_7': True,
                'is_featured': True,
                'rating': 4.6,
                'review_count': 640,
                'amenities': ['Direct Foot-Over-Bridge to Platforms', 'Airport Express Metro Link', '24/7 Gated Perimeter', 'Pre-paid Coolie & Porter Counter', 'Overnight Security'],
                'ev_charging_available': True,
                'ev_charger_types': 'EESL Multi-Standard Fast Charger',
            },
            # 7. CORPORATE & DINING - Gurugram (Haryana)
            {
                'name': 'DLF Cyber Hub & Cyber City Automated Executive Deck',
                'slug': 'dlf-cyber-hub-gurugram',
                'tagline': 'Premium corporate hub and fine dining parking with 150kW hyper-chargers.',
                'address': 'DLF Cyber City, Phase 2, Sector 24, Gurugram',
                'city': 'Gurugram (Haryana)',
                'postal_code': '122002',
                'latitude': 28.4950,
                'longitude': 77.0895,
                'hourly_rate': Decimal('60.00'),
                'daily_rate': Decimal('380.00'),
                'image_url': 'https://images.unsplash.com/photo-1558441719-f90351336140?auto=format&fit=crop&w=1200&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1558441719-f90351336140?auto=format&fit=crop&w=1200&q=80',
                ],
                'description': 'The premier commercial hub of Millennium City. Accommodating executive sedans and electric vehicles with dual-gun 150kW DC hyperchargers, Rapid Metro footbridge integration, and cashless FASTag / QR boom gates.',
                'is_24_7': True,
                'is_featured': True,
                'rating': 4.9,
                'review_count': 382,
                'amenities': ['150kW Hyper-Fast EV Hub', 'Rapid Metro Integrated Bridge', 'ANPR Fastag & QR Pass Gate', 'Valet Assistance', '24/7 Corporate Security'],
                'ev_charging_available': True,
                'ev_charger_types': 'Jio-bp & Fortum (150kW Dual Gun CCS2)',
            },
            # 8. TRANSIT / RAILWAY - Anand Vihar Mega Rail Terminal (Delhi / UP Border)
            {
                'name': 'Anand Vihar Mega Rail & ISBT Transit Terminal Deck',
                'slug': 'anand-vihar-transit-terminal',
                'tagline': 'Integrated eastern gateway parking linking Vande Bharat trains, Blue Line Metro & ISBT.',
                'address': 'Anand Vihar Railway Station Complex, Kaushambi Border',
                'city': 'East Delhi (Delhi)',
                'postal_code': '110092',
                'latitude': 28.6502,
                'longitude': 77.3155,
                'hourly_rate': Decimal('35.00'),
                'daily_rate': Decimal('200.00'),
                'image_url': 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=1200&q=80',
                'gallery_images': [
                    'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=1200&q=80',
                ],
                'description': 'Multi-modal transit parking connecting East Delhi, Ghaziabad, and Noida commuters. Provides sheltered parking bays for both two-wheelers and four-wheelers catching long-distance trains or interstate buses.',
                'is_24_7': True,
                'is_featured': False,
                'rating': 4.7,
                'review_count': 275,
                'amenities': ['Direct Railway Station Access', 'Metro Blue & Pink Line Connection', '24/7 Guarded Guardhouse', 'Two-Wheeler & Four-Wheeler Zones', 'Touchless Payment'],
                'ev_charging_available': True,
                'ev_charger_types': 'Tata Power EZ Charge (CCS2)',
            },
        ]

        # 3. Clean up non-Indian facilities and create Indian Facilities, Floors, and Slots
        indian_slugs = [f['slug'] for f in facilities_data]
        ParkingFacility.objects.exclude(slug__in=indian_slugs).delete()

        for fac_data in facilities_data:
            facility, created = ParkingFacility.objects.update_or_create(
                slug=fac_data['slug'],
                defaults=fac_data
            )

            # Floors: Level 1 (Ground), Level 2 (Upper Deck & EV), Level 3 (Sky Terrace)
            floors_config = [
                ('Level P1 - Ground Floor', 1, 12),
                ('Level P2 - Upper Deck & EV', 2, 10),
                ('Level P3 - Sky Terrace', 3, 8),
            ]

            for floor_name, floor_num, slot_count in floors_config:
                floor, _ = ParkingFloor.objects.get_or_create(
                    facility=facility,
                    floor_name=floor_name,
                    defaults={'floor_number': floor_num}
                )

                # Generate slots
                prefix_map = {1: 'A', 2: 'B', 3: 'C'}
                prefix = prefix_map.get(floor_num, 'S')

                for i in range(1, slot_count + 1):
                    slot_num = f"{prefix}-{i:02d}"
                    
                    # Distribute vehicle types
                    if i in [1, 2]:
                        v_type = 'handicap'
                        is_handicap = True
                        has_ev = False
                        mult = Decimal('1.00')
                    elif i in [3, 4, 5] and facility.ev_charging_available:
                        v_type = 'ev'
                        has_ev = True
                        is_handicap = False
                        mult = Decimal('1.20')
                    elif i in [6, 7]:
                        v_type = 'suv'
                        has_ev = False
                        is_handicap = False
                        mult = Decimal('1.15')
                    elif i == slot_count:
                        v_type = 'motorcycle'
                        has_ev = False
                        is_handicap = False
                        mult = Decimal('0.70')
                    else:
                        v_type = 'sedan'
                        has_ev = False
                        is_handicap = False
                        mult = Decimal('1.00')

                    # Some slots occupied for realistic live preview
                    status = 'occupied' if i in [2, 5, 8] else 'available'

                    ParkingSlot.objects.update_or_create(
                        facility=facility,
                        slot_number=slot_num,
                        defaults={
                            'floor': floor,
                            'vehicle_type': v_type,
                            'has_ev_charger': has_ev,
                            'is_handicap': is_handicap,
                            'status': status,
                            'price_multiplier': mult,
                        }
                    )

            # Add sample reviews
            sample_reviews = [
                (customer_user, 5, "Remarkably clean and organized facility. The digital QR pass worked instantly at the boom barrier gate!"),
                (admin_user, 5, "Seamless booking experience and top-tier fast EV charging. Truly frictionless parking."),
            ]
            for user, rating, comment in sample_reviews:
                Review.objects.get_or_create(
                    facility=facility,
                    user=user,
                    defaults={'rating': rating, 'comment': comment}
                )

        # 4. Create an active demo booking for Arjun
        first_facility = ParkingFacility.objects.get(slug='igi-airport-t3-skypark')
        booked_slot = first_facility.slots.filter(vehicle_type='ev', status='available').first()
        if not booked_slot:
            booked_slot = first_facility.slots.first()

        now = timezone.now()
        start_t = now + timedelta(hours=1)
        end_t = start_t + timedelta(hours=3)

        booking_ref = "PK-892401"
        qr_url = f"http://127.0.0.1:8000/verify-ticket/{booking_ref}/"
        qr_base64 = generate_qr_code_base64(qr_url)

        booking, _ = Booking.objects.update_or_create(
            reference_code=booking_ref,
            defaults={
                'user': customer_user,
                'guest_name': 'Arjun Verma',
                'guest_email': 'arjun.verma@example.in',
                'guest_phone': '+91 98765 43210',
                'facility': first_facility,
                'floor': booked_slot.floor,
                'slot': booked_slot,
                'vehicle_plate': 'DL-01-CZ-7842',
                'vehicle_type': 'ev',
                'vehicle_model': 'Tata Nexon EV Max',
                'start_time': start_t,
                'end_time': end_t,
                'duration_hours': 3.0,
                'hourly_rate': first_facility.hourly_rate * booked_slot.price_multiplier,
                'base_price': Decimal('360.00'),
                'service_fee': Decimal('15.00'),
                'tax_amount': Decimal('30.00'),
                'discount_amount': Decimal('50.00'),
                'total_price': Decimal('355.00'),
                'status': 'confirmed',
                'qr_data': qr_url,
                'qr_image_base64': qr_base64,
            }
        )

        Payment.objects.update_or_create(
            booking=booking,
            defaults={
                'transaction_id': 'TXN_UPI_99481237IND',
                'amount': Decimal('355.00'),
                'currency': 'INR',
                'payment_method': 'UPI / NetBanking (Verified Demo)',
                'status': 'successful',
                'provider': 'ParkEase Pay India (Test Mode)',
            }
        )

        Reward.objects.get_or_create(
            user=customer_user,
            points=100,
            action='Welcome Bonus',
            description='Welcome to ParkEase Mobility Club',
        )
        Reward.objects.get_or_create(
            user=customer_user,
            points=50,
            action='Booking Reward',
            description='Booking completed at IGI Airport T3 SkyPark',
        )

        Favorite.objects.get_or_create(
            user=customer_user,
            facility=first_facility,
        )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with Indian locations (Delhi, UP, Haryana: Airport, Malls, Hospitals, Railway)!"))
