"""
Migration 0010 — Palette light configurable + options avancées du bandeau

Nouveaux champs :
  - light_background_color, light_text_color, light_primary_color,
    light_primary_text_color, light_secondary_color, light_secondary_text_color,
    light_border_color
  - banner_max_width, banner_font_size, banner_padding,
    banner_border_color, banner_border_radius_mobile, banner_overlay
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("xeolux_cookiekit", "0009_appearance_fields_and_cachekit_fix"),
    ]

    operations = [
        # ── Palette claire configurable ───────────────────────────────────
        migrations.AddField(
            model_name="cookiekitconfig",
            name="light_background_color",
            field=models.CharField(
                default="#f5f5f7",
                max_length=20,
                verbose_name="Fond clair",
                help_text="Utilisé quand le bandeau est en mode 'Clair' ou 'Auto' + OS en mode clair.",
            ),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="light_text_color",
            field=models.CharField(default="#1d1d1f", max_length=20, verbose_name="Texte clair"),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="light_primary_color",
            field=models.CharField(default="#e05e00", max_length=20, verbose_name="Couleur primaire (clair)"),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="light_primary_text_color",
            field=models.CharField(default="#ffffff", max_length=20, verbose_name="Texte bouton primaire (clair)"),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="light_secondary_color",
            field=models.CharField(default="#e0e0e5", max_length=20, verbose_name="Couleur secondaire (clair)"),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="light_secondary_text_color",
            field=models.CharField(default="#1d1d1f", max_length=20, verbose_name="Texte bouton secondaire (clair)"),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="light_border_color",
            field=models.CharField(
                blank=True,
                default="#e5e5ea",
                max_length=20,
                verbose_name="Bordure (clair)",
                help_text="Laissez vide pour désactiver la bordure en mode clair.",
            ),
        ),
        # ── Options avancées du bandeau ───────────────────────────────────
        migrations.AddField(
            model_name="cookiekitconfig",
            name="banner_max_width",
            field=models.CharField(
                default="680px",
                max_length=20,
                verbose_name="Largeur maximale",
                help_text="Valeur CSS. Ex : 680px, 90vw.",
            ),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="banner_font_size",
            field=models.CharField(
                default="15px",
                max_length=20,
                verbose_name="Taille du texte",
                help_text="Valeur CSS pour font-size. Ex : 14px, 0.9rem.",
            ),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="banner_padding",
            field=models.CharField(
                default="1.5rem 2rem",
                max_length=30,
                verbose_name="Padding interne",
                help_text="Valeur CSS pour padding. Ex : 1.5rem 2rem, 20px 24px.",
            ),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="banner_border_color",
            field=models.CharField(
                blank=True,
                default="",
                max_length=20,
                verbose_name="Bordure (sombre)",
                help_text="Couleur de bordure en mode sombre. Laissez vide pour désactiver.",
            ),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="banner_border_radius_mobile",
            field=models.CharField(
                default="0px",
                max_length=20,
                verbose_name="Border radius mobile",
                help_text="Border radius sur mobile. Ex : 0px ou 12px.",
            ),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="banner_overlay",
            field=models.BooleanField(
                default=False,
                verbose_name="Overlay sombre (arrière-plan)",
                help_text="Affiche un fond sombre derrière le bandeau modal/flottant.",
            ),
        ),
    ]
