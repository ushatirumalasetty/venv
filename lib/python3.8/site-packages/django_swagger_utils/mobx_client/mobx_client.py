
from django_swagger_utils.core.utils.write_to_file import write_to_file

from .conf import render

__author__ = 'tanmay.ibhubs'

import re
import os


class MobxTemplateGenerator(object):
    def __init__(self, parser, app_name, mobx_base_dir, paths):
        '''
        parser to parse the spec file and appname to store the files are required.
        :param parser:
        :param appname:
        '''
        self.paths = paths
        self.parser = parser
        self.app_name = app_name
        self.mobx_base_dir = mobx_base_dir
        self.primitive_types = ('integer', 'string', 'boolean', 'number')

    def convert_to_snake(self, name):
        '''
        convert name from camelCase to snake_case
        :param name:
        :return:
        '''
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def get_camel(self, column):
        '''
        convert column from snake_case to camelCase
        :param column:
        :return:
        '''
        words = column.split('_')
        first = words[0]
        return first + ''.join((w.capitalize() for w in words[1:]))

    def get_capitalized(self, column):
        '''
        convert column from snake_case to camelCase
        :param column:
        :return:
        '''
        words = column.split('_')
        words = [(w[0].capitalize() + w[1:]) for w in words]
        return ''.join(words)

    def get_camel_from_capitalized(self,
                                   capitalized):  # returns camel cased name from capitalized one
        return capitalized[0].lower() + capitalized[1:]

    def get_self_item(self, each_property, context_dict):
        '''
        This method is being used for the constructor field.
        If the type is array , we just need 'observable([])' to print in the constructor field
        :param each_property:
        :param context_dict:
        :return:
        '''
        if context_dict['flag']:
            context_dict['flag'] = False
            return 'observable([])'
        else:
            return each_property

    def get_default(self, type, property_def, result):
        '''
        This methods is being used to get the default value of any type so as to be used in mobx-classes
        :param type: ->type of which we need to get the default value
        :param property_def: -> in classes it is of complex type like array or object , we need to get its default for
        the mobx class
        :param result:-> specially being used for recursion, in case of array and object
        :return:
        '''
        if type != None:
            if type == 'boolean':
                return "true"
            elif type == 'integer':
                return -1
            elif type == 'number':
                return -1
            elif type == 'string':
                return "\"\""
            elif type == 'array':
                items = property_def.get('items')
                result = '[' + str(
                    self.get_default(items.get('type'), items, result)) + ']'
                return result
            elif type == 'object':
                return ''
            else:
                return ''

    def if_ref(self, property_def):

        """
        :param property_def:
        :return:
        """

        # ref_name has the path $ref is pointing to
        ref_name = property_def['$ref']

        # we split the path to get the actual definition/parameter/
        # response to which it is referring to
        reference_def = ref_name.split('/')[2]
        return reference_def

    def kwargs_append(self, kwargs, field, request_data_field, action,
                      constructor,
                      api_type_field, has_v_kwargs=False):
        """
        appends to the kwargs and returns the kwargs
        :param kwargs:
        :param field:
        :param request_data_field:
        :param action:
        :param constructor:
        :param api_type_field:
        :param has_v_kwargs:
        :return:
        """
        if has_v_kwargs is False:

            kwargs['fields'].append(field)
            kwargs['request_data'].append(request_data_field)
            kwargs['actions'].append(action)
            kwargs['constructor'].append(constructor)
            kwargs['api_model_dict']['fields'].append(api_type_field)
        else:
            kwargs['fields'].extend(field)
            kwargs['request_data'].extend(request_data_field)
            kwargs['actions'].extend(action)
            kwargs['constructor'].extend(constructor)
            kwargs['api_model_dict']['fields'].extend(
                api_type_field)

        return kwargs

    def generate_definitions(self, base_path):
        '''
        This is the driver program which generates definitions.
        :return:
        '''
        for def_name, definition in list(self.parser.definitions().items()):
            self.generate_definition(model_name=def_name, body=definition,
                                     base_path=base_path, is_property=False)

            # if not isinstance(data, type(None)):
            #     write_path = os.path.join(base_path, def_name, 'index' + '.js')
            #     write_to_file(data, write_path, False)

    def generate_definition(self, **kwargs):

        """
        This method initializes all the kwargs and checks the type of kwargs['body'] and
        calls the respective method

        if the module is not called from any sub routine but the
        "generate_definitions" is_property will be false

        :param kwargs:
        :return: kwargs
        """
        # contains model name
        model_name = kwargs['model_name']

        # if imports from other model is there
        kwargs['extra_imports'] = ''

        # if there is import in type.js
        kwargs['api_type_import'] = "API" + model_name

        # to get the capitalised name from the model name
        kwargs['capital_name'] = self.get_capitalized(model_name)

        # to get camel cased name from capitalised name
        kwargs['camel_name'] = self.get_camel_from_capitalized(model_name)

        # If import flag is true that means there is an array field in the
        # model , so we import IObservable array from mobx in the template
        kwargs['import_flag'] = False
        kwargs['flag'] = False

        # fields in index.js
        kwargs['fields'] = []

        # constructor for index.js
        kwargs['constructor'] = []

        # action bound in index.js
        kwargs['actions'] = []
        kwargs['api_model_dict'] = {}
        kwargs['api_model_dict']['import'] = ''
        kwargs['api_model_dict']['enums'] = []
        kwargs['api_model_dict']['class_name'] = 'API' + self.get_capitalized(
            model_name)
        kwargs['api_model_dict']['fields'] = []
        kwargs['request_data'] = []

        if 'to_write' not in kwargs:  # by default we set kwargs['to_write'] to be True
            kwargs['to_write'] = True

        if 'allOf' in kwargs['body']:
            # when the body has allOf we call this
            # definition method
            kwargs = self.generate_all_of_definition(**kwargs)


        elif kwargs['body'].get('type') == 'object':
            # when type is of object type call this
            kwargs = self.generate_object_definition(**kwargs)


        elif kwargs['body'].get('type') == 'array':
            # when type is of array type call this
            kwargs = self.generate_array_definition(**kwargs)

        elif '$ref' in kwargs['body']:
            # when the key inside body is '$ref'  call this
            kwargs = self.generate_ref_definition(**kwargs)

        if kwargs['to_write']:

            # if kwargs['to_write'] is True that means we
            #  have to generate that file
            if 'from_endpoint' in kwargs and kwargs['from_endpoint']:
                # when kwargs['end_point'] is true , we append the
                # kwargs['endpoint_type'] to the write_path
                # both for index.js and type.js

                # joining kwargs['endpoint_type'] in the path
                write_path = os.path.join(kwargs['base_path'], model_name,
                                          kwargs['endpoint_type'], 'type.js')

                # write_to_file writes the passes content into the given
                # path file

                # here we are writing into the api_template
                write_to_file(
                    render('mobx_apimodel.j2', kwargs['api_model_dict']),
                    write_path,
                    False
                )

                write_path = os.path.join(kwargs['base_path'], model_name,
                                          kwargs['endpoint_type'], 'index.js')

                # writing into the mobx_template
                write_to_file(render('mobx_models.j2', kwargs),
                              write_path,
                              False)
            else:

                if 'only_type' in kwargs and kwargs['only_type'] is True:

                    # will be true for parameters snd responses
                    return kwargs
                else:

                    base_path = kwargs['base_path']
                    write_path = os.path.join(base_path, model_name,
                                              'type.js')
                # as there is no endpoint , the(api_template) path will be
                # os.path.join(kwargs['base_path'], model_name,'type.js')
                write_to_file(
                    render('mobx_apimodel.j2', kwargs['api_model_dict']),
                    write_path,
                    False)
                if 'only_type' not in kwargs or kwargs['only_type'] is False:
                    # if not parameter or response , the index.js file will be
                    # generated

                    write_path = os.path.join(kwargs['base_path'], model_name,
                                              'index.js')
                    write_to_file(render('mobx_models.j2', kwargs), write_path,
                                  False)

        return kwargs

    def generate_ref_definition(self, **kwargs):
        """
        sets kwargs['to_write'] to false as we donot expect to to do anything
        when there is $ref as the key while parsing json
        :param kwargs:
        :return:
        """
        kwargs['to_write'] = False
        return kwargs

    def generate_object_definition(self, **kwargs):

        """
        parse the json file(inside the object key ,
        depending on the type of the key present , we perform respective
        definition generations
        :return kwargs: a dictionary containing template fields
        """

        properties = kwargs['body'].get('properties', {})
        model_name = kwargs['model_name']

        # if it is a required field in the spec
        required = kwargs['body'].get('required', [])
        # append model name to kwargs['base_path']
        current_path = os.path.join(kwargs['base_path'], model_name)
        if 'only_type' in kwargs and kwargs['only_type'] is True:
            current_path = kwargs['base_path']

        for each_property in list(properties.keys()):
            property_def = properties[each_property]
            contains_enum = False
            if 'enum' in property_def:
                enum = property_def['enum']
                kwargs['api_model_dict']['enums'].append({
                    'property_name': self.get_capitalized(each_property),
                    'values': enum
                })
                contains_enum = True

            if '$ref' in property_def:
                # if '$ref' is present as the key , all we do is generate
                # index.js file and a type.js file

                reference_def = self.if_ref(property_def)

                # joins reference_def to the 'mobx_base_dir_models' path
                model_path = os.path.join(self.paths['mobx_base_dir_models'],
                                          reference_def)

                # returns the relative version of the path
                relpath = os.path.relpath(model_path, current_path)
                # we import reference_def from the relative path's index.js
                ex_import = 'import ' + reference_def + ' from \'' + str(
                    relpath) + '/' + 'index.js\'\n'

                # import -> type API from relative path's type.js
                ex_api_import = 'import type {API' + self.get_capitalized(
                    reference_def) + '} from \'' + str(
                    relpath) + '/type.js\'\n'

                if ex_import not in kwargs['extra_imports']:
                    kwargs['extra_imports'] += ex_import
                if ex_api_import not in kwargs['api_model_dict']['import']:
                    kwargs['api_model_dict']['import'] += ex_api_import
                is_required = each_property in required
                field = (
                    self.get_camel(each_property), reference_def, is_required)
                request_data_field = (
                    self.get_camel(each_property),
                    self.get_camel(each_property),
                    'object', is_required)
                api_type_field = (
                    each_property, "API" + reference_def, is_required)
                constructor = (self.get_camel(each_property),
                               "new " + self.get_capitalized(
                                   reference_def) + "(" + self.get_camel_from_capitalized(
                                   model_name) + "." + each_property + ")")

                action = (self.get_capitalized(each_property),
                          self.get_camel(each_property),
                          ":" + self.get_capitalized(reference_def),
                          '=' + '{}',
                          "new " + self.get_capitalized(
                              reference_def) + '(' + self.get_camel(
                              each_property) + ')', is_required)

                kwargs = self.kwargs_append(kwargs, field, request_data_field,
                                            action, constructor,
                                            api_type_field)


            elif 'type' in property_def:

                # check the type in the property_def
                prop_type = property_def['type']

                if prop_type in self.primitive_types:

                    if prop_type == 'integer':
                        prop_type = 'number'
                    is_required = each_property in required
                    field = (
                        self.get_camel(each_property), prop_type, is_required)

                    request_data_field = (self.get_camel(each_property),
                                          self.get_camel(each_property),
                                          prop_type, is_required)
                    if contains_enum:
                        api_type_field = (
                            each_property, self.get_capitalized(each_property),
                            is_required)
                    else:
                        api_type_field = (
                            each_property, prop_type, is_required)
                    default_type = self.get_default(prop_type, property_def,
                                                    '')
                    constructor = (
                        self.get_camel(each_property),
                        self.get_self_item(each_property, kwargs)

                    )
                    action = (self.get_capitalized(each_property),
                              self.get_camel(each_property),
                              ':' + str(prop_type), '=' + str(default_type),
                              self.get_camel(each_property), is_required)
                    kwargs = self.kwargs_append(kwargs, field,
                                                request_data_field, action,
                                                constructor, api_type_field)


                elif prop_type == 'object':

                    # only_type is true for only paremeters and responses
                    # as we are expecting only 1 type.js file for all the
                    # parameters , the base_path is kept constant

                    if 'only_type' in kwargs and kwargs['only_type'] is True:
                        base_path = kwargs['base_path']
                    else:
                        base_path = kwargs['base_path'] + "/" + model_name

                    only_type = False
                    if 'only_type' in kwargs:
                        only_type = kwargs['only_type']

                    # {
                    # "FooBar": {
                    #     "type": "object",
                    #     "properties": {
                    #         "foo": {
                    #             "type": "object"
                    #               }
                    #             "properties": ...
                    #     }
                    # }

                    self.generate_definition(
                        model_name=self.get_capitalized(each_property),
                        body=property_def,
                        base_path=base_path, only_type=only_type)

                    ex_import = 'import ' + self.get_capitalized(
                        each_property) + ' from \'./' + self.get_capitalized(
                        each_property) + '/' + 'index.js\'\n'

                    ex_api_import = 'import type {API' + self.get_capitalized(
                        each_property) + '} from \'./' + self.get_capitalized(
                        each_property) + '/type.js\'\n'
                    if ex_import not in kwargs['extra_imports']:
                        kwargs['extra_imports'] += ex_import
                    if ex_api_import not in kwargs['api_model_dict']['import']:
                        kwargs['api_model_dict']['import'] += ex_api_import

                    is_required = each_property in required

                    field = (self.get_camel(each_property),
                             self.get_capitalized(each_property), is_required)
                    request_data_field = (
                        self.get_camel(each_property),
                        self.get_camel(each_property), 'object', is_required)
                    api_type_field = (
                        each_property,
                        "API" + self.get_capitalized(each_property),
                        is_required)
                    constructor = (self.get_camel(each_property),
                                   "new " + self.get_capitalized(
                                       each_property) + "(" + self.get_camel_from_capitalized(
                                       model_name) + "." + each_property + ")")

                    action = (self.get_capitalized(each_property),
                              self.get_camel(each_property),
                              ":" + self.get_capitalized(each_property),
                              '=' + '{}',
                              "new " + self.get_capitalized(
                                  each_property) + '(' + self.get_camel(
                                  each_property) + ')', is_required)
                    kwargs = self.kwargs_append(kwargs, field,
                                                request_data_field, action,
                                                constructor, api_type_field)

                elif prop_type == 'array':

                    # {
                    #     "ArrayObject":{
                    #         "type": "object",
                    #         "properties":{
                    #             "array_obj":{
                    #                 "type": "array",  <--------
                    #                 "items": {
                    #                     ...
                    #                 }
                    #             }
                    #         }
                    #     }
                    # }
                    if 'only_type' in kwargs and kwargs['only_type'] is True:
                        base_path = kwargs['base_path']

                    else:
                        base_path = kwargs['base_path'] + "/" + model_name

                    only_type = False
                    if 'only_type' in kwargs:
                        only_type = kwargs['only_type']
                    v_kwargs = self.generate_definition(
                        model_name=each_property, body=property_def,
                        is_property=True,
                        base_path=base_path + "/" + self.get_capitalized(
                            model_name), only_type=only_type)
                    kwargs = self.kwargs_append(kwargs=kwargs,
                                                field=v_kwargs['fields'],
                                                request_data_field=v_kwargs[
                                                    'request_data'],
                                                action=v_kwargs['actions'],
                                                constructor=v_kwargs[
                                                    'constructor'],
                                                api_type_field=
                                                v_kwargs['api_model_dict'][
                                                    'fields'],
                                                has_v_kwargs=True)

                    if v_kwargs['extra_imports'] not in kwargs[
                        'extra_imports']:
                        kwargs['extra_imports'] += v_kwargs['extra_imports']
                    if v_kwargs['api_model_dict']['import'] not in \
                        kwargs['api_model_dict']['import']:
                        kwargs['api_model_dict']['import'] += \
                            v_kwargs['api_model_dict']['import']
                    kwargs['import_flag'] = True
                    kwargs['api_model_dict']['import_flag'] = True

            elif 'allOf' in property_def:

                # "SampleObject": {
                #     "type": "object",
                #     "properties": {
                #         "field_all_of": {
                #             "allOf": [
                #                 {
                #                     "$ref": "#/definitions/FooBar"
                #                 },
                #                 {
                #                     "$ref": "#/definitions/KeyValue"
                #                 }
                #             ]
                #         }
                #     }
                if 'only_type' in kwargs and kwargs['only_type'] is True:
                    base_path = kwargs['base_path']

                else:
                    base_path = kwargs['base_path'] + "/" + model_name
                only_type = False
                if 'only_type' in kwargs:
                    only_type = kwargs['only_type']
                self.generate_definition(
                    model_name=self.get_capitalized(each_property) + 'Content',
                    body=property_def, is_property=True,
                    base_path=base_path, only_type=only_type)

                ex_import = 'import ' + self.get_capitalized(
                    each_property) + ' from \'./' + self.get_capitalized(
                    each_property) + 'Content' + '/' + 'index.js\'\n'
                ex_api_import = 'import type {API' + self.get_capitalized(
                    each_property) + '} from \'./' + self.get_capitalized(
                    each_property) + 'Content' + '/type.js\'\n'

                if ex_import not in kwargs['extra_imports']:
                    kwargs['extra_imports'] += ex_import
                if ex_api_import not in kwargs['api_model_dict']['import']:
                    kwargs['api_model_dict']['import'] += ex_api_import
                is_required = each_property in required

                field = (self.get_camel(each_property),
                         self.get_capitalized(each_property) + 'Content',
                         is_required)
                request_data_field = (
                    self.get_camel(each_property),
                    self.get_camel(each_property),
                    'object', is_required)
                api_type_field = (each_property, "API" + self.get_capitalized(
                    each_property) + 'Content', is_required)
                constructor = (self.get_camel(each_property),
                               "new " + self.get_capitalized(
                                   each_property) + 'Content' + "(" + self.get_camel_from_capitalized(
                                   model_name) + "." + each_property + ")")

                action = (self.get_capitalized(each_property) + 'Content',
                          self.get_camel(each_property),
                          ":" + self.get_capitalized(
                              each_property) + 'Content', '=' + '{}',
                          "new " + self.get_capitalized(
                              each_property) + 'Content' + '(' + self.get_camel(
                              each_property) + ')', is_required)
                kwargs = self.kwargs_append(kwargs, field, request_data_field,
                                            action, constructor,
                                            api_type_field)

        return kwargs

    def generate_array_definition(self, **kwargs):
        """
         parse the json file(inside the object key ,
        depending on the type of the key present , we perform respective
        definition generations
        :param kwargs:
        :return:
        """
        model_name = kwargs['model_name']
        items = kwargs['body']['items']
        prop_result = 'IObservableArray'
        api_prop_result = prop_result
        default_type = 'observable([])'
        required = kwargs['body'].get('required', [])
        current_path = os.path.dirname(kwargs['base_path'])

        if 'type' in items:
            prop_type = items['type']
            prop_result = 'Array'
            if prop_type in self.primitive_types:
                # {
                # "ArrayOfPrimitives": {
                #              "type": "array",
                #              "items": {
                #                  "type": "string"
                #              }
                #          }
                # }

                kwargs['to_write'] = False
                if prop_type == 'integer':
                    prop_type = 'number'
                prop_result += '<' + prop_type + '>'

                is_required = prop_result in required

                field = (self.get_camel(model_name), prop_result, is_required)
                request_data_field = (
                    self.get_camel(model_name), self.get_camel(model_name),
                    prop_result, is_required)
                constructor = (
                    self.get_camel(model_name),
                    model_name + '.map((item) => new ' + prop_type + '(item))')
                action = (self.get_capitalized(model_name),
                          self.get_camel(model_name), ':' + str(prop_result),
                          '=' + str(default_type),
                          self.get_camel(model_name), is_required)

                api_type_field = (model_name, prop_result, is_required)

                kwargs = self.kwargs_append(kwargs, field, request_data_field,
                                            action, constructor,
                                            api_type_field)



            elif prop_type == 'object':

                # {
                #     "ArrayOfObject": {
                #         "type": "array",
                #         "items": {
                #             "type": "object",
                #             "properties": {
                #                 "abc_a": {
                #                     "type": "string"
                #                 }
                #             }
                #         }
                #     },
                # }

                only_type = False
                if 'only_type' in kwargs:
                    only_type = kwargs['only_type']
                kwargs = self.generate_definition(
                    model_name=self.get_capitalized(model_name), body=items,
                    base_path=kwargs['base_path'], only_type=only_type)

                kwargs['to_write'] = False

                ex_import = 'import ' + self.get_capitalized(
                    model_name) + ' from \'../' + self.get_capitalized(
                    model_name) + '/' + 'index.js\'\n'
                ex_api_import = 'import type {API' + self.get_capitalized(
                    model_name) + '} from \'../' + self.get_capitalized(
                    model_name) + '/type.js\'\n'

                if ex_import not in kwargs['extra_imports']:
                    kwargs['extra_imports'] += ex_import
                if ex_api_import not in kwargs['api_model_dict']['import']:
                    kwargs['api_model_dict']['import'] += ex_api_import

                prop_result += '<' + self.get_capitalized(model_name) + '>'
                api_prop_result += '<' + 'API' + self.get_capitalized(
                    model_name) + '>'
                is_required = prop_result in required

                field = (self.get_camel(model_name), prop_result, is_required)
                request_data_field = (self.get_camel(model_name),
                                      self.get_camel(
                                          model_name) + '.map((item) => item.getRequestData())',
                                      prop_result, is_required)
                api_type_field = (model_name, api_prop_result, is_required)
                constructor = (
                    self.get_camel(model_name),
                    model_name + '.map((item) => new ' + prop_type + '(item))')
                action = (self.get_capitalized(model_name),
                          self.get_camel(model_name), ':' + str(prop_result),
                          '=' + str(default_type),
                          self.get_camel(model_name), is_required)

                kwargs = self.kwargs_append(kwargs, field, request_data_field,
                                            action, constructor,
                                            api_type_field)



            elif prop_type == 'array':

                # {
                #     "ArrayInArray": {
                #         "type": "array",
                #         "items": {
                #             "type": "array",
                #             "items": {
                #                 ....
                #             }
                #         }
                #     }
                #
                #
                # }
                only_type = False
                if 'only_type' in kwargs:
                    only_type = kwargs['only_type']
                kwargs = self.generate_definition(
                    model_name=model_name + 'Content', body=items,
                    base_path=kwargs[
                        'base_path'], only_type=only_type)
                kwargs['to_write'] = False

        if '$ref' in items:
            kwargs['to_write'] = False
            prop_type = self.if_ref(items)

            # joins reference_def to the 'mobx_base_dir_models' path
            model_path = os.path.join(self.paths['mobx_base_dir_models'],
                                      prop_type)
            relpath = os.path.relpath(model_path, current_path)
            # ref_name = items['$ref']
            # prop_type = ref_name.split('/')[2]
            prop_result += '<' + prop_type + '>'
            api_prop_result += '<' + 'API' + prop_type + '>'
            is_required = prop_result in required

            field = (self.get_camel(model_name), prop_result, is_required)
            request_data_field = (self.get_camel(model_name),
                                  self.get_camel(
                                      model_name) + '.map((item) => item.getRequestData())',
                                  prop_result, is_required)
            # we import reference_def from the relative path's index.js
            ex_import = 'import ' + prop_type + ' from \'' + str(
                relpath) + '/' + 'index.js\'\n'

            # import -> type API from relative path's type.js
            ex_api_import = 'import type {API' + self.get_capitalized(
                prop_type) + '} from \'' + str(
                relpath) + '/type.js\'\n'

            if ex_import not in kwargs['extra_imports']:
                kwargs['extra_imports'] += ex_import
            if ex_api_import not in kwargs['api_model_dict']['import']:
                kwargs['api_model_dict']['import'] += ex_api_import

            constructor = (
                self.get_camel(model_name),
                model_name + '.map((item) => new ' + prop_type + '(item))')
            action = (self.get_capitalized(model_name),
                      self.get_camel(model_name), ':' + str(prop_result),
                      '=' + str(default_type),
                      self.get_camel(model_name), is_required)

            api_type_field = (model_name, api_prop_result, is_required)
            kwargs = self.kwargs_append(kwargs, field, request_data_field,
                                        action, constructor,
                                        api_type_field)



        elif 'allOf' in items:

            if 'is_property' in kwargs and kwargs['is_property'] is False:
                #  in this case is_property will be False as allOf is directly
                # inside an array

                # {
                #     "ArrayOfAllOf": {
                #         "type": "array",
                #         "items": {
                #             "allOf": [
                #                 {
                #                     "$ref": "#/definitions/FooBar"
                #                 },
                #                 {
                #                     "$ref": "#/definitions/KeyValue"
                #                 }
                #             ]
                #         }
                #     },
                #
                # }
                parent_to_write = False
                base_path = kwargs['base_path']
            else:
                if 'only_type' in kwargs and kwargs['only_type'] is True:
                    parent_to_write = True
                    base_path = kwargs['base_path']

                # {
                #     "ArrayInArray": {
                #         "type": "array",
                #         "items": {
                #             "type": "array",
                #             "items": {
                #                 "type": "object",
                #                 "properties": {
                #                     "field_all_of": {
                #                         "allOf": [
                #                            ...
                #                         ]
                #                     }
                #                 }
                #             }
                #         }
                #     }
                # }
                else:
                    parent_to_write = True
                    base_path = kwargs['base_path'] + "/" + model_name

            only_type = False
            if 'only_type' in kwargs:
                only_type = kwargs['only_type']
            self.generate_definition(
                model_name=self.get_capitalized(model_name) + 'Content',
                body=items,
                base_path=base_path, only_type=only_type)

            kwargs['to_write'] = parent_to_write
            if 'is_property' in kwargs and kwargs['is_property'] is True:
                kwargs['to_write'] = False

            ex_import = 'import ' + self.get_capitalized(
                model_name) + 'Content' + ' from \'./' + self.get_capitalized(
                model_name) + 'Content' + '/' + 'index.js\'\n'
            ex_api_import = 'import type {API' + self.get_capitalized(
                model_name) + 'Content' + '} from \'./' + self.get_capitalized(
                model_name) + 'Content' + '/type.js\'\n'

            if ex_import not in kwargs['extra_imports']:
                kwargs['extra_imports'] += ex_import
            if ex_api_import not in kwargs['api_model_dict']['import']:
                kwargs['api_model_dict']['import'] += ex_api_import

            prop_result += '<' + self.get_capitalized(
                model_name) + 'Content' + '>'

            api_prop_result += '<' + 'API' + self.get_capitalized(
                model_name) + 'Content' + '>'
            is_required = prop_result in required

            field = (self.get_camel(model_name), prop_result, is_required)
            request_data_field = (self.get_camel(model_name), self.get_camel(
                model_name) + '.map((item) => item.getRequestData())',
                                  prop_result, is_required)

            constructor = (
                self.get_camel(model_name),
                model_name + '.map((item) => new ' + self.get_capitalized(
                    model_name) + 'Content' + '(item))')

            action = (self.get_capitalized(model_name) + 'Content',
                      self.get_camel(model_name), ':' + str(prop_result),
                      '=' + str(default_type),
                      self.get_camel(model_name), is_required)

            api_type_field = (model_name, api_prop_result, is_required)
            kwargs = self.kwargs_append(kwargs, field, request_data_field,
                                        action, constructor, api_type_field)

        return kwargs

    def generate_all_of_definition(self, **kwargs):

        model_name = kwargs['model_name']
        allOf = kwargs['body']['allOf']
        for each_ref in allOf:

            if '$ref' in each_ref:
                # {
                #     "allOf": [
                #         {
                #             "$ref": "#/definitions/FooBar"
                #         },
                #         {
                #             "$ref": "#/definitions/KeyValue"
                #         }
                #     ]
                # }
                only_type = False
                if 'only_type' in kwargs:
                    only_type = kwargs['only_type']

                name = each_ref.get('$ref')
                name = name.split('/')[2]
                for v_def_name, v_definition in list(self.parser.definitions().items()):
                    if name == v_def_name:
                        v_kwargs = self.generate_definition(
                            model_name=self.get_capitalized(model_name),
                            body=v_definition,
                            base_path=kwargs['base_path'], only_type=only_type)

                        # kwargs = self.kwargs_append(kwargs=kwargs, field,
                        # request_data_field, action,
                        # constructor,
                        # api_type_field,v_kwargs=v_kwargs,has_v_kwargs=True)
                        kwargs = self.kwargs_append(kwargs=kwargs,
                                                    field=v_kwargs['fields'],
                                                    request_data_field=
                                                    v_kwargs['request_data'],
                                                    action=v_kwargs['actions'],
                                                    constructor=v_kwargs[
                                                        'constructor'],
                                                    api_type_field=
                                                    v_kwargs['api_model_dict'][
                                                        'fields'],
                                                    has_v_kwargs=True)

                        if v_kwargs['extra_imports'] not in kwargs[
                            'extra_imports']:
                            kwargs['extra_imports'] += v_kwargs[
                                'extra_imports']

                        if v_kwargs['api_model_dict']['import'] not in \
                            kwargs['api_model_dict']['import']:
                            kwargs['api_model_dict']['import'] += \
                                v_kwargs['api_model_dict']['import']

                        kwargs['import_flag'] = True
                        kwargs['api_model_dict']['import_flag'] = True
            elif 'type' in each_ref:

                if each_ref['type'] == 'object':
                    # {
                    #     "allOf": [
                    #         {
                    #             "type":"object"
                    #             "properties": ...
                    #         }
                    #     ]
                    # }
                    only_type = False
                    if 'only_type' in kwargs:
                        only_type = kwargs['only_type']
                    v_kwargs = self.generate_definition(
                        model_name=self.get_capitalized(model_name),
                        body=each_ref,
                        base_path=kwargs['base_path'], to_write=False,
                        only_type=only_type)
                    # kwargs = self.kwargs_append(kwargs, field,
                    #                             request_data_field, action,
                    #                             constructor, api_type_field)
                    kwargs = self.kwargs_append(kwargs=kwargs,
                                                field=v_kwargs['fields'],
                                                request_data_field=v_kwargs[
                                                    'request_data'],
                                                action=v_kwargs['actions'],
                                                constructor=v_kwargs[
                                                    'constructor'],
                                                api_type_field=
                                                v_kwargs['api_model_dict'][
                                                    'fields'],
                                                has_v_kwargs=True)

                    if v_kwargs['extra_imports'] not in kwargs[
                        'extra_imports']:
                        kwargs['extra_imports'] += v_kwargs['extra_imports']
                    if v_kwargs['api_model_dict']['import'] not in \
                        kwargs['api_model_dict']['import']:
                        kwargs['api_model_dict']['import'] += \
                            v_kwargs['api_model_dict']['import']
                    kwargs['api_model_dict']['enums'].extend(
                        v_kwargs['api_model_dict']['enums'])
                    kwargs['import_flag'] = True
                    kwargs['api_model_dict']['import_flag'] = True

        return kwargs

    def check_if_array_schema(self, schema):
        """
        returns schema if not an array,

        if an array, returns the item as schema

        :param schema:
        :return:
        """
        if 'type' in schema and schema['type'] == 'array':
            return self.check_if_array_schema(schema['items'])

        return schema

    def generate_parameter_or_response(self, base_path, is_response):
        """
        method to generate parameters and responses
        :param base_path:
        :param is_response:
        :return:
        """
        kwargs = {
            'imports': '',
            'import_flag': False,
            'type_files': [],
            'enums': []
        }

        if is_response is True:
            f = list(self.parser.responses().items())
        else:
            f = list(self.parser.parameters().items())
        for name, body in f:
            schema = body.get('schema', None)
            if not schema:
                continue

            schema = self.check_if_array_schema(schema)
            model_name = name
            if '$ref' in schema:
                pass

            if not schema:
                pass

            elif '$ref' in schema:
                pass

            elif 'type' in schema and schema['type'] in self.primitive_types:
                pass

            else:

                # we pass only_type to be true

                v_kwargs = self.generate_definition(model_name=model_name,
                                                    body=schema,
                                                    base_path=base_path,
                                                    to_write=True,
                                                    only_type=True)
                imports = v_kwargs['api_model_dict']['import']
                kwargs['imports'] = self.format_type_imports(kwargs['imports'],
                                                             imports)

                if not kwargs['import_flag'] and 'import_flag' in v_kwargs:
                    kwargs['import_flag'] = v_kwargs['import_flag']
                kwargs['type_files'].append(v_kwargs['api_model_dict'])
                kwargs['enums'].extend(v_kwargs['api_model_dict']['enums'])

        write_path = os.path.join(base_path, 'type.js')

        # write_to_file writes the passes content into the given
        # path file

        # here we are writing into the api_template
        write_to_file(
            render('mobx_type_apimodel.j2', kwargs),
            write_path,
            False
        )

    @staticmethod
    def format_type_imports(imports, v_imports):
        imports = imports.split("\n")
        v_imports = v_imports.split("\n")

        u_imports_set = set(imports).union(set(v_imports))
        u_imports = list(u_imports_set)

        u_imports.remove('')
        u_imports = '\n'.join(u_imports)
        u_imports += '\n'
        return u_imports

    def generate_parameters(self, base_path):
        """
        method to generate parameters
        :param base_path:
        :return:
        """
        self.generate_parameter_or_response(base_path=base_path,
                                            is_response=False)

    def generate_responses(self, base_path):
        """
        driver program to generate responses
        :param base_path:
        :return:
        """
        self.generate_parameter_or_response(base_path=base_path,
                                            is_response=True)

    def generate_endpoints(self, base_path):
        """
        method to genereate endpoints
        :param base_path:
        :return:
        """
        for path, path_body in list(self.parser.paths().items()):

            for each_method in list(path_body.keys()):
                if each_method in ['get', 'put', 'delete', 'post', 'update']:
                    inner_body = path_body[each_method]
                    operation_id = inner_body['operationId']

                    # form responses
                    responses = inner_body['responses']
                    responses = responses['200']
                    response_name = self.get_capitalized(operation_id)
                    if '$ref' in responses:
                        continue
                    schema = responses.get('schema', None)
                    if schema is None:
                        continue
                    elif '$ref' in schema:
                        continue
                    else:
                        self.generate_definition(model_name=response_name,
                                                 body=schema,
                                                 base_path=base_path,
                                                 from_endpoint=True,
                                                 endpoint_type='response')

                    # form parameters
                    parameters = inner_body.get('parameters', None)
                    if not parameters:
                        continue

                    for parameter in parameters:
                        parameter_name = self.get_capitalized(operation_id)
                        schema = parameter.get('schema', None)
                        if not schema:
                            continue
                        elif '$ref' in schema:
                            continue

                        else:
                            self.generate_definition(model_name=parameter_name,
                                                     body=schema,
                                                     base_path=base_path,
                                                     from_endpoint=True,
                                                     endpoint_type='request')


def stack_trace(value=None):
    """

    backtracks all the subroutine calls

    prints function names where it is called and their  line numbers

    :param value:

    :return:

    """

    print("=======================> Stacktrace STARTS for {value} <==".format(

        value=value))

    import traceback

    for line in traceback.format_stack():
        trace_line = line.strip()

        start_index = trace_line.rfind('/')

        trace_line = trace_line[start_index + 1:]

        print(trace_line.replace('",', "=> "))

    print("========================> Stacktrace ENDS for {value} <==".format(

        value=value))
