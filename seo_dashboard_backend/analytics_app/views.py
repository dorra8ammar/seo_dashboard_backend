from datetime import date, timedelta
import secrets
from urllib.parse import urlencode, urlparse

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import GoogleAnalyticsToken

from .models import Recommendation, Website
from .pdf_generator import generate_seo_report
from .seo_analyzer import analyze_seo_and_generate_recommendations
from .serializers import RecommendationSerializer, WebsiteSerializer


oauth_states = {}


def _get_google_credentials_for_user(user):
    token_obj = GoogleAnalyticsToken.objects.get(user=user)
    return Credentials(
        token=token_obj.access_token,
        refresh_token=token_obj.refresh_token,
        token_uri=token_obj.token_uri,
        client_id=token_obj.client_id,
        client_secret=token_obj.client_secret,
        scopes=[
            "https://www.googleapis.com/auth/analytics.readonly",
            "https://www.googleapis.com/auth/webmasters.readonly",
        ],
    )


def _fetch_website_analytics_bundle(user, website):
    credentials = _get_google_credentials_for_user(user)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    ga_service = build("analyticsdata", "v1beta", credentials=credentials)
    ga_response = ga_service.properties().runReport(
        property=f"properties/{website.property_id}",
        body={
            "dateRanges": [
                {
                    "startDate": start_date.strftime("%Y-%m-%d"),
                    "endDate": end_date.strftime("%Y-%m-%d"),
                }
            ],
            "dimensions": [{"name": "date"}],
            "metrics": [
                {"name": "activeUsers"},
                {"name": "sessions"},
                {"name": "screenPageViews"},
                {"name": "bounceRate"},
            ],
        },
    ).execute()

    ga_data = []
    for row in ga_response.get("rows", []):
        ga_data.append(
            {
                "date": row["dimensionValues"][0]["value"],
                "users": float(row["metricValues"][0]["value"]),
                "sessions": float(row["metricValues"][1]["value"]),
                "views": float(row["metricValues"][2]["value"]),
                "bounceRate": float(row["metricValues"][3]["value"]),
            }
        )

    sc_service = build("searchconsole", "v1", credentials=credentials)
    sc_response = sc_service.searchanalytics().query(
        siteUrl=website.url,
        body={
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["query"],
            "rowLimit": 20,
        },
    ).execute()

    search_console_data = []
    for row in sc_response.get("rows", []):
        search_console_data.append(
            {
                "keyword": row["keys"][0],
                "clicks": row["clicks"],
                "impressions": row["impressions"],
                "ctr": row["ctr"],
                "position": row["position"],
            }
        )

    return ga_data, search_console_data


# ================= WEBSITE =================

class WebsiteCreateView(generics.CreateAPIView):
    serializer_class = WebsiteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WebsiteListView(generics.ListAPIView):
    serializer_class = WebsiteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Website.objects.filter(user=self.request.user)


# ================= GOOGLE LOGIN (ANALYTICS + SEARCH CONSOLE) =================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def google_analytics_login(request):
    state = secrets.token_urlsafe(16)
    oauth_states[state] = request.user.id

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": (
            "https://www.googleapis.com/auth/analytics.readonly "
            "https://www.googleapis.com/auth/webmasters.readonly"
        ),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }

    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return Response({"auth_url": url})


@api_view(["GET"])
def google_analytics_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    if not code or not state:
        return JsonResponse({"error": "code ou state manquant"}, status=400)

    user_id = oauth_states.get(state)
    if not user_id:
        return JsonResponse({"error": "state invalide"}, status=400)

    user = User.objects.get(id=user_id)

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()

    GoogleAnalyticsToken.objects.update_or_create(
        user=user,
        defaults={
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "token_uri": token_url,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "scopes": (
                "https://www.googleapis.com/auth/analytics.readonly "
                "https://www.googleapis.com/auth/webmasters.readonly"
            ),
        },
    )

    oauth_states.pop(state, None)

    return redirect("http://localhost:5173/dashboard")


# ================= PROPRIETES GOOGLE ANALYTICS =================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_ga_properties(request):
    token_obj = GoogleAnalyticsToken.objects.get(user=request.user)

    credentials = Credentials(token=token_obj.access_token)

    service = build("analyticsadmin", "v1beta", credentials=credentials)
    result = service.accountSummaries().list().execute()

    properties = []
    for account in result.get("accountSummaries", []):
        for prop in account.get("propertySummaries", []):
            properties.append(
                {
                    "property_id": prop.get("property", "").split("/")[-1],
                    "display_name": prop.get("displayName"),
                }
            )

    return JsonResponse(properties, safe=False)


