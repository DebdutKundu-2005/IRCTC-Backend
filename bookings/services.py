
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from rest_framework import serializers


def calculate_booking_fare(train, total_passengers, travel_class="GENERAL"):
    distance_km = train.distance_km

    if distance_km <= 0:
        raise serializers.ValidationError({
            "train": "A valid route distance is required."
        })

    if total_passengers < 1:
        raise serializers.ValidationError({
            "total_passengers": "At least one passenger is required."
        })

    fare_rates = settings.TICKET_FARE_RATES

    train_type = train.train_type
    train_rates = fare_rates.get(train_type, {})
    rate = train_rates.get(travel_class)

    if rate is None:
        raise serializers.ValidationError({
            "travel_class": "This class is not available for this train type."
        })

    total_fare = (
        Decimal(distance_km)
        * Decimal(str(rate))
        * Decimal(total_passengers)
    )

    return total_fare.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )
