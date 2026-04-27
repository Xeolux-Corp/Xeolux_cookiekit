from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("xeolux_cookiekit", "0004_cookie_signing"),
    ]

    operations = [
        # --- LinkedIn Insight Tag ---
        migrations.AddField(
            model_name="cookiekitconfig",
            name="linkedin_insight_enabled",
            field=models.BooleanField(default=False, verbose_name="LinkedIn Insight Tag activé"),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="linkedin_partner_id",
            field=models.CharField(
                blank=True, default="", max_length=50,
                verbose_name="LinkedIn Partner ID",
                help_text="Exemple : 1234567",
            ),
        ),
        # --- TikTok Pixel ---
        migrations.AddField(
            model_name="cookiekitconfig",
            name="tiktok_pixel_enabled",
            field=models.BooleanField(default=False, verbose_name="TikTok Pixel activé"),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="tiktok_pixel_id",
            field=models.CharField(
                blank=True, default="", max_length=50,
                verbose_name="TikTok Pixel ID",
                help_text="Exemple : C3XXXXXXXXXXXXXXXX",
            ),
        ),
        # --- Twitter/X Pixel ---
        migrations.AddField(
            model_name="cookiekitconfig",
            name="twitter_pixel_enabled",
            field=models.BooleanField(default=False, verbose_name="Twitter / X Pixel activé"),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="twitter_pixel_id",
            field=models.CharField(
                blank=True, default="", max_length=50,
                verbose_name="Twitter / X Pixel ID",
                help_text="Exemple : o2345 (Universal Website Tag)",
            ),
        ),
        # --- Microsoft Clarity ---
        migrations.AddField(
            model_name="cookiekitconfig",
            name="clarity_enabled",
            field=models.BooleanField(default=False, verbose_name="Microsoft Clarity activé"),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="clarity_project_id",
            field=models.CharField(
                blank=True, default="", max_length=50,
                verbose_name="Clarity Project ID",
                help_text="Exemple : abcde12345",
            ),
        ),
        # --- Hotjar ---
        migrations.AddField(
            model_name="cookiekitconfig",
            name="hotjar_enabled",
            field=models.BooleanField(default=False, verbose_name="Hotjar activé"),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="hotjar_site_id",
            field=models.CharField(
                blank=True, default="", max_length=20,
                verbose_name="Hotjar Site ID",
                help_text="Exemple : 1234567",
            ),
        ),
        # --- Crisp Chat ---
        migrations.AddField(
            model_name="cookiekitconfig",
            name="crisp_enabled",
            field=models.BooleanField(default=False, verbose_name="Crisp Chat activé"),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="crisp_website_id",
            field=models.CharField(
                blank=True, default="", max_length=100,
                verbose_name="Crisp Website ID",
                help_text="Exemple : xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            ),
        ),
    ]
