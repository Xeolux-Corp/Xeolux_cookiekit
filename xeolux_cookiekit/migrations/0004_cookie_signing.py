from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("xeolux_cookiekit", "0003_analyticskit_bridge"),
    ]

    operations = [
        migrations.AddField(
            model_name="cookiekitconfig",
            name="cookie_signing_enabled",
            field=models.BooleanField(
                default=True,
                verbose_name="Signature HMAC activée",
                help_text=(
                    "Active la signature HMAC-SHA256 du cookie de consentement. "
                    "Un cookie HttpOnly supplémentaire (_sig) est posé côté serveur."
                ),
            ),
        ),
    ]