# ================= DONNEES GOOGLE ANALYTICS =================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_ga_data(request, property_id):
    token_obj = GoogleAnalyticsToken.objects.get(user=request.user)

    credentials = Credentials(token=token_obj.access_token)

    service = build("analyticsdata", "v1beta", credentials=credentials)

    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    response = service.properties().runReport(
        property=f"properties/{property_id}",
        body={
            "dateRanges": [{"startDate": start_date_str, "endDate": end_date_str}],
            "dimensions": [{"name": "date"}],
            "metrics": [
                {"name": "activeUsers"},
                {"name": "sessions"},
                {"name": "screenPageViews"},
                {"name": "bounceRate"},
            ],
        },
    ).execute()

    data = []
    for row in response.get("rows", []):
        data.append(
            {
                "date": row["dimensionValues"][0]["value"],
                "users": row["metricValues"][0]["value"],
                "sessions": row["metricValues"][1]["value"],
                "views": row["metricValues"][2]["value"],
                "bounceRate": row["metricValues"][3]["value"],
            }
        )

    return Response(data)


# ================= VERIFICATION URL / PROPRIETE =================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_ga_property_url(request):
    site_url = request.data.get("site_url")
    property_id = request.data.get("property_id")

    if not site_url or not property_id:
        return Response(
            {"error": "site_url et property_id sont obligatoires"},
            status=400,
        )

    try:
        token_obj = GoogleAnalyticsToken.objects.get(user=request.user)
    except GoogleAnalyticsToken.DoesNotExist:
        return Response(
            {"error": "Aucun compte Google Analytics connecte."},
            status=404,
        )

    credentials = Credentials(token=token_obj.access_token)

    service = build("analyticsadmin", "v1beta", credentials=credentials)

    try:
        streams_response = service.properties().dataStreams().list(
            parent=f"properties/{property_id}"
        ).execute()
    except Exception as e:
        return Response(
            {"error": "Impossible de recuperer les data streams", "details": str(e)},
            status=400,
        )

    site_domain = urlparse(site_url).netloc.replace("www.", "").lower()

    for stream in streams_response.get("dataStreams", []):
        web_stream_data = stream.get("webStreamData")
        if web_stream_data and web_stream_data.get("defaultUri"):
            default_uri = web_stream_data["defaultUri"]
            ga_domain = urlparse(default_uri).netloc.replace("www.", "").lower()

            if site_domain == ga_domain:
                return Response(
                    {
                        "match": True,
                        "site_url": site_url,
                        "default_uri": default_uri,
                        "message": "La propriete GA correspond a l'URL du site.",
                    }
                )

    return Response(
        {
            "match": False,
            "site_url": site_url,
            "message": (
                "Cette propriete Google Analytics ne correspond pas a l'URL saisie."
            ),
        }
    )


# ================= GOOGLE SEARCH CONSOLE =================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_search_console_data(request):
    """
    Recupere les donnees SEO depuis Google Search Console.
    Retourne : mots-cles, clics, impressions, CTR, position.
    """
    site_url = request.GET.get("site_url")
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    if not site_url:
        return JsonResponse({"error": "site_url manquant"}, status=400)

    try:
        token_obj = GoogleAnalyticsToken.objects.get(user=request.user)
    except GoogleAnalyticsToken.DoesNotExist:
        return JsonResponse(
            {
                "error": (
                    "Token Google introuvable. Veuillez reconnecter Google Analytics."
                )
            },
            status=404,
        )

    credentials = Credentials(
        token=token_obj.access_token,
        refresh_token=token_obj.refresh_token,
        token_uri=token_obj.token_uri,
        client_id=token_obj.client_id,
        client_secret=token_obj.client_secret,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
    )

    service = build("searchconsole", "v1", credentials=credentials)

    if start_date_str and end_date_str:
        start_date = start_date_str
        end_date = end_date_str
    else:
        end_date_obj = date.today()
        start_date_obj = end_date_obj - timedelta(days=30)
        start_date = start_date_obj.strftime("%Y-%m-%d")
        end_date = end_date_obj.strftime("%Y-%m-%d")

    request_body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["query"],
        "rowLimit": 20,
    }

    try:
        response = service.searchanalytics().query(
            siteUrl=site_url,
            body=request_body,
        ).execute()
    except Exception as e:
        return JsonResponse({"error": f"Erreur Search Console: {str(e)}"}, status=400)

    results = []
    for row in response.get("rows", []):
        results.append(
            {
                "keyword": row["keys"][0],
                "clicks": row["clicks"],
                "impressions": row["impressions"],
                "ctr": row["ctr"],
                "position": row["position"],
            }
        )

    return JsonResponse(results, safe=False)


# ================= RECOMMANDATIONS IA =================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_recommendations(request, website_id):
    """
    Recupere les recommandations SEO pour un site.
    Si aucune recommandation n'existe, les genere.
    """
    try:
        website = Website.objects.get(id=website_id, user=request.user)
    except Website.DoesNotExist:
        return Response({"error": "Site non trouve"}, status=404)

    recent_recommendations = Recommendation.objects.filter(
        website=website,
        created_at__gte=timezone.now() - timedelta(days=1),
    )

    if recent_recommendations.exists():
        serializer = RecommendationSerializer(recent_recommendations, many=True)
        return Response(serializer.data)

    try:
        ga_data, search_console_data = _fetch_website_analytics_bundle(
            request.user, website
        )

        recommendations_data = analyze_seo_and_generate_recommendations(
            ga_data, search_console_data, website
        )

        Recommendation.objects.filter(website=website).delete()

        saved_recommendations = []
        for rec_data in recommendations_data:
            recommendation = Recommendation.objects.create(
                website=website,
                title=rec_data["title"],
                description=rec_data["description"],
                action=rec_data.get("action", ""),
                recommendation_type=rec_data["recommendation_type"],
                priority=rec_data["priority"],
            )
            saved_recommendations.append(recommendation)

        serializer = RecommendationSerializer(saved_recommendations, many=True)
        return Response(serializer.data)

    except Exception as e:
        return Response(
            {"error": f"Erreur generation recommandations: {str(e)}"},
            status=500,
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def mark_recommendation_read(request, recommendation_id):
    """Marquer une recommandation comme lue."""
    try:
        recommendation = Recommendation.objects.get(
            id=recommendation_id,
            website__user=request.user,
        )
        recommendation.is_read = True
        recommendation.save()
        return Response({"message": "Recommandation marquee comme lue"})
    except Recommendation.DoesNotExist:
        return Response({"error": "Recommandation non trouvee"}, status=404)


# ================= EXPORT PDF =================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_seo_report(request, website_id):
    """
    Exporte un rapport PDF complet pour un site
    """
    from .pdf_generator import generate_seo_report
    from datetime import datetime

    try:
        website = Website.objects.get(id=website_id, user=request.user)
    except Website.DoesNotExist:
        return Response({"error": "Site non trouve"}, status=404)

    try:
        token_obj = GoogleAnalyticsToken.objects.get(user=request.user)
    except GoogleAnalyticsToken.DoesNotExist:
        return Response({"error": "Google Analytics non connecte"}, status=404)

    credentials = Credentials(token=token_obj.access_token)

    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    service_ga = build("analyticsdata", "v1beta", credentials=credentials)
    ga_data = []

    try:
        ga_response = service_ga.properties().runReport(
            property=f"properties/{website.property_id}",
            body={
                "dateRanges": [
                    {
                        "startDate": start_date.strftime("%Y-%m-%d"),
                        "endDate": end_date.strftime("%Y-%m-%d"),
                    }
                ],
                "dimensions": [{"name": "date"}],
                "metrics": [
                    {"name": "activeUsers"},
                    {"name": "sessions"},
                    {"name": "screenPageViews"},
                ],
            },
        ).execute()

        for row in ga_response.get("rows", []):
            ga_data.append(
                {
                    "date": (
                        row["dimensionValues"][0]["value"][4:6]
                        + "/"
                        + row["dimensionValues"][0]["value"][6:8]
                    ),
                    "users": row["metricValues"][0]["value"],
                    "sessions": row["metricValues"][1]["value"],
                    "views": row["metricValues"][2]["value"],
                }
            )
    except Exception as e:
        print(f"Erreur GA: {e}")

    service_sc = build("searchconsole", "v1", credentials=credentials)
    search_console_data = []

    try:
        sc_response = service_sc.searchanalytics().query(
            siteUrl=website.url,
            body={
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
                "dimensions": ["query"],
                "rowLimit": 20,
            },
        ).execute()

        for row in sc_response.get("rows", []):
            search_console_data.append(
                {
                    "keyword": row["keys"][0],
                    "clicks": row["clicks"],
                    "impressions": row["impressions"],
                    "ctr": row["ctr"],
                    "position": row["position"],
                }
            )
    except Exception as e:
        print(f"Erreur SC: {e}")

    recommendations = []
    recs = Recommendation.objects.filter(website=website).order_by(
        "priority", "-created_at"
    )
    for rec in recs:
        recommendations.append(
            {
                "title": rec.title,
                "description": rec.description,
                "action": rec.action,
                "priority": rec.priority,
                "recommendation_type": rec.recommendation_type,
            }
        )

    pdf_buffer = generate_seo_report(
        website_name=website.nom_site,
        website_url=website.url,
        ga_data=ga_data,
        search_console_data=search_console_data,
        recommendations=recommendations,
    )

    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="seo_report_{website.nom_site}_{datetime.now().strftime("%Y%m%d")}.pdf"'
    )

    return response
