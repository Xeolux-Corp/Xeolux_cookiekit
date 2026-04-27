"""
urls.py — Routes publiques de xeolux_cookiekit.

Inclure dans votre urls.py principal :

    from django.urls import path, include

    urlpatterns = [
        ...
        path("", include("xeolux_cookiekit.urls")),
    ]

Cela expose :
  /cookiekit/   → tableau de bord (login + permission requis)
"""

from django.urls import path

from xeolux_cookiekit.views import cookiekit_dashboard

app_name = "xeolux_cookiekit"

urlpatterns = [
    path("cookiekit/", cookiekit_dashboard, name="dashboard"),
]
