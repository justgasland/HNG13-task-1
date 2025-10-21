from django.urls import path
from .views import (
    StringListCreateView,
    StringDetailView,
    FilterByNaturalLanguageView
)

urlpatterns = [
    path('strings/', StringListCreateView.as_view(), name='list_create_string'),
    path('strings/<str:string_value>/', StringDetailView.as_view(), name='string_detail'),
    path('strings/filter-by-natural-language/', FilterByNaturalLanguageView.as_view(), name='filter_by_natural_language'),
]
