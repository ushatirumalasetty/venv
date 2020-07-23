# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

app_name = 'django_swagger_utils'

urlpatterns = [
    url(r'^chartit/',views.chartit,name='chartit'),
    url(r'^(?P<path>.*)/?$', views.swagger_ui, name='swagger_ui'),
]
