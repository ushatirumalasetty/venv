# -*- coding: utf-8 -*-
from django.db import models


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated_on = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True


class Latency(models.Model):
    app_name = models.CharField(max_length=100)
    operation_id = models.CharField(max_length=500)
    response_time = models.FloatField()
    date_time = models.DateTimeField(auto_now_add=True)
    db_queries_count = models.IntegerField(default=0)
    db_queries = models.TextField(max_length=1000000, blank=True, default="")
    db_time = models.FloatField(default=0)
    duplicate_queries = models.IntegerField(default=0)
    total_duplicate_queries = models.IntegerField(default=0)

    class Meta(object):
        verbose_name_plural = 'Latencies'


class LastAccess(BaseModel):
    from django.conf import settings
    app_name = models.CharField(max_length=100)
    operation_id = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                             on_delete=models.CASCADE)

    class Meta(object):
        unique_together=(('app_name','operation_id','user'))


class APICallback(BaseModel):
    source = models.CharField(max_length=200)
    app_name = models.CharField(max_length=100)
    operation_id = models.CharField(max_length=500)
    post_url = models.CharField(max_length=300)
