import csv

import requests
import boto.cloudformation


class LookupProvider(object):

    def validate(self, superstack):
        pass

    def lookup(self, superstack, stack, parameter):
        raise NotImplementedError('Lookup must implement lookup method')


class CloudFormationLookupProvider(LookupProvider):

    def __init__(self, region):
        self.conn = boto.cloudformation.connect_to_region(region)

    def lookup(self, superstack, stack, parameter):
        # target_stack = superstack.stacks[parameter.Source]

        if parameter.Type == 'output':
            # TODO CFN API for output
            pass

        elif parameter.Type == 'resource':
            # TODO
            pass

        elif parameter.Type == 'parameter':
            # TODO
            pass

        else:
            raise ValueError(
                '%s.%s parameter cannot use CloudFormationLookupProvider' % (
                    stack.title,
                    parameter.title
                ))


class UbuntuAmiLookupProvider(LookupProvider):
    TYPE_IDX = 4
    ARCH_IDX = 5
    REGION_IDX = 6
    AMI_IDX = 7
    VIRTUALIZATION_IDX = 10

    def __init__(self, release, virtualization='hvm', arch='amd64',
                 type='ebs-ssd', use_cache=True):
        self.release = release
        self.virtualization = virtualization
        self.arch = arch
        self.type = type
        self.use_cache = use_cache
        self.ami = None

    def lookup(self, superstack, stack, parameter):
        if self.use_cache and self.ami is not None:
            return self.ami

        r = requests.get('https://cloud-images.ubuntu.com/query/{}/server/'
                         'released.current.txt'.format(self.release))

        if r.status_code is not 200:
            raise IOError('Ubuntu cloud images returned with '
                          'status {}'.format(r.status_code))

        for image in list(csv.reader(r.text.split('\n'), delimiter='\t')):
            if len(image) != 11:
                continue
            if image[self.REGION_IDX] != superstack.region:
                continue
            if image[self.ARCH_IDX] != self.arch:
                continue
            if image[self.VIRTUALIZATION_IDX] != self.virtualization:
                continue
            if image[self.TYPE_IDX] != self.type:
                continue

            self.ami = image[self.AMI_IDX]
            break

        return self.ami
