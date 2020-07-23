# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.views import logout_then_login
from django.contrib.auth import views as auth_views

app_name = 'django_swagger_utils'

urlpatterns = [
    url(r"^login/$", auth_views.LoginView.as_view(template_name='login.html'),
        name="login"),
    url(r"^logout/$", logout_then_login, name="logout"),
]
