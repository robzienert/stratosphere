import stratosphere

################
# Cloudtools-style DSL:

# A group of CloudFormation templates that relate to each other is
# called a Superstack. I don't really like the name, but it doesn't
# conflict with any CFN naming.
superstack = stratosphere.Superstack()
superstack.add_description('''This is a description of the superstack,
                              it's just for documentation purposes.''')

# The Superstack can tell CloudFormation to send notifications to
# one or more SNS topics.
# superstack.sns_notifications(topic_arn...)

# An initial restriction to a Superstack is that all stacks within
# must be part of the same region.
superstack.region('us-east-1')

# Superstacks, by default, can only link up data that it knows about
# in the stacks that it contains (parameters, resources, outputs), but
# additional lookup providers can be added, allowing developers to
# populate stack parameters according to their own use cases.
# Example:
# - Look up the latest Ubuntu 14.04 HVM AMI
# - Look up the subnet IDs for a specific AZ
# superstack.add_lookup('MyLookup', my_custom_lookup_provider)

superstack.add_stack(stratosphere.Stack('MyVpcStack'))

superstack.add_stack(stratosphere.Stack(
    'MyApplicationStack',
    CloudFormationTemplate='app.json',
    # CloudFormationTemplate='http://s3.amazonaws.com/app.json',
    # CloudFormationTemplate=troposphere_template,
    DependsOn=['MyVpcStack'],
    Parameters=[
        stratosphere.Parameter(
            'VpcId',
            Source='MyVpcStack',
            Type='resource',
            Variable='Vpc'
        ),
        stratosphere.Parameter(
            'PrivateSubnet',
            # Provider=my_lookup_provider
            #Provider='MyLookup'
        ),
        stratosphere.Parameter(
            'ApplicationName',
            Value='raw-value'
        )
    ]
))

###############
# YAML DSL
# This would come later; I want to get the native API working well first
# before adding in another abstraction.

###############
# CLI
# 'plan' will validate the templates as much as it can and print the
# planned execution based on the state in CFN. Parameters can be passed
# in to either override defaults set by the template, or set parameters
# in templates that were undefined. If a stack has already been created,
# undefined parameters need not be defined again.
# stratosphere plan -var 'VpcCidr=10.10' foo-superstack

# Plans and runs any necessary executions
# stratosphere run \
#              -var 'VpcCidr=10.10' # Override defaults; or provide params that weren't defined
# foo-superstack # Looks for "foo-superstack.py" in same dir

