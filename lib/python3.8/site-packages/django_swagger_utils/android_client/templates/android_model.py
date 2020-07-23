ANDROID_MODEL = """{% autoescape off %}package {{android_import_statement}};
import java.io.Serializable;
import android_{{android_app_name}}.models.common.*;

{% if android_model_is_used_as_list %}import java.util.ArrayList;{% endif %}

public class {{android_model_camel_case_name}} implements Serializable{
    {% for key, value in model_parameters %}public {{value}} {{key}};
    {% endfor %}
    public {{android_model_camel_case_name}}({% for key, value in model_parameters %}{{value}} {{key}}{%if not forloop.last%},{%endif%}{% endfor %}) {
        {% for key, value in model_parameters %}this.{{key}} = {{key}};
        {% endfor %}
    }

    public {{android_model_camel_case_name}}(){}

    {% for key, value in model_parameters %}
    public void set_{{key}}({{value}} {{key}}){
        this.{{key}} = {{key}};
    }

    {% endfor %}
    {% if android_model_is_used_as_list %}public static class List extends ArrayList<{{android_model_camel_case_name}}>{
    }{% endif %}
}
{% endautoescape %}
"""
