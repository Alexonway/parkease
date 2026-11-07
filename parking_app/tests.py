from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from parking_app.models import (
    ParkingFacility, ParkingFloor, ParkingSlot, Booking, Payment, UserProfile, ContactMessage
)
from parking_app.utils import calculate_parking_quote, generate_qr_code_base64

class ParkingSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Facility
        self.facility = ParkingFacility.objects.create(
            name="Test Indian MLCP Hub",
            slug="test-indian-mlcp",
            address="100 Barakhamba Road",
            city="New Delhi (Delhi)",
            hourly_rate=Decimal("50.00"),
            daily_rate=Decimal("300.00"),
            ev_charging_available=True,
            is_active=True,
        )

        self.floor = ParkingFloor.objects.create(
            facility=self.facility,
            floor_name="Ground P1",
            floor_number=1,
        )

        self.slot = ParkingSlot.objects.create(
            facility=self.facility,
            floor=self.floor,
            slot_number="A-01",
            vehicle_type="ev",
            has_ev_charger=True,
            status="available",
            price_multiplier=Decimal("1.00"),
        )

        self.user = User.objects.create_user(
            username="testdriver",
            email="driver@example.com",
            password="TestPassword123!"
        )
        self.profile = UserProfile.objects.create(user=self.user, role="customer")

        self.admin = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="AdminPassword123!"
        )
        self.admin_profile = UserProfile.objects.create(user=self.admin, role="admin")

    def test_quote_calculation(self):
        start = timezone.now()
        end = start + timedelta(hours=3)
        quote = calculate_parking_quote(self.facility, self.slot, start, end)
        
        # 3 hours * 50 = 150 base + 1.50 service fee + 8% tax (12.12) = 163.62
        self.assertEqual(quote['duration_hours'], 3.0)
        self.assertEqual(quote['base_price'], Decimal('150.00'))
        self.assertEqual(quote['service_fee'], Decimal('1.50'))
        self.assertEqual(quote['total_price'], Decimal('163.62'))

    def test_qr_generation(self):
        qr_data = "http://127.0.0.1:8000/verify-ticket/PK-999999/"
        qr_base64 = generate_qr_code_base64(qr_data)
        self.assertTrue(qr_base64.startswith("data:image/png;base64,"))

    def test_public_views_accessible(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/parking/').status_code, 200)
        self.assertEqual(self.client.get(f'/parking/{self.facility.slug}/').status_code, 200)
        self.assertEqual(self.client.get('/about/').status_code, 200)
        self.assertEqual(self.client.get('/contact/').status_code, 200)

    def test_booking_checkout_flow(self):
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(hours=3)

        post_data = {
            'confirm_and_pay': '1',
            'slot_id': self.slot.id,
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
            'guest_name': 'Arjun Verma',
            'guest_email': 'arjun@example.in',
            'guest_phone': '+91 98765 43210',
            'vehicle_plate': 'DL-01-CZ-7842',
            'vehicle_model': 'Tata Nexon EV Max',
            'payment_method': 'Credit Card',
        }

        response = self.client.post('/book/', post_data)
        self.assertEqual(response.status_code, 302)

        booking = Booking.objects.get(vehicle_plate='DL-01-CZ-7842')
        self.assertEqual(booking.guest_name, 'Arjun Verma')
        self.assertEqual(booking.status, 'confirmed')
        self.assertTrue(hasattr(booking, 'payment'))
        self.assertEqual(booking.payment.status, 'successful')

        self.slot.refresh_from_db()
        self.assertEqual(self.slot.status, 'occupied')

        ticket_res = self.client.get(f'/verify-ticket/{booking.reference_code}/')
        self.assertEqual(ticket_res.status_code, 200)
        self.assertContains(ticket_res, 'VALID RESERVED PASS')

    def test_cancellation_and_refund_flow(self):
        start = timezone.now() + timedelta(hours=4)
        end = start + timedelta(hours=6)

        booking = Booking.objects.create(
            user=self.user,
            guest_name="Test Driver",
            guest_email="driver@example.com",
            guest_phone="555-1234",
            facility=self.facility,
            floor=self.floor,
            slot=self.slot,
            vehicle_plate="TST-999",
            start_time=start,
            end_time=end,
            hourly_rate=Decimal("10.00"),
            base_price=Decimal("20.00"),
            service_fee=Decimal("1.50"),
            tax_amount=Decimal("1.72"),
            total_price=Decimal("23.22"),
            status="confirmed",
        )
        payment = Payment.objects.create(
            booking=booking,
            transaction_id="TXN_TEST_REFUND",
            amount=Decimal("23.22"),
            status="successful",
        )
        self.slot.status = "occupied"
        self.slot.save()

        # Login user
        self.client.login(username="testdriver", password="TestPassword123!")
        
        # Post cancellation
        cancel_res = self.client.post(f'/booking/{booking.reference_code}/cancel/', {'reason': 'Trip rescheduled'})
        self.assertEqual(cancel_res.status_code, 302)

        booking.refresh_from_db()
        payment.refresh_from_db()
        self.slot.refresh_from_db()

        self.assertEqual(booking.status, "cancelled")
        self.assertEqual(payment.status, "refunded")
        self.assertEqual(self.slot.status, "available")

    def test_staff_gate_check_in_and_out(self):
        start = timezone.now() - timedelta(minutes=10)
        end = start + timedelta(hours=2)

        booking = Booking.objects.create(
            user=self.user,
            guest_name="Gate Driver",
            guest_email="gatedriver@example.com",
            guest_phone="555-9876",
            facility=self.facility,
            floor=self.floor,
            slot=self.slot,
            vehicle_plate="GATE-101",
            start_time=start,
            end_time=end,
            hourly_rate=Decimal("10.00"),
            base_price=Decimal("20.00"),
            service_fee=Decimal("1.50"),
            tax_amount=Decimal("1.72"),
            total_price=Decimal("23.22"),
            status="confirmed",
        )

        self.client.login(username="adminuser", password="AdminPassword123!")

        # Gate Check-in
        check_in_res = self.client.post(f'/verify-ticket/{booking.reference_code}/', {'gate_action': 'check_in'})
        self.assertEqual(check_in_res.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'checked_in')
        self.assertIsNotNone(booking.checked_in_at)

        # Gate Complete (Checkout)
        check_out_res = self.client.post(f'/verify-ticket/{booking.reference_code}/', {'gate_action': 'complete'})
        self.assertEqual(check_out_res.status_code, 302)
        booking.refresh_from_db()
        self.slot.refresh_from_db()
        self.assertEqual(booking.status, 'completed')
        self.assertEqual(self.slot.status, 'available')

    def test_contact_form_submission(self):
        post_data = {
            'name': 'James Miller',
            'email': 'james@example.com',
            'phone': '555-8888',
            'subject': 'Monthly Corporate Fleet Parking',
            'message': 'We would like to reserve 10 dedicated bays for executive vehicles.'
        }
        res = self.client.post('/contact/', post_data)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(ContactMessage.objects.filter(email='james@example.com').exists())

    def test_admin_portal_security_restrictions(self):
        # 1. Unauthenticated user must be redirected to dedicated admin login
        res_anon = self.client.get('/admin-portal/')
        self.assertEqual(res_anon.status_code, 302)
        self.assertTrue('/admin-portal/login/' in res_anon.url)

        # 2. Customer user MUST be blocked with HTTP 403 Forbidden!
        self.client.login(username="testdriver", password="TestPassword123!")
        res_cust = self.client.get('/admin-portal/')
        self.assertEqual(res_cust.status_code, 403)
        self.assertContains(res_cust, 'Restricted Administrator Area', status_code=403)

        # 3. Customer cannot login via admin login form
        self.client.logout()
        res_fake_admin = self.client.post('/admin-portal/login/', {
            'username': 'testdriver',
            'password': 'TestPassword123!'
        })
        self.assertEqual(res_fake_admin.status_code, 200)
        self.assertContains(res_fake_admin, 'ACCESS FORBIDDEN')

        # 4. Authorized admin can access console
        self.client.login(username="adminuser", password="AdminPassword123!")
        res_admin = self.client.get('/admin-portal/')
        self.assertEqual(res_admin.status_code, 200)
        self.assertContains(res_admin, 'Executive Operations Console')
