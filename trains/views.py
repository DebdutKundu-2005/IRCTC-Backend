from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Train
from .serializers import TrainSerializer


class TrainListCreateView(generics.ListCreateAPIView):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    permission_classes = [AllowAny]


class TrainSearchView(generics.ListAPIView):
    serializer_class = TrainSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        source = self.request.query_params.get('source')
        destination = self.request.query_params.get('destination')

        queryset = Train.objects.filter(is_active=True)

        if source:
            queryset = queryset.filter(
                source_station__iexact=source
            )

        if destination:
            queryset = queryset.filter(
                destination_station__iexact=destination
            )

        return queryset


class TrainDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    permission_classes = [AllowAny]