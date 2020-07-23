# coding=utf-8
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework_xml.parsers import XMLParser

PARSER_MAPPING = {
    "application/json": JSONParser,
    "application/xml": XMLParser,
    "application/x-www-form-urlencoded": FormParser,
    "multipart/form-data": MultiPartParser,
}
