from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from lumber import views

app_name = 'lumber'
urlpatterns = [
    path('app', views.AppView.as_view(), name='app'),
    path('sink/<uuid:dsn>', views.LogView.as_view(), name='sink'),
    path('api/apps', views.AppsApiView.as_view(), name='apps'),
    path('api/logs/<uuid:app_id>', views.LogsApiView.as_view(), name='logs'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
