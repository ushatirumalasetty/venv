import copy
import inspect

from django.utils import html
from rest_framework import serializers
from rest_framework.fields import _UnvalidatedField, empty


class CollectionFormatField(serializers.Field):
    child = _UnvalidatedField()

    def __init__(self, *args, **kwargs):
        self.child = kwargs.pop('child', copy.deepcopy(self.child))
        self.separator = kwargs.pop("separator")
        self.allow_empty = kwargs.pop('allow_empty', True)

        assert not inspect.isclass(self.child), '`child` has not been instantiated.'
        assert self.child.source is None, (
            "The `source` argument is not meaningful when applied to a `child=` field. "
            "Remove `source=` from the field declaration."
        )
        super(CollectionFormatField, self).__init__(*args, **kwargs)

        self.child.bind(field_name='', parent=self)

    def get_value(self, dictionary):
        if self.field_name not in dictionary:
            if getattr(self.root, 'partial', False):
                return empty
        # We override the default field access in order to support
        # lists in HTML forms.
        if html.is_html_input(dictionary):
            val = dictionary.getlist(self.field_name, [])
            if len(val) > 0:
                # Support QueryDict lists in HTML input.
                return val
            return html.parse_html_list(dictionary, prefix=self.field_name)
        return dictionary.get(self.field_name, empty)

    def to_representation(self, obj):
        """
        python object (list) --> data string [ serialization ]
        """
        return self.separator.join([self.child.to_representation(item) for item in obj])

    def to_internal_value(self, data):
        """
        data string --> python object (list) [ deserialization ]
        """
        return [[self.child.run_validation(item) for item in data.split(self.separator)]]
