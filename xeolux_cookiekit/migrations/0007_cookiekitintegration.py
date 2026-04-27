"""
Migration 0007 — Création du modèle CookieKitIntegration.

Remplace les 22 champs individuels d'intégration de CookieKitConfig par
un modèle dédié avec JSONField extensible.
"""

from __future__ import annotations

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("xeolux_cookiekit", "0006_remove_custom_scripts_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="CookieKitIntegration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        max_length=100,
                        unique=True,
                        verbose_name="Identifiant (slug)",
                        help_text="Identifiant technique immuable. Ex : google_analytics, meta_pixel.",
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        max_length=100,
                        verbose_name="Nom affiché",
                    ),
                ),
                (
                    "enabled",
                    models.BooleanField(
                        default=False,
                        verbose_name="Actif",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("analytics", "Analytics"),
                            ("marketing", "Marketing"),
                            ("preferences", "Préférences / Chat"),
                            ("necessary", "Nécessaires"),
                        ],
                        default="analytics",
                        max_length=50,
                        verbose_name="Catégorie de consentement",
                    ),
                ),
                (
                    "config",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        verbose_name="Configuration",
                        help_text=(
                            "Paramètres spécifiques au format JSON. "
                            'Ex : {"measurement_id": "G-XXXXXXXX"} pour Google Analytics.'
                        ),
                    ),
                ),
                (
                    "order",
                    models.PositiveSmallIntegerField(
                        default=0,
                        verbose_name="Ordre d'affichage",
                    ),
                ),
            ],
            options={
                "verbose_name": "Intégration",
                "verbose_name_plural": "Intégrations",
                "ordering": ["order", "slug"],
            },
        ),
    ]
