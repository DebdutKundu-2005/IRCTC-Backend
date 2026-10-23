from decimal import Decimal
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from trains.models import Train
from bookings.models import Booking
from .models import Payment


User = get_user_model()


class PaymentAPITestCase(APITestCase):

    def setUp(self):
        # Users
        self.user = User.objects.create_user(
            username='paymentuser',
            password='testpass123'
        )

        self.user2 = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )

        # Train
        self.train = Train.objects.create(
            train_number='54321',
            train_name='Payment Express',
            source_station='Howrah',
            destination_station='New Delhi',
            departure_time='10:00:00',
            arrival_time='18:00:00',
            total_seats=10,
            is_active=True
        )

        # Future journey date
        self.journey_date = date.today() + timedelta(days=30)

        # Booking
        self.booking = Booking.objects.create(
        user=self.user,
            train=self.train,
            journey_date=self.journey_date,
            total_passengers=1,
            status='CONFIRMED',
            fare_amount=Decimal('500.00')
        )

        

        # Authenticate
        self.client.force_authenticate(
            user=self.user
        )
        
    # TEST 1: Create payment
    def test_create_payment(self):

        url = reverse('payment-create')

        data = {
            'booking': self.booking.id,
            'amount': str(self.booking.fare_amount),
            'payment_method': 'UPI'
        }

        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code,
            201
        )

        payment = Payment.objects.get(
            id=response.data['id']
        )

        self.assertEqual(
            payment.status,
            'PENDING'
        )

        self.assertEqual(
            payment.amount,
            Decimal('500.00')
        )

        self.assertEqual(
            payment.payment_method,
            'UPI'
        )

        self.assertIsNone(
            payment.transaction_id
        )

    # TEST 2: Successful payment
    def test_payment_success(self):

        payment = Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='UPI',
            status='PENDING'
        )

        url = reverse(
            'payment-success',
            kwargs={'pk': payment.id}
        )

        response = self.client.put(url)

        self.assertEqual(
            response.status_code,
            200
        )

        payment.refresh_from_db()

        self.assertEqual(
            payment.status,
            'COMPLETED'
        )

        self.assertIsNotNone(
            payment.transaction_id
        )

        self.assertTrue(
            payment.transaction_id.startswith('TXN-')
        )

    # TEST 3: Failed payment
    def test_payment_failed(self):

        payment = Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='CARD',
            status='PENDING'
        )

        url = reverse(
            'payment-failed',
            kwargs={'pk': payment.id}
        )

        response = self.client.put(url)

        self.assertEqual(
            response.status_code,
            200
        )

        payment.refresh_from_db()

        self.assertEqual(
            payment.status,
            'FAILED'
        )

    # TEST 4: Completed payment cannot be failed
    def test_completed_payment_cannot_be_failed(self):

        payment = Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='CARD',
            status='COMPLETED',
            transaction_id='TXN-TEST123456'
        )

        url = reverse(
            'payment-failed',
            kwargs={'pk': payment.id}
        )

        response = self.client.put(url)

        self.assertEqual(
            response.status_code,
            400
        )

        payment.refresh_from_db()

        self.assertEqual(
            payment.status,
            'COMPLETED'
        )

    # TEST 5: Failed payment cannot be successful
    def test_failed_payment_cannot_be_successful(self):

        payment = Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='UPI',
            status='FAILED'
        )

        url = reverse(
            'payment-success',
            kwargs={'pk': payment.id}
        )

        response = self.client.put(url)

        self.assertEqual(
            response.status_code,
            400
        )

        payment.refresh_from_db()

        self.assertEqual(
            payment.status,
            'FAILED'
        )

    # TEST 6: Duplicate payment not allowed
    def test_duplicate_payment_not_allowed(self):

        Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='UPI',
            status='PENDING'
        )

        url = reverse('payment-create')

        data = {
            'booking': self.booking.id,
            'amount': '500.00',
            'payment_method': 'CARD'
        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # TEST 7: Cancelled booking cannot be paid
    def test_cancelled_booking_payment_not_allowed(self):

        self.booking.status = 'CANCELLED'
        self.booking.save(
            update_fields=['status']
        )

        url = reverse('payment-create')

        data = {
            'booking': self.booking.id,
            'amount': '500.00',
            'payment_method': 'UPI'
        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # TEST 8: User cannot pay for another user's booking
    def test_other_user_cannot_pay_for_booking(self):

        self.client.force_authenticate(
            user=self.user2
        )

        url = reverse('payment-create')

        data = {
            'booking': self.booking.id,
            'amount': '500.00',
            'payment_method': 'UPI'
        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # TEST 9: Invalid payment amount

    def test_invalid_payment_amount(self):

        url = reverse('payment-create')

        data = {
            'booking': self.booking.id,
            'amount': '-100.00',
            'payment_method': 'UPI'
        }

        response = self.client.post(
            url,
            data
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # TEST 10: Payment detail

    def test_payment_detail(self):

        payment = Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='NETBANKING',
            status='PENDING'
        )

        url = reverse(
            'payment-detail',
            kwargs={'pk': payment.id}
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data['id'],
            payment.id
        )

        self.assertEqual(
            response.data['booking_pnr'],
            self.booking.pnr
        )

# TEST 11: Successful payment belongs to correct booking
    def test_successful_payment_booking(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='UPI',
            status='PENDING'
        )

        url = reverse(
            'payment-success',
            kwargs={'pk': payment.id}
        )

        response = self.client.put(url)

        self.assertEqual(response.status_code, 200)

        payment.refresh_from_db()

        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(payment.booking.id, self.booking.id)
        self.assertEqual(payment.booking.pnr, self.booking.pnr)

    
    def test_process_payment_success(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='UPI',
            status='PENDING'
        )

        url = reverse(
            'payment-process',
            kwargs={'payment_id': payment.id}
        )

        response = self.client.post(
            url,
            {'action': 'SUCCESS'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        payment.refresh_from_db()
        self.booking.refresh_from_db()

        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(self.booking.status, 'CONFIRMED')
        self.assertIsNotNone(payment.transaction_id)

    def test_process_payment_failed(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='UPI',
            status='PENDING'
        )

        url = reverse(
            'payment-process',
            kwargs={'payment_id': payment.id}
        )

        response = self.client.post(
            url,
            {'action': 'FAILED'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        payment.refresh_from_db()
        self.booking.refresh_from_db()

        self.assertEqual(payment.status, 'FAILED')
        self.assertEqual(self.booking.status, 'CANCELLED')

    def test_process_completed_payment_again_is_rejected(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='UPI',
            status='COMPLETED',
            transaction_id='TXN-EXISTING123'
        )

        url = reverse(
            'payment-process',
            kwargs={'payment_id': payment.id}
        )

        response = self.client.post(
            url,
            {'action': 'SUCCESS'},
            format='json'
        )

        self.assertEqual(response.status_code, 400)

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(
            payment.transaction_id,
            'TXN-EXISTING123'
        )

    def test_other_user_cannot_process_payment(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='UPI',
            status='PENDING'
        )

        self.client.force_authenticate(user=self.user2)

        url = reverse(
            'payment-process',
            kwargs={'payment_id': payment.id}
        )

        response = self.client.post(
            url,
            {'action': 'SUCCESS'},
            format='json'
        )

        self.assertEqual(response.status_code, 404)

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'PENDING')

    def test_duplicate_payment_creation_rejected(self):
        Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='UPI',
            status='PENDING'
        )

        url = reverse('payment-create')

        response = self.client.post(
            url,
            {
                'booking': self.booking.id,
                'amount': '500.00',
                'payment_method': 'UPI'
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            Payment.objects.filter(booking=self.booking).count(),
            1
        )
    
    def test_process_failed_payment_again_is_rejected(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=500,
            payment_method='UPI',
            status='FAILED',
            transaction_id='TXN-FAILED12345'
        )

        url = reverse(
            'payment-process',
            kwargs={'payment_id': payment.id}
        )

        response = self.client.post(
            url,
            {'action': 'SUCCESS'},
            format='json'
        )

        self.assertEqual(response.status_code, 400)

        payment.refresh_from_db()

        self.assertEqual(payment.status, 'FAILED')
        self.assertEqual(
            payment.transaction_id,
            'TXN-FAILED12345'
        )

