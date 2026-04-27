from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("xeolux_cookiekit", "0002_cookiekitconfig_privacy_policy"),
    ]

    operations = [
        migrations.AddField(
            model_name="cookiekitconfig",
            name="analyticskit_bridge_enabled",
            field=models.BooleanField(
                default=False,
                verbose_name="Bridge AnalyticsKit activé",
            ),
        ),
        # Ajout du help_text sur cookie_max_age_days (pas de changement de schéma)
        migrations.AlterField(
            model_name="cookiekitconfig",
            name="cookie_max_age_days",
            field=models.PositiveIntegerField(
                default=180,
                verbose_name="Durée du cookie (jours)",
                help_text="CNIL : 6 mois recommandés, 13 mois maximum autorisés (395 jours).",
            ),
        ),
    ]
