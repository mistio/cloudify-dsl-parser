########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

from dsl_parser import (exceptions,
                        constants)
from dsl_parser.framework.elements import (DictElement,
                                           Element,
                                           Leaf)


class Instances(Element):

    schema = Leaf(type=int)
    default_value = None

    def parse(self):
        if self.initial_value is None:
            return self.default_value
        return self.initial_value


class DefaultOneInstances(Instances):

    default_value = 1

    def validate(self):
        if self.initial_value is not None and self.initial_value < 0:
            raise exceptions.DSLParsingLogicException(
                exceptions.ERROR_INVALID_INSTANCES,
                '{0} should be a non negative value.'
                .format(self.name))


class DefaultInstances(DefaultOneInstances):
    pass


class MinInstances(DefaultOneInstances):
    pass


class MaxInstances(Instances):

    schema = Leaf(type=(int, basestring))
    default_value = constants.UNBOUNDED

    def validate(self):
        value = self.initial_value
        if value is None:
            return
        if isinstance(value, basestring):
            if value != constants.UNBOUNDED_LITERAL:
                raise exceptions.DSLParsingLogicException(
                    exceptions.ERROR_INVALID_LITERAL_INSTANCES,
                    'The only valid string for {0} is {1}.'
                    .format(self.name,
                            constants.UNBOUNDED_LITERAL))
            return
        if value == constants.UNBOUNDED:
            return
        if value < 1:
            raise exceptions.DSLParsingLogicException(
                exceptions.ERROR_INVALID_INSTANCES,
                '{0} should be a positive value.'
                .format(self.name))

    def parse(self):
        if self.initial_value == constants.UNBOUNDED_LITERAL:
            return constants.UNBOUNDED
        return super(MaxInstances, self).parse()


class Properties(DictElement):

    DEFAULT = {
        'min_instances': MinInstances.default_value,
        'max_instances': MaxInstances.default_value,
        'default_instances': DefaultInstances.default_value,
        'current_instances': DefaultInstances.default_value,
        'planned_instances': DefaultInstances.default_value
    }

    schema = {
        'min_instances': MinInstances,
        'max_instances': MaxInstances,
        'default_instances': DefaultInstances
    }

    def validate(self):
        result = self.build_dict_result()
        min_instances = result.get('min_instances',
                                   self.DEFAULT['min_instances'])
        max_instances = result.get('max_instances',
                                   self.DEFAULT['max_instances'])
        default_instances = result.get('default_instances',
                                       self.DEFAULT['default_instances'])
        if default_instances < min_instances:
            raise exceptions.DSLParsingLogicException(
                exceptions.ERROR_INVALID_INSTANCES,
                'default_instances ({0}) cannot be smaller than '
                'min_instances ({1})'
                .format(default_instances, min_instances))
        if max_instances == constants.UNBOUNDED:
            return
        if min_instances > max_instances:
            raise exceptions.DSLParsingLogicException(
                exceptions.ERROR_INVALID_INSTANCES,
                'min_instances ({0}) cannot be greater than '
                'max_instances ({1})'
                .format(min_instances, max_instances))
        if default_instances > max_instances:
            raise exceptions.DSLParsingLogicException(
                exceptions.ERROR_INVALID_INSTANCES,
                'default_instances ({0}) cannot be greater than '
                'max_instances ({1})'
                .format(default_instances, max_instances))

    def parse(self, **kwargs):
        result = self.build_dict_result()
        result['default_instances'] = result.get(
            'default_instances', self.DEFAULT['default_instances'])
        result['min_instances'] = result.get(
            'min_instances', self.DEFAULT['min_instances'])
        result['max_instances'] = result.get(
            'max_instances', self.DEFAULT['max_instances'])
        result['current_instances'] = result['default_instances']
        result['planned_instances'] = result['default_instances']
        return result