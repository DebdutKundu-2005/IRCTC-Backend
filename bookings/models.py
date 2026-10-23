from django.db import models
import random

from django.conf import settings
from trains.models import Train


def generate_pnr():
    while True:
        pnr = str(random.randint(1000000000, 9999999999))

        if not Booking.objects.filter(pnr=pnr).exists():
            return pnr


class Booking(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('WAITING', 'Waiting'),
        ('CANCELLED', 'Cancelled'),
    ]

    fare_amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0
)
    
    TRAVEL_CLASS_CHOICES = [
        ("GENERAL", "General"),
        ("SL", "Sleeper"),
        ("3A", "AC 3 Tier"),
        ("2A", "AC 2 Tier"),
        ("1A", "AC First Class"),
    ]

    travel_class = models.CharField(
        max_length=10,
        choices=TRAVEL_CLASS_CHOICES,
        default="GENERAL",
    )


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    journey_date = models.DateField()
    booking_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='CONFIRMED'
    )

    total_passengers = models.PositiveIntegerField(default=1)

    pnr = models.CharField(
        max_length=10,
        unique=True,
        default=generate_pnr
    )

    def __str__(self):
        return f"{self.pnr} - {self.user.username}"


class Passenger(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='passengers'
    )

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)
    seat_number = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name