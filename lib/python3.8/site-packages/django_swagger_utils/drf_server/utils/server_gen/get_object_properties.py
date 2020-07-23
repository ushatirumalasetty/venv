def get_object_properties(prop_name, schema_properties, paths, base_path,
                          to_file=True):
    from django_swagger_utils.drf_server.generators.serializer_generator import \
        SerializerGenerator
    serializer_generator = SerializerGenerator(
        schema_properties=schema_properties, base_path=base_path,
        serializer_name=prop_name, paths=paths)
    context_properties = serializer_generator.generate_serializer_file(
        to_file=to_file)
    return context_properties
