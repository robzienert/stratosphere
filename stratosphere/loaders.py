import logging
from urlparse import urlparse
import os
import json

import requests


class ConfigLoader(object):
    def load(self, filename):
        raise NotImplementedError('load method must be implemented')

    def _validate_file(self, filename):
        if not os.path.isfile(filename):
            raise IOError('could not find config at %s' % filename)


class PythonConfigLoader(ConfigLoader):
    def load(self, filename):
        logging.debug('Loading "%s"' % (filename,))
        self._validate_file(filename)

        with open(filename, 'r') as f:
            config = eval(f.read(), {'__builtins__': None}, {})
            return config


class YamlConfigLoader(ConfigLoader):
    pass


class CloudFormationLoader(object):
    """
    TODO
        Template paths are returned as strings currently; not sure if I want
        to parse them as json yet.
    """

    def load(self, template):
        logging.debug('Loading "%s"' % (template,))
        if isinstance(template, basestring):
            u = urlparse(template)
            if not u.netloc:
                if not os.path.exists(u.path):
                    raise IOError(
                        'could not find local CloudFormation template '
                        'at "%s"' % (u.path,)
                    )
                with open(u.path, 'r') as f:
                    return json.loads(f.read())

            else:
                r = requests.get(template)
                if r.status_code != 200:
                    raise IOError(
                        'could not find remote CloudFormation template '
                        ' at "%s"' % (template,)
                    )
                return json.loads(str(r.text))
        else:
            # TODO Handle troposphere templates
            raise NotImplementedError(
                'troposphere templates not yet supported'
            )
