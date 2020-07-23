from rest_framework import serializers


def deserialize(serializer_class, data, **kwargs):
    if serializer_class and data is not None:
        serializer = serializer_class(data=data, **kwargs)
        if serializer.is_valid(raise_exception=True):
            if issubclass(serializer_class, serializers.ListSerializer):
                return serializer.data, serializer.validated_data
            else:
                input_type_obj = serializer.save()
                return input_type_obj, serializer.validated_data
        else:
            from django_swagger_utils.drf_server.exceptions.validation_error import ValidationError
            raise ValidationError(str(serializer.errors))
    return None, None
