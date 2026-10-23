from django.db import models

# Create your models here.
class Train(models.Model):
    TRAIN_TYPE_CHOICES = [
        ("LOCAL", "Local"),
        ("EXPRESS", "Express"),
    ]

    train_type = models.CharField(
        max_length=10,
        choices=TRAIN_TYPE_CHOICES,
        default="EXPRESS",
    )


    train_number = models.CharField(max_length=10, unique=True)
    train_name = models.CharField(max_length=100)

    source_station = models.CharField(max_length=100)
    destination_station = models.CharField(max_length=100)

    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    total_seats = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    distance_km = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.train_number} - {self.train_name}"
