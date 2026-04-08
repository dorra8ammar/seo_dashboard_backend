from django.db import models
from django.contrib.auth.models import User


class Website(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    nom_site = models.CharField(max_length=255)
    property_id = models.CharField(max_length=100, null=True, blank=True)
    property_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nom_site

class Analysis(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    trafic = models.IntegerField(default=0)
    clics = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    ctr = models.FloatField(default=0.0)
    position = models.FloatField(default=0.0)

    def __str__(self):
        return f"Analyse {self.website.nom_site}"


class Recommendation(models.Model):
    """Modele pour stocker les recommandations SEO generees par l'IA."""

    PRIORITY_CHOICES = [
        (1, "Haute"),
        (2, "Moyenne"),
        (3, "Basse"),
    ]

    TYPE_CHOICES = [
        ("ctr", "Taux de clic"),
        ("position", "Position Google"),
        ("traffic", "Trafic"),
        ("bounce", "Taux de rebond"),
        ("seo", "SEO general"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="recommendations",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    action = models.CharField(max_length=255, blank=True, null=True)
    recommendation_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["priority", "-created_at"]

    def __str__(self):
        return f"{self.title} - {self.website.nom_site}"
