# Generated migration — v1.2.1
# - Fix existing cachekit_version_key='cookiekit' → 'cookies'
# - Add banner_color_scheme, banner_animation, banner_backdrop_blur, dashboard_theme

from django.db import migrations, models


def fix_cachekit_version_key(apps, schema_editor):
    """Met à jour les lignes DB dont cachekit_version_key vaut l'ancienne valeur 'cookiekit'."""
    Config = apps.get_model("xeolux_cookiekit", "CookieKitConfig")
    Config.objects.filter(cachekit_version_key="cookiekit").update(
        cachekit_version_key="cookies"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("xeolux_cookiekit", "0008_remove_integration_fields"),
    ]

    operations = [
        # 1. Correction de la valeur par défaut du champ existant
        migrations.AlterField(
            model_name="cookiekitconfig",
            name="cachekit_version_key",
            field=models.CharField(
                default="cookies",
                max_length=100,
                verbose_name="Clé de version CacheKit",
            ),
        ),
        # 2. Migration data : ancienne valeur 'cookiekit' → 'cookies'
        migrations.RunPython(fix_cachekit_version_key, migrations.RunPython.noop),
        # 3. Nouveaux champs apparence
        migrations.AddField(
            model_name="cookiekitconfig",
            name="banner_color_scheme",
            field=models.CharField(
                choices=[
                    ("dark", "Sombre"),
                    ("light", "Clair"),
                    ("auto", "Automatique (système)"),
                ],
                default="dark",
                help_text="Thème de couleur appliqué au bandeau de consentement.",
                max_length=10,
                verbose_name="Thème du bandeau",
            ),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="banner_animation",
            field=models.CharField(
                choices=[
                    ("slide", "Glissement"),
                    ("fade", "Fondu"),
                    ("none", "Aucune"),
                ],
                default="slide",
                max_length=10,
                verbose_name="Animation du bandeau",
            ),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="banner_backdrop_blur",
            field=models.BooleanField(
                default=False,
                help_text="Applique un flou derrière le bandeau. Effet glassmorphism.",
                verbose_name="Effet verre dépoli (backdrop blur)",
            ),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="dashboard_theme",
            field=models.CharField(
                choices=[
                    ("dark", "Sombre"),
                    ("light", "Clair"),
                    ("auto", "Automatique (système)"),
                ],
                default="dark",
                help_text="Thème de couleur du dashboard CookieKit.",
                max_length=10,
                verbose_name="Thème du dashboard",
            ),
        ),
    ]
