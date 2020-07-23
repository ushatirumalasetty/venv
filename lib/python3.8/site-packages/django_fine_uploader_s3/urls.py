"""django_fine_uploader_s3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from django_fine_uploader_s3 import views

urlpatterns = [
    url(r'^s3/signature', views.handle_POST, name="s3_signee"),
    url(r'^s3/delete', views.handle_DELETE, name='s3_delete'),
    url(r'^s3/success', views.success_redirect_endpoint, name="s3_success_endpoint"),
    url(r'^s3/sign', views.sign_s3_upload, name="sign_s3_upload")
]
