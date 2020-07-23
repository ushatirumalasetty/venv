# coding=utf-8
from rest_framework.renderers import JSONRenderer
from rest_framework_xml.renderers import XMLRenderer

RENDERER_MAPPING = {
    "application/json": JSONRenderer,
    "application/xml": XMLRenderer,
}