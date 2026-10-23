from rest_framework import serializers
from .models import Train


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = [
            'id',
            'train_number',
            'train_name',
            'source_station',
            'destination_station',
            'departure_time',
            'arrival_time',
            'total_seats',
            'is_active',
            'created_at',
        ]