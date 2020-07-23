ANDROID_REQUEST = """{% autoescape off %}package {{android_import_statement}};
import java.io.Serializable;
{% if android_common_models_import_statement%}import {{android_common_models_import_statement}}.*;{% endif %}
{% if android_req_is_array %}import java.util.ArrayList;{% endif %}
import java.io.Serializable;

public class {{android_request_camel_case_name}}Request implements Serializable{
    {% for key, value in req_parameters %}public {{value}} {{key}};
    {% endfor %}
    public {{android_request_camel_case_name}}Request({%for key, value in req_parameters%} {{value}} {{key}}{%if not forloop.last%},{%endif%}{% endfor %}) {
        {%for key, value in req_parameters%}this.{{key}} = {{key}};
        {% endfor %}
    }

    {% if android_req_parameters_are_optional %}
    public {{android_request_camel_case_name}}Request(){}
    {% for key, value in req_parameters %}
    public void set_{{key}}({{value}} {{key}}){
        this.{{key}} = {{key}};
    }
    {% endfor %}
    {% endif %}

    {% if android_req_is_array %}public static class List extends ArrayList<{{android_request_camel_case_name}}>{
    }{% endif %}
}
{% endautoescape %}
"""
