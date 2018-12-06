"""external-data-scrapers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from apps.ovfiets import views as ovfiets_views


class ExternalDataView(routers.APIRootView):
    """
    List of external APIs that are scraped by the external-data-scrapers

    Daily scraped APIs
    ==================
    - OvFiets (every 5 minutes)

    [github/amsterdam/external-data-scrapers](https://github.com/Amsterdam/external-data-scrapers)

    [Author: y.elsherbini](https://github.com/yelsherbini/)
    """


class ExternalDataRouter(routers.DefaultRouter):
    APIRootView = ExternalDataView


router = ExternalDataRouter()
router.register(r'ovfiets', ovfiets_views.OvFietsView)

urls = router.urls

schema_view = get_schema_view(
    openapi.Info(
        title="External data scrapers",
        default_version='v1',
        description="One spot for scraping external data",
        terms_of_service="https://data.amsterdam.nl/",
        contact=openapi.Contact(email="datapunt@amsterdam.nl"),
        license=openapi.License(name="CC0 1.0 Universal"),
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('status/', include('apps.health.urls')),
    path('externaldata/', include(urls)),

    url(r'^externaldata/swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^externaldata/swagger/$',
        schema_view.with_ui('swagger', cache_timeout=None),
        name='schema-swagger-ui'),
    url(r'^externaldata/redoc/$',
        schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend([
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ])
