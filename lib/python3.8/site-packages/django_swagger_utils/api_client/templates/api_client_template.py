api_client_template = """{% load get_type %}{% autoescape off %}from ib_common.service_adapter_utils.base_adapter_class import BaseAdapterClass


class {{app_name_capital}}APIClient(BaseAdapterClass):
    conn = None

    def __init__(self, *args, **kwargs):
        super({{app_name_capital}}APIClient, self).__init__(*args, **kwargs)
        self.setup_conn()

    def setup_conn(self):
        from .interface import {{app_name_capital}}ServiceInterface
        self.conn = {{app_name_capital}}ServiceInterface(self.user, self.access_token, self.source)
    
    {% for endpoint_dict in endpoints %}
    def {{endpoint_dict.operation_id}}(self, {% if endpoint_dict.path_params.keys %}{{ endpoint_dict.path_params.keys | join:', ' }}, {% endif %}{% if endpoint_dict.request_query_params.keys %}{{ endpoint_dict.request_query_params.keys | join:', ' }}, {% endif %}{% if endpoint_dict.request_headers_params.keys %}{{ endpoint_dict.request_headers_params.keys | join:', ' }}, {% endif %}{% if endpoint_dict.request_body_serializer_is_array %} *items{% else %} {% if endpoint_dict.request_body_dict.keys %}{{ endpoint_dict.request_body_dict.keys | join:', ' }}, {% endif %}{% endif %}):
        \"\"\"
        
        Summary: {{endpoint_dict.summary}}
        
        Description: {{endpoint_dict.description}}
        
        {% if endpoint_dict.request_body_serializer_is_array %}:items: list, Ex: {{endpoint_dict.request_body_sample_json}} {% elif endpoint_dict.request_body_dict.keys %} {% for each_param, data in endpoint_dict.request_body_dict.items %}
        :{{each_param}} {{data|get_type}}, Ex: {{data}} {% endfor %} 
        {% endif %}{% if endpoint_dict.path_params.keys %} {% for each_param, data in endpoint_dict.path_params.items %}
        :{{each_param}} {{data|get_type}}, Ex: {{data}} {% endfor %} 
        {% endif %}{% if endpoint_dict.request_headers_params.keys %} {% for each_param, data in endpoint_dict.request_headers_params.items %}
        :{{each_param}} {{data|get_type}}, Ex: {{data}} {% endfor %}
        {% endif %}{% if endpoint_dict.request_query_params.keys %} {% for each_param, data in endpoint_dict.request_query_params.items %}
        :{{each_param}} {{data|get_type}}, Ex: {{data}} {% endfor %} 
        {% endif %}
        
        :returns  
        
{{endpoint_dict.responses.200.response_serializer_sample_json}}    
        
        \"\"\"
        {% if endpoint_dict.request_body_serializer_is_array %} 
        request_data = items 
        {% elif endpoint_dict.request_body_dict.keys %} 
        request_data = {{% for each_param, data in endpoint_dict.request_body_dict.items %}
            '{{each_param}}': {{each_param}},{% endfor %} 
        } 
        {% endif %}{% if endpoint_dict.path_params.keys %} 
        path_params = {{% for each_param, data in endpoint_dict.path_params.items %}
            '{{each_param}}': {{each_param}},{% endfor %} 
        } 
        {% endif %}{% if endpoint_dict.request_headers_params.keys %} 
        headers_obj = {{% for each_param, data in endpoint_dict.request_headers_params.items %}
            '{{each_param}}': {{each_param}},{% endfor %} 
        } 
        {% endif %}{% if endpoint_dict.request_query_params.keys %} 
        query_params = {{% for each_param, data in endpoint_dict.request_query_params.items %}
            '{{each_param}}': {{each_param}},{% endfor %} 
        } 
        {% endif %}
        return self.execute(self.conn.{{endpoint_dict.operation_id}}{% if endpoint_dict.request_body_serializer_is_array or endpoint_dict.request_body_dict.keys %}, request_data=request_data {% endif%}{% if endpoint_dict.path_params.keys %}, path_params=path_params {% endif%}{% if endpoint_dict.request_headers_params.keys %}, headers_obj=headers_obj {% endif%}{% if endpoint_dict.request_query_params.keys %}, query_params=query_params {% endif%})
    {% endfor %}
{% endautoescape %}"""
