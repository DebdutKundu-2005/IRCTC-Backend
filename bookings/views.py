from datetime import date

from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .services import calculate_booking_fare
from .models import Booking, Passenger
from .serializers import (
    BookingSerializer,
    PassengerSerializer,
    PNRBookingSerializer
)
from .tasks import send_booking_confirmation_email

# FIND NEXT AVAILABLE SEAT
def get_next_available_seat(train, journey_date):
    occupied_seats = Passenger.objects.filter(
        booking__train=train,
        booking__journey_date=journey_date,
        booking__status='CONFIRMED'
    ).exclude(
        seat_number__isnull=True
    ).values_list(
        'seat_number',
        flat=True
    )

    occupied_numbers = set()

    for seat in occupied_seats:
        if seat and seat.startswith('S'):
            try:
                occupied_numbers.add(int(seat[1:]))
            except ValueError:
                pass

    for number in range(1, train.total_seats + 1):
        if number not in occupied_numbers:
            return f"S{number}"

    return None

# BOOKING LIST + CREATE
class BookingListCreateView(generics.ListCreateAPIView):

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        )

    
    def perform_create(self, serializer):

        train = serializer.validated_data['train']
        journey_date = serializer.validated_data['journey_date']

        total_passengers = serializer.validated_data.get(
            'total_passengers',
            1
        )

        travel_class = serializer.validated_data.get(
            'travel_class',
            'GENERAL'
        )

        # Calculate fare using train type, distance and class
        fare_amount = calculate_booking_fare(
            train=train,
            total_passengers=total_passengers,
            travel_class=travel_class
        )

        # Count seats reserved by CONFIRMED bookings
        booked_seats = Booking.objects.filter(
            train=train,
            journey_date=journey_date,
            status='CONFIRMED'
        ).aggregate(
            total=Sum('total_passengers')
        )['total'] or 0

        available_seats = train.total_seats - booked_seats

        # Decide booking status
        if available_seats >= total_passengers:
            status = 'CONFIRMED'
        else:
            status = 'WAITING'

        # Create booking with calculated fare
        booking = serializer.save(
            user=self.request.user,
            status=status,
            fare_amount=fare_amount
        )

        # Send email ONLY for confirmed booking
        if booking.status == 'CONFIRMED':
            transaction.on_commit(
                lambda: send_booking_confirmation_email.delay(
                    booking.id
                )
            )

# PASSENGER CREATE
class PassengerListCreateView(generics.CreateAPIView):

    serializer_class = PassengerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        booking_id = self.kwargs['booking_id']

        booking = get_object_or_404(
            Booking,
            id=booking_id,
            user=self.request.user
        )

        # Cancelled booking
        if booking.status == 'CANCELLED':
            raise serializers.ValidationError(
                "Cannot add passenger to a cancelled booking."
            )

        # Check passenger limit
        existing_passengers = Passenger.objects.filter(
            booking=booking
        ).count()

        if existing_passengers >= booking.total_passengers:
            raise serializers.ValidationError(
                "Maximum passengers for this booking "
                "have already been added."
            )

        # WAITING booking
        # No seat assigned
        if booking.status == 'WAITING':

            serializer.save(
                booking=booking,
                seat_number=None
            )

            return

        # CONFIRMED booking
        # Find available seat
        train = booking.train

        seat_number = get_next_available_seat(
            train,
            booking.journey_date
        )

        if seat_number is None:
            raise serializers.ValidationError(
                "No seats available for this train "
                "on the selected date."
            )

        serializer.save(
            booking=booking,
            seat_number=seat_number
        )

# BOOKING DETAIL
class BookingDetailView(generics.RetrieveAPIView):

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        )

# PNR SEARCH
class PNRSearchView(generics.RetrieveAPIView):

    serializer_class = PNRBookingSerializer
    permission_classes = [AllowAny]

    def get_object(self):

        pnr = self.kwargs['pnr']

        return get_object_or_404(
            Booking,
            pnr=pnr
        )

# BOOKING CANCEL
class BookingCancelView(generics.UpdateAPIView):

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):

        # Get booking
        booking = self.get_object()

        # Already cancelled
        if booking.status == 'CANCELLED':
            raise serializers.ValidationError(
                "This booking is already cancelled."
            )

        # Past journey cannot be cancelled
        if booking.journey_date < date.today():
            raise serializers.ValidationError(
                "Past journey bookings cannot be cancelled."
            )
        
        # Cancel current booking
        booking.status = 'CANCELLED'

        booking.save(
            update_fields=['status']
        )

        # Find oldest WAITING booking
        waiting_booking = Booking.objects.filter(
            train=booking.train,
            journey_date=booking.journey_date,
            status='WAITING'
        ).order_by(
            'booking_date'
        ).first()

        promoted_booking = None

        # Promote waiting booking
        if waiting_booking:

            # Count currently reserved seats
            confirmed_seats = Booking.objects.filter(
                train=booking.train,
                journey_date=booking.journey_date,
                status='CONFIRMED'
            ).aggregate(
                total=Sum('total_passengers')
            )['total'] or 0

            available_seats = (
                booking.train.total_seats
                - confirmed_seats
            )

            # Promote ONLY if enough seats are available
            if available_seats >= waiting_booking.total_passengers:

                waiting_booking.status = 'CONFIRMED'

                waiting_booking.save(
                    update_fields=['status']
                )

                # Assign DIFFERENT seats to passengers
                waiting_passengers = Passenger.objects.filter(
                    booking=waiting_booking
                )

                for passenger in waiting_passengers:

                    available_seat = get_next_available_seat(
                        booking.train,
                        booking.journey_date
                    )

                    if available_seat is None:
                        break

                    passenger.seat_number = available_seat

                    passenger.save(
                        update_fields=['seat_number']
                    )

                promoted_booking = waiting_booking

                # Send confirmation email
                transaction.on_commit(
                    lambda: send_booking_confirmation_email.delay(
                        waiting_booking.id
                    )
                )

        # Response
        response_data = {
            'message': 'Booking cancelled successfully.',
            'pnr': booking.pnr,
            'status': booking.status
        }

        if promoted_booking:

            response_data['promoted_booking_pnr'] = (
                promoted_booking.pnr
            )

            response_data['promoted_booking_status'] = (
                promoted_booking.status
            )

        return Response(response_data)