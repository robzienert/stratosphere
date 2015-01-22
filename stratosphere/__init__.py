import requests
from urlparse import urlparse
import os
from toposort import toposort

try:
    from troposphere import Template
    template_types = (basestring, Template)
except ImportError:
    template_types = basestring,


class BaseStratosphereObject(object):
    def __init__(self, title, **kwargs):
        self.title = title
        self.propnames = self.props.keys()

        self.properties = {}

        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def __getattr__(self, name):
        try:
            return self.properties.__getitem__(name)
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self.__dict__.keys():
            return dict.__setattr__(self, name, value)
        elif name in self.propnames:
            expected_type = self.props[name][0]

            if isinstance(expected_type, list):
                if not isinstance(value, list):
                    self._raise_type(name, value, expected_type)
                for v in value:
                    if not isinstance(v, tuple(expected_type)):
                        self._raise_type(name, v, expected_type)
                return self.properties.__setitem__(name, value)
            elif isinstance(value, expected_type):
                return self.properties.__setitem__(name, value)
            else:
                self._raise_type(name, value, expected_type)

        raise AttributeError(
            '%s does not support attribute %s' %
            (self.__class__.__name__, name)
        )

    def _raise_type(self, name, value, expected_type):
        raise TypeError('%s is %s, expected %s' %
                        (name, type(value), expected_type))

    def validate(self, superstack):
        pass


class Stack(BaseStratosphereObject):
    props = {
        'CloudFormationTemplate': (template_types, False),
        'Description': (basestring, False),
        'DependsOn': (list, False),
        'Parameters': (list, False),
        'SnsNotification': (list, False)
    }

    def __init__(self, title, **kwargs):
        super(Stack, self).__init__(title, **kwargs)
        self.parameter_values = {}

    def validate(self, superstack):
        if isinstance(self.CloudFormationTemplate, basestring):
            u = urlparse(self.CloudFormationTemplate)
            if not u.netloc:
                if not os.path.exists(u.path):
                    raise IOError(
                        'could not find local CloudFormation template '
                        'at "%s"' % (u.path,)
                    )
            else:
                # TODO Do we need to cache this?
                r = requests.get(self.CloudFormationTemplate)
                if r.status_code != 200:
                    raise IOError(
                        'could not find remote CloudFormation template '
                        ' at "%s"' % (self.CloudFormationTemplate,)
                    )

        for parameter in self.Parameters:
            parameter.validate(self)


class Superstack(object):
    def __init__(self):
        self.description = None
        self.stacks = {}
        self.providers = []
        self.sns_notifications = []
        self.region = None

    def add_description(self, description):
        self.description = description

    def set_region(self, region):
        self.region = region

    def _update(self, d, values):
        if isinstance(values, list):
            for v in values:
                if v.title in d:
                    self._handle_duplicate_key(v.title)
                d[v.title] = values
        else:
            if values.title in d:
                self._handle_duplicate_key(values.title)
            d[values.title] = values
        return values

    def add_stack(self, stack):
        return self._update(self.stacks, stack)

    def add_provider(self, provider):
        return self._update(self.providers, provider)

    def add_sns_notification(self, topic):
        if isinstance(topic, list):
            self.sns_notifications.extend(topic)
        else:
            self.sns_notifications.append(topic)
        return self.sns_notifications

    def validate(self):
        for stack in self.stacks:
            stack.validate()

        for provider in self.providers:
            provider.validate(self)

        self.sort_stack_dependencies()

    def sort_stack_dependencies(self):
        return list(toposort({t: s.depends_on for t, s in self.stacks}))

    def _handle_duplicate_key(self, key):
        raise ValueError('duplicate key "%s" detected' % key)
