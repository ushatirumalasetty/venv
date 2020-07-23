from rest_framework import serializers

__author__ = 'anush0247'


class BaseRequestType(object):
    def __init__(self, data, clientKeyDetailsId):
        self.data = data
        self.clientKeyDetailsId = clientKeyDetailsId


class BaseRequestSerializer(serializers.Serializer):
    data = serializers.CharField()
    clientKeyDetailsId = serializers.IntegerField()

    def create(self, validated_data):
        return BaseRequestType(**validated_data)
