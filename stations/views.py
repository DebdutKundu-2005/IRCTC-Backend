from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Station
from .serializers import StationSerializer


class StationListCreateView(generics.ListCreateAPIView):
    serializer_class = StationSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Station.objects.all()

        station_code = self.request.query_params.get('station_code')
        city = self.request.query_params.get('city')

        if station_code:
            queryset = queryset.filter(station_code__iexact=station_code)

        if city:
            queryset = queryset.filter(city__iexact=city)

        return queryset


class StationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]