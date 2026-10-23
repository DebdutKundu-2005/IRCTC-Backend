from django.urls import path

from .views import (
    TrainListCreateView,
    TrainSearchView,
    TrainDetailView
)


urlpatterns = [
    path(
        '',
        TrainListCreateView.as_view(),
        name='train-list-create'
    ),

    path(
        'search/',
        TrainSearchView.as_view(),
        name='train-search'
    ),

    path(
        '<int:pk>/',
        TrainDetailView.as_view(),
        name='train-detail'
    ),
]