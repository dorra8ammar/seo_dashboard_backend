from rest_framework import serializers

from .models import Analysis, Recommendation, Website


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ["id", "url", "nom_site", "property_id", "property_name"]


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = '__all__'


class RecommendationSerializer(serializers.ModelSerializer):
    priority_label = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = [
            "id",
            "title",
            "description",
            "action",
            "recommendation_type",
            "priority",
            "priority_label",
            "is_read",
            "created_at",
        ]

    def get_priority_label(self, obj):
        priority_map = {1: "Haute", 2: "Moyenne", 3: "Basse"}
        return priority_map.get(obj.priority, "Moyenne")
