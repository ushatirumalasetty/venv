from django.contrib import admin

from django_swagger_utils import models


class LatencyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'app_name',
        'operation_id',
        'response_time',
        'db_queries_count',
        'db_time',
        'duplicate_queries',
        'total_duplicate_queries',
        'date_time'
    )
    search_fields = (
        'app_name',
        'operation_id',
    )

    list_filter = (
        'app_name',
        'operation_id',
    )


class LastAccessAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'app_name',
        'operation_id',
        'user',
        'created_on',
        'last_updated_on'
    )
    search_fields = (
        'app_name',
        'operation_id',
        'user',
    )

    list_filter = (
        'app_name',
        'operation_id',
        'user',
        'created_on',
        'last_updated_on'
    )


class APICallbackAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'source',
        'app_name',
        'operation_id',
        'post_url',
        'created_on',
        'last_updated_on'
    )
    search_fields = (
        'source',
        'app_name',
        'operation_id',
        'post_url',
    )

    list_filter = (
        'source',
        'app_name',
        'operation_id',
        'post_url',
        'created_on',
        'last_updated_on'
    )


def _register(model, admin_class):
    admin.site.register(model, admin_class)


_register(models.Latency, LatencyAdmin)
_register(models.LastAccess, LastAccessAdmin)
_register(models.APICallback, APICallbackAdmin)
