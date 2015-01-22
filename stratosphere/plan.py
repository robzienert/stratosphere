import stratosphere.providers as providers

class ParameterValueResolver(object):

    def __init__(self, superstack):
        self.superstack = superstack
        self.cfn_provider = providers.CloudFormationLookupProvider()

    def resolve_stack(self, stack):
        for parameter in stack.Parameters:
            self.resolve_parameter(stack, parameter)

    def resolve_parameter(self, stack, parameter):
        if parameter.Value is not None:
            return parameter.Value

        if parameter.Provider is not None:
            return parameter.Provider.lookup(self.superstack, stack)

        self.cfn_provider.lookup(self.superstack, stack, parameter)
