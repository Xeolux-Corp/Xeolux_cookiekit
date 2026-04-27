"""
Migration 0008 — Suppression des champs d'intégration individuels de CookieKitConfig.

Les intégrations sont désormais gérées par CookieKitIntegration (migration 0007).
"""

from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("xeolux_cookiekit", "0007_cookiekitintegration"),
    ]

    operations = [
        # Google Analytics
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="google_analytics_enabled",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="google_analytics_id",
        ),
        # Google Tag Manager
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="google_tag_manager_enabled",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="google_tag_manager_id",
        ),
        # Meta Pixel
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="meta_pixel_enabled",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="meta_pixel_id",
        ),
        # Matomo
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="matomo_enabled",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="matomo_site_id",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="matomo_tracker_url",
        ),
        # Plausible
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="plausible_enabled",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="plausible_domain",
        ),
        # LinkedIn Insight
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="linkedin_insight_enabled",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="linkedin_partner_id",
        ),
        # TikTok Pixel
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="tiktok_pixel_enabled",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="tiktok_pixel_id",
        ),
        # Twitter/X Pixel
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="twitter_pixel_enabled",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="twitter_pixel_id",
        ),
        # Microsoft Clarity
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="clarity_enabled",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="clarity_project_id",
        ),
        # Hotjar
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="hotjar_enabled",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="hotjar_site_id",
        ),
        # Crisp Chat
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="crisp_enabled",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="crisp_website_id",
        ),
    ]
