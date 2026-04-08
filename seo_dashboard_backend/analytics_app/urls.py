from django.urls import path
from .views import (
    WebsiteCreateView,
    WebsiteListView,
    export_seo_report,
    get_recommendations,
    get_search_console_data,
    google_analytics_login,
    google_analytics_callback,
    list_ga_properties,
    mark_recommendation_read,
    get_ga_data,
    verify_ga_property_url,
)

urlpatterns = [
    path("add-site/", WebsiteCreateView.as_view()),
    path("sites/", WebsiteListView.as_view()),
    path("google-analytics/login/", google_analytics_login),
    path("google-analytics/callback/", google_analytics_callback),
    path("google-analytics/properties/", list_ga_properties),
    path("google-analytics/data/<str:property_id>/", get_ga_data),
    path("google-analytics/verify-url/", verify_ga_property_url),
    path("search-console/data/", get_search_console_data),
    path("recommendations/<int:website_id>/", get_recommendations),
    path(
        "recommendations/<int:recommendation_id>/read/",
        mark_recommendation_read,
    ),
    path("export-pdf/<int:website_id>/", export_seo_report),
]
