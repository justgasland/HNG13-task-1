from django.urls import path
from .views import StringCreateListView, StringDetailView, NaturalLanguageFilterView

urlpatterns = [
    # Natural language filter MUST come before the detail view
    # to avoid matching "filter-by-natural-language" as a string_value
    path('strings/filter-by-natural-language', NaturalLanguageFilterView.as_view(), name='natural_language_filter'),
    
    # Create and list strings
    path('strings', StringCreateListView.as_view(), name='string_create_list'),
    
    # Get and delete specific string (MUST be last to avoid conflicts)
    path('strings/<path:string_value>', StringDetailView.as_view(), name='string_detail'),
]