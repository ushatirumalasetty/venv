ANDROID_SPICE_REQUEST = """{% autoescape off %}package {{android_import_statement}}.network.spice_requests;

import {{android_import_statement}}.network.{{android_app_name}}ServerCommands;
{% if android_model %}import {{android_import_statement}}.models.common.{{android_model}};{%endif%}
{% if not android_model %}{%if android_req_parameters or android_req_is_single_array %}import {{android_import_statement}}.models.requests.{{android_spice_request_camel_case_name}}.*;{%endif%}{%endif%}
{%if not android_res_model%}{%if android_res_parameters%}import {{android_import_statement}}.models.responses.{{android_spice_request_camel_case_name}}.*;{%endif%}{%endif%}
{%if android_res_model%}import {{android_import_statement}}.models.common.{{android_res_model}};{%endif%}
import java.util.ArrayList;

import com.octo.android.robospice.request.retrofit2.RetrofitSpiceRequest;
import com.google.gson.Gson;
import com.octo.android.robospice.persistence.exception.SpiceException;
import retrofit2.Response;

public class {{android_spice_request_camel_case_name}}SpiceRequest extends RetrofitSpiceRequest<{%if android_res_is_single_type_array%}{{android_res_is_single_type_array}}{%else%}{%if not android_res_model%}{%if android_res_parameters%}{{android_spice_request_camel_case_name}}Response{%endif%}{%if not android_res_parameters%}Void{%endif%}{%endif%}{%if android_res_model%}{{android_res_model}}{%endif%}{% if android_res_is_array %}{{android_res_is_array}}{% endif %}{%endif%}, {{android_app_name}}ServerCommands>{

    {%if android_req_is_single_type_array%}{{android_req_is_single_type_array}} {{android_spice_request_variable_name}}Request;{%endif%}{%if not android_model%}{% if android_req_parameters %}{{android_spice_request_camel_case_name}}Request{% if android_req_is_array %}{{android_req_is_array}}{% endif %} {{android_spice_request_variable_name}}Request;{%endif%}{%endif%}
    {%if android_model%}{{android_model}}{%if android_req_is_array%}{{android_req_is_array}}{%endif%} {{android_model | lower}};{%endif%}
    {% for key, value in android_path_parameters %}public {{value}} {{key}};
    {%endfor%}
    {% for key, value in android_query_parameters %}public {{value}} {{key}};
    {%endfor%}
    public {{android_spice_request_camel_case_name}}SpiceRequest({%if android_req_is_single_type_array%}{{android_req_is_single_type_array}} {{android_spice_request_variable_name}}Request{%endif%}{%if not android_model%}{%if android_req_parameters%}{{android_spice_request_camel_case_name}}Request{% if android_req_is_array %}{{android_req_is_array}}{% endif %} {{android_spice_request_variable_name}}Request{%endif%}{%if android_path_parameters%}{%if android_req_parameters or android_req_is_single_type_array%},{%endif%}{%endif%}{%endif%}{%if android_model %}{{android_model}}{% if android_req_is_array %}{{android_req_is_array}}{% endif %} {{android_model | lower}}{%if android_path_parameters%},{%endif%}{%endif%}{%for key, value in android_path_parameters%} {{value}} {{key}}{%if not forloop.last%},{%endif%}{%if forloop.last%}{% if android_query_parameters%},{%endif%}{%endif%}{% endfor %}{%for key, value in android_query_parameters%}{{value}} {{key}}{%if not forloop.last%},{%endif%}{% endfor %}) {
        super({%if android_res_is_single_type_array%}{{android_res_is_single_type_array}}{%else%}{%if not android_res_model%}{%if android_res_parameters%}{{android_spice_request_camel_case_name}}Response{%endif%}{%if not android_res_parameters%}Void{%endif%}{%endif%}{%if android_res_model%}{{android_res_model}}{%endif%}{% if android_res_is_array %}{{android_res_is_array}}{% endif %}{%endif%}.class, {{android_app_name}}ServerCommands.class);
        {%if not android_model%}{% if android_req_parameters or android_req_is_single_type_array%}this.{{android_spice_request_variable_name}}Request = {{android_spice_request_variable_name}}Request;{%endif%}{%endif%}
        {%if android_model%}this.{{android_model | lower}} = {{android_model | lower}};{%endif%}
        {%for key, value in android_path_parameters%}this.{{key}} = {{key}};
        {% endfor %}
        {%for key, value in android_query_parameters%}this.{{key}} = {{key}};
        {% endfor %}
    }

    @Override
    public {%if android_res_is_single_type_array%}{{android_res_is_single_type_array}}{%else%}{%if not android_res_model%}{%if android_res_parameters%}{{android_spice_request_camel_case_name}}Response{%endif%}{%if not android_res_parameters%}Void{%endif%}{%endif%}{%if android_res_model%}{{android_res_model}}{%endif%}{% if android_res_is_array %}{{android_res_is_array}}{% endif %}{%endif%} loadDataFromNetwork() throws Exception {
        Response<{%if android_res_is_single_type_array%}{{android_res_is_single_type_array}}{%else%}{%if not android_res_model%}{%if android_res_parameters%}{{android_spice_request_camel_case_name}}Response{%endif%}{%if not android_res_parameters%}Void{%endif%}{%endif%}{%if android_res_model%}{{android_res_model}}{%endif%}{% if android_res_is_array %}{{android_res_is_array}}{% endif %}{%endif%}> responseTypeResponse = getService().{{android_spice_request_variable_name}}({%if android_req_is_single_type_array%}{{android_spice_request_variable_name}}Request{%if android_path_parameters%},{%endif%}{%endif%}{%if not android_model%}{%if android_req_parameters%}{% if android_req_is_array %}{{android_spice_request_variable_name}}Request{% endif %}{% if not android_req_is_array %}{{android_spice_request_variable_name}}Request{% endif %}{%if android_path_parameters%},{%endif%}{%endif%}{%endif%}{%if android_model %}{{android_model | lower}}{%if android_path_parameters%},{%endif%}{%endif%}{%for key, value in android_path_parameters%}{{key}}{%if not forloop.last%},{%endif%}{%if forloop.last%}{% if android_query_parameters%},{%endif%}{%endif%}{% endfor %}{%for key, value in android_query_parameters%}{{key}}{%if not forloop.last%},{%endif%}{% endfor %}).clone().execute();
        if (!responseTypeResponse.isSuccessful()) {
        Gson gson = new Gson();
        String json2 = gson.toJson(responseTypeResponse.errorBody().string());
        throw new SpiceException(json2 + "@" + responseTypeResponse.code());
        }
        return responseTypeResponse.body();
    }
}
    {% endautoescape %}
"""
