import logging
import stratosphere
from stratosphere.exception import StackNotFoundError
import json


class CloudFormationRegistry(object):
    def __init__(self, cfn_conn):
        self.cfn_conn = cfn_conn
        logging.debug('Caching current CloudFormation stack information')

        self.stacks = self.cfn_conn.describe_stacks()
        self.resources = {}

    def has_stack(self, name):
        return self.get_stack(name) is not None

    def get_stack(self, name, resources=True):
        stacks = [s for s in self.stacks if s.stack_name == name]
        stack = stacks[0] if len(stacks) == 1 else None

        if stack and resources:
            logging.debug(
                'Caching resources for CloudFormation stack "%s"' % (name,)
            )
            self.resources[stack.stack_name] = stack.describe_resources()

        return stack

    def refresh(self, name, resources=True):
        stack = self.get_stack(name)
        if stack:
            self.stacks.remove(stack)
            del(self.resources[stack.stack_name])

            refreshed = self.cfn_conn.describe_stacks(stack_name_or_id=name)
            if not refreshed:
                raise StackNotFoundError(
                    'Could not find CloudFormation stack '
                    'by name "%s"' % (name,)
                )
            self.stacks.append(refreshed)

            if resources:
                self.resources[name] = refreshed.describe_resources()

    def uptodate(self, stack):
        # TODO - this method needs more love... how do we compare?
        if not isinstance(stack, stratosphere.Stack):
            raise ValueError(
                'stack must be of type stratosphere.Stack, "%s" given' %
                (type(stack),)
            )

        cfn_stack = self.get_stack(stack.StackName)
        if cfn_stack is None:
            return False

        t = cfn_stack.get_template()
        cfn_template_body = json.loads(
            t['GetTemplateResponse']['GetTemplateResult']['TemplateBody']
        )

        return stack.template_body == cfn_template_body
