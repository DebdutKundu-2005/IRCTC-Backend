from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import response
from django.urls import reverse
from rest_framework.test import APITestCase

from trains.models import Train
from .models import Booking, Passenger
from decimal import Decimal


User = get_user_model()


class BookingAPITestCase(APITestCase):

    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )

        # Create train
        self.train = Train.objects.create(
            train_number='12345',
            train_name='Test Express',
            source_station='Howrah',
            destination_station='New Delhi',
            departure_time='10:00:00',
            arrival_time='18:00:00',
            total_seats=1,
            is_active=True,
            distance_km=100,
            train_type="EXPRESS",
            
        )

        # Future journey date
        self.journey_date = date.today() + timedelta(days=30)

        # Login/authenticate user
        self.client.force_authenticate(user=self.user)

    # TEST 1: Create confirmed booking
    @patch('bookings.views.send_booking_confirmation_email.delay')
    def test_create_confirmed_booking(self, mock_email):
        url = reverse('booking-list-create')

        data = {
            'train': self.train.id,
            'journey_date': self.journey_date,
            'total_passengers': 1
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, data)

        booking = Booking.objects.get(
            id=response.data['id']
        )

        self.assertEqual(
            booking.status,
            'CONFIRMED'
        )
        self.assertEqual(
        booking.fare_amount,
        Decimal("100.00")
        )   

        self.assertEqual(
            booking.total_passengers,
            1
        )

        self.assertIsNotNone(
            booking.pnr
        )

        # Confirmation email task should be called
        mock_email.assert_called_once_with(
            booking.id
        )

    # TEST 2: Add passenger and check seat allocation
    @patch('bookings.views.send_booking_confirmation_email.delay')
    def test_passenger_gets_seat(self, mock_email):

        # Create booking
        booking = Booking.objects.create(
            user=self.user,
            train=self.train,
            journey_date=self.journey_date,
            total_passengers=1,
            status='CONFIRMED'
        )

        url = reverse(
            'passenger-list-create',
            kwargs={'booking_id': booking.id}
        )

        data = {
            'name': 'Rahul',
            'age': 25,
            'gender': 'MALE'
        }

        response = self.client.post(url, data)
        
        self.assertEqual(
            response.status_code,
            201
        )
     

        passenger = Passenger.objects.get(
            id=response.data['id']
        )

        self.assertEqual(
            passenger.seat_number,
            'S1'
        )

    # TEST 3: Second booking goes to waiting list
    @patch('bookings.views.send_booking_confirmation_email.delay')
    def test_waiting_list_booking(self, mock_email):

        # First booking occupies the only seat
        first_booking = Booking.objects.create(
            user=self.user,
            train=self.train,
            journey_date=self.journey_date,
            total_passengers=1,
            status='CONFIRMED'
        )

        Passenger.objects.create(
            booking=first_booking,
            name='Rahul',
            age=25,
            gender='MALE',
            seat_number='S1'
        )

        # Second user creates booking
        self.client.force_authenticate(
            user=self.user2
        )

        url = reverse('booking-list-create')

        data = {
            'train': self.train.id,
            'journey_date': self.journey_date,
            'total_passengers': 1
        }

        response = self.client.post(url, data)
        

        self.assertEqual(
            response.status_code,
            201
        )

        waiting_booking = Booking.objects.get(
            id=response.data['id']
        )

        self.assertEqual(
            waiting_booking.status,
            'WAITING'
        )

    # TEST 4: Waiting passenger gets no seat
    def test_waiting_passenger_has_no_seat(self):

        booking = Booking.objects.create(
            user=self.user,
            train=self.train,
            journey_date=self.journey_date,
            total_passengers=1,
            status='WAITING'
        )

        url = reverse(
            'passenger-list-create',
            kwargs={'booking_id': booking.id}
        )

        data = {
            'name': 'Amit',
            'age': 30,
            'gender': 'MALE'
        }

        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code,
            201
        )

        passenger = Passenger.objects.get(
            id=response.data['id']
        )

        self.assertIsNone(
            passenger.seat_number
        )

    # TEST 5: Booking detail
    def test_booking_detail(self):

        booking = Booking.objects.create(
            user=self.user,
            train=self.train,
            journey_date=self.journey_date,
            total_passengers=1,
            status='CONFIRMED'
        )

        url = reverse(
            'booking-detail',
            kwargs={'pk': booking.id}
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data['id'],
            booking.id
        )

    # TEST 6: PNR search
    def test_pnr_search(self):

        booking = Booking.objects.create(
            user=self.user,
            train=self.train,
            journey_date=self.journey_date,
            total_passengers=1,
            status='CONFIRMED'
        )

        url = reverse(
            'pnr-search',
            kwargs={'pnr': booking.pnr}
        )

        # PNR search does not require authentication
        self.client.force_authenticate(user=None)

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data['pnr'],
            booking.pnr
        )

        self.assertEqual(
            response.data['train_number'],
            self.train.train_number
        )

    # TEST 7: Cancel booking and promote waiting booking
    @patch('bookings.views.send_booking_confirmation_email.delay')
    def test_cancel_promotes_waiting_booking(self, mock_email):

        # First confirmed booking
        first_booking = Booking.objects.create(
            user=self.user,
            train=self.train,
            journey_date=self.journey_date,
            total_passengers=1,
            status='CONFIRMED'
        )

        Passenger.objects.create(
            booking=first_booking,
            name='Rahul',
            age=25,
            gender='MALE',
            seat_number='S1'
        )

        # Second booking goes to waiting
        waiting_booking = Booking.objects.create(
            user=self.user2,
            train=self.train,
            journey_date=self.journey_date,
            total_passengers=1,
            status='WAITING'
        )

        waiting_passenger = Passenger.objects.create(
            booking=waiting_booking,
            name='Amit',
            age=30,
            gender='MALE',
            seat_number=None
        )

        # Authenticate first user
        self.client.force_authenticate(
            user=self.user
        )

        # Cancel first booking
        url = reverse(
            'booking-cancel',
            kwargs={'pk': first_booking.id}
        )

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.put(url)

        self.assertEqual(
            response.status_code,
            200
        )

        # First booking cancelled
        first_booking.refresh_from_db()

        self.assertEqual(
            first_booking.status,
            'CANCELLED'
        )

        # Waiting booking promoted
        waiting_booking.refresh_from_db()

        self.assertEqual(
            waiting_booking.status,
            'CONFIRMED'
        )

        # Waiting passenger gets S1
        waiting_passenger.refresh_from_db()

        self.assertEqual(
            waiting_passenger.seat_number,
            'S1'
        )

        # Promotion email sent
        mock_email.assert_called_once_with(
            waiting_booking.id
        )
    def test_fare_rejects_invalid_distance(self):
        from rest_framework.exceptions import ValidationError
        from bookings.services import calculate_booking_fare

        self.train.distance_km = 0

        with self.assertRaises(ValidationError):
            calculate_booking_fare(
            train=self.train,
            total_passengers=1,
            travel_class="GENERAL",
            )
    def test_fare_rejects_invalid_travel_class(self):
        from rest_framework.exceptions import ValidationError
        from bookings.services import calculate_booking_fare

        with self.assertRaises(ValidationError):
            calculate_booking_fare(
                train=self.train,
                total_passengers=1,
                travel_class="INVALID",
            )