from datetime import date, datetime

from rest_framework import serializers
from .models import Booking, Passenger


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = [
            'id',
            'name',
            'age',
            'gender',
            'seat_number',
        ]
        read_only_fields = ['seat_number']
    def validate_age(self, value):
        if value < 1:
            raise serializers.ValidationError("Age must be at least 1.")
        if value > 120:
            raise serializers.ValidationError("Please enter a valid age.")
        return value
    def validate_gender(self, value):
        value=value.upper()
        if value not in['MALE', 'FEMALE', 'OTHER']:
            raise serializers.ValidationError("Gender must be 'MALE', 'FEMALE', or 'OTHER'.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True, read_only=True)
    fare_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'pnr',
            'user',
            'train',
            'journey_date',
            'booking_date',
            'status',
            'total_passengers',
            'travel_class',
            'fare_amount',
            'passengers',
        ]
        read_only_fields = [
            'user',
            'pnr',
            'booking_date',
            'status',
            'fare_amount',
        ]

    def validate(self, data):
        journey_date = data.get('journey_date')
        total_passengers = data.get('total_passengers', 1)
        train = data.get('train')

        if journey_date is not None and journey_date < date.today():
            raise serializers.ValidationError(
                "Journey date cannot be in the past."
            )

        if train is not None and not train.is_active:
            raise serializers.ValidationError(
                "This train is currently inactive."
            )

        if total_passengers < 1:
            raise serializers.ValidationError(
                "At least 1 passenger is required."
            )

        if total_passengers > 6:
            raise serializers.ValidationError(
                "Maximum 6 passengers are allowed per booking."
            )

        return data

class PNRBookingSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True, read_only=True)
    train_number = serializers.CharField(source='train.train_number', read_only=True)
    train_name = serializers.CharField(source='train.train_name', read_only=True)
    source_station = serializers.CharField(source='train.source_station', read_only=True)
    destination_station = serializers.CharField(source='train.destination_station', read_only=True)
    departure_time = serializers.TimeField(source='train.departure_time', read_only=True)
    arrival_time = serializers.TimeField(source='train.arrival_time', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'pnr',
            'train_number',
            'train_name',
            'source_station',
            'destination_station',
            'departure_time',
            'arrival_time',
            'journey_date',
            'booking_date',
            'status',
            'total_passengers',
            'passengers',
            'travel_class',
            'fare_amount',
        ]