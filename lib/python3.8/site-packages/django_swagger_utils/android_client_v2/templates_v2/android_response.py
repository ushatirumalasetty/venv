ANDROID_RESPONSE = """{% autoescape off %}package {{android_import_statement}};
import java.io.Serializable;
{% if android_common_models_import_statement%}import {{android_common_models_import_statement}}.*;{% endif %}
{% if android_res_is_array %}import java.util.ArrayList;{% endif %}
import java.io.Serializable;

public class {{android_response_camel_case_name}}Response implements Serializable{
    {% if res_parameters %}{% for key, value in res_parameters %}public {{value}} {{key}};
    {% endfor %}{% endif %}

    {% if android_res_parameters_are_optional %}
    public {{android_response_camel_case_name}}Response(){}
    {% for key, value in res_parameters %}
    public void set_{{key}}({{value}} {{key}}){
        this.{{key}} = {{key}};
    }
    {% endfor %}
    {% endif %}

    {% if android_res_is_array %}public static class List extends ArrayList<{{android_response_camel_case_name}}Response>{
    }
    {% endif %}
}
{% endautoescape %}
"""
