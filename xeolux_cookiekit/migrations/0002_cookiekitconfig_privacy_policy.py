from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("xeolux_cookiekit", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cookiekitconfig",
            name="privacy_policy_url",
            field=models.URLField(
                blank=True,
                default="",
                max_length=500,
                verbose_name="URL politique de confidentialité / cookies",
            ),
        ),
        migrations.AddField(
            model_name="cookiekitconfig",
            name="privacy_policy_label",
            field=models.CharField(
                default="Politique de confidentialité",
                max_length=100,
                verbose_name="Libellé lien politique de confidentialité",
            ),
        ),
    ]
