import logging
import boto.cloudformation
from stratosphere.exception import PlanError
from stratosphere.loaders import PythonConfigLoader, CloudFormationLoader
from stratosphere.aws import CloudFormationRegistry
from stratosphere.providers import CloudFormationLookupProvider
from colored import fg, attr


class CommitPlan(object):
    def __init__(self, superstack, create=None, update=None):
        self.superstack = superstack
        self.create = [] if create is None else create
        self.update = [] if update is None else update


class PlanProcessor(object):
    def __init__(self, print_plan=True, loader=None):
        self.print_plan = print_plan
        self.loader = PythonConfigLoader() if loader is None else loader

    def process(self, superstack_target):
        superstack = self.loader.load(superstack_target)

        logging.debug('Loading stack CloudFormation templates...')
        cfn_template_loader = CloudFormationLoader()
        for stack in superstack.stacks:
            stack.template_body = cfn_template_loader.load(
                stack.CloudFormationTemplate
            )

        superstack.validate()

        # TODO The connection object should probably be injected so it can
        # be used in the other processors? Need a way to define the region.
        cfn_conn = boto.cloudformation.connect_to_region(superstack.region)
        cfn_registry = CloudFormationRegistry(cfn_conn)

        superstack.add_provider(CloudFormationLookupProvider(cfn_registry))

        commit_plan = CommitPlan(superstack)
        for stack in superstack.stacks:
            if cfn_registry.get_stack(stack.StackName) is None:
                commit_plan.create.append(stack)
            elif not cfn_registry.uptodate(stack):
                commit_plan.update.append(stack)
            else:
                raise PlanError('could not determine action for stack "%s"'
                                % (stack.StackName,))

        if self.print_plan:
            PlanRenderer(commit_plan).render()

        return commit_plan


class PlanRenderer(object):
    """
    Example Output

        STRATOSPHERE
        ============

        SuperStackName

        0.0 Stack1 - NO_ACTION
            Parameters:
                FooParam: "StaticValue"
                BarParam: <UbuntuAmiLookupProvider>
        0.1 Stack2 - CREATE
        0.2 Stack3 - UPDATE
            Parameters:
                BazParam: <Ref Stack1.Param.BarParam>
        1.0 Stack4 - UPDATE
            DependsOn: Stack1, Stack3
        2.0 Stack5 - NO_ACTION
            DependsOn: Stack4
        2.1 Stack6 - NO_ACTION
            DependsOn: Stack4
    """
    HEADER_FG = fg('blue_1')
    CREATE_FG = fg('green')
    UPDATE_FG = fg('yellow')

    def __init__(self, commit_plan):
        self.commit_plan = commit_plan

    def render(self):
        superstack = self.commit_plan.superstack

        print ('%sSTRATOSPHERE%s' % (self.HEADER_FG, attr('reset')))
        print ('%s============%s' % (self.HEADER_FG, attr('reset')))
        print ''
        print superstack.title
        print ''

        for idx, group in self.commit_plan.superstack.execution_groups:
            minor = 0
            for stack_name, dependencies in group:
                print '%s.%s %s - %s' % (idx, minor, stack_name,
                                         self._action(stack_name))

                if len(dependencies) > 0:
                    print '  DependsOn: %s' % ', '.join(dependencies)

                stack = superstack.stacks[stack_name]
                if len(stack.Parameters) > 0:
                    self._render_parameters(stack.Parameters)

    def _render_parameters(self, parameters):
        print '  Parameters:'
        for param in parameters:
            if param.Source is not None:
                print '    %s: <Ref %s.%s.%s>' \
                      % (param.title, param.Source, param.Type, param.Variable)
            elif param.Provider is not None:
                print '    %s: %s' % (param.title, param.Provider)
            elif param.Value is not None:
                print '    %s: <Literal "%s">' % (param.title, param.Value)
            else:
                print '    %s: <None>'

    def _action(self, stack_name):
        if stack_name in self.commit_plan.create:
            return '%sCREATE%s' % (self.CREATE_FG, attr('reset'))

        if stack_name in self.commit_plan.update:
            return '%sUPDATE%s' % (self.UPDATE_FG, attr('reset'))

        return 'NO_ACTION'


class CommitProcessor(object):
    def __init__(self):
        pass


class CreateStackProcessor(object):
    def __init__(self):
        pass


class UpdateStackProcessor(object):
    def __init__(self):
        pass
