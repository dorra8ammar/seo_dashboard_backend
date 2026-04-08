import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("analytics_app", "0002_website_property_id_website_property_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="recommendation",
            name="analysis",
        ),
        migrations.RemoveField(
            model_name="recommendation",
            name="contenu",
        ),
        migrations.AddField(
            model_name="recommendation",
            name="action",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="recommendation",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="recommendation",
            name="description",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="recommendation",
            name="is_read",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="recommendation",
            name="priority",
            field=models.IntegerField(
                choices=[(1, "Haute"), (2, "Moyenne"), (3, "Basse")],
                default=2,
            ),
        ),
        migrations.AddField(
            model_name="recommendation",
            name="recommendation_type",
            field=models.CharField(
                choices=[
                    ("ctr", "Taux de clic"),
                    ("position", "Position Google"),
                    ("traffic", "Trafic"),
                    ("bounce", "Taux de rebond"),
                    ("seo", "SEO general"),
                ],
                default="seo",
                max_length=50,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="recommendation",
            name="title",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="recommendation",
            name="website",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recommendations",
                to="analytics_app.website",
            ),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name="recommendation",
            options={"ordering": ["priority", "-created_at"]},
        ),
    ]
