models = """{% autoescape off %}from enum import Enum
from ib_common.constants.base_enum_class import BaseEnumClass

__author__ = 'tanmay.ibhubs'

{% for class_name, variables in classes %}
class {{class_name}}(BaseEnumClass, Enum):
    {% for var_name in variables %}{{var_name}} = "{{var_name}}"
    {% endfor %}
{% endfor %}
{% endautoescape %}
"""
