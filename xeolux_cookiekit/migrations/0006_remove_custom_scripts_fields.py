from django.db import migrations


class Migration(migrations.Migration):
    """
    Supprime les champs custom_head_scripts et custom_body_scripts de CookieKitConfig.
    Les scripts personnalisés sont désormais gérés exclusivement via le modèle CookieScript,
    accessible dans Admin → Xeolux CookieKit → Scripts personnalisés.
    """

    dependencies = [
        ("xeolux_cookiekit", "0005_new_integrations"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="custom_head_scripts",
        ),
        migrations.RemoveField(
            model_name="cookiekitconfig",
            name="custom_body_scripts",
        ),
    ]
