import stratosphere
import stratosphere.parameters as parameters
import stratosphere.providers as providers

superstack = stratosphere.Superstack()
superstack.add_description('Deploys a ratpack application on top of a 3 '
                           'AZ VPC.')
superstack.region('us-east-1')

vpc_stack = superstack.add_stack(stratosphere.Stack(
    'Vpc',
    StackName='dev-vpc',
    CloudFormationTemplate='VpcRatpackApp/vpc.json',
    Parameters=[
        parameters.Parameter(
            'EnvName',
            Value='dev'
        ),
        parameters.Parameter(
            'CidrBlock',
            Value='10.0'
        ),
        parameters.Parameter(
            'AvailabilityZones',
            Value='us-east-1c,us-east-1d,us-east-1e'
        )
    ]
))

platform_stack = superstack.add_stack(stratosphere.Stack(
    'PlatformSecurityGroups',
    StackName='dev-platform-security-group',
    CloudFormationTemplate='VpcRatpackApp/security_groups.json',
    DependsOn=[vpc_stack],
    Parameters=[
        parameters.Parameter(
            'VpcId',
            Source=vpc_stack,
            Type=parameters.Parameter.OUTPUT,
            Variable='VpcId'
        )
    ]
))

superstack.add_stack(stratosphere.Stack(
    'RatpackApp',
    StackName='dev-ratpack-app',
    CloudFormationTemplate='VpcRatpackApp/app.json',
    DependsOn=[platform_stack],
    Parameters=[
        parameters.Parameter(
            'VpcId',
            Source=vpc_stack,
            Type=parameters.Parameter.OUTPUT,
            Variable='VpcId'
        ),
        parameters.Parameter(
            'KeyName',
            Value='dev-ratpack'
        ),
        parameters.Parameter(
            'ImageId',
            Provider=providers.UbuntuAmiLookupProvider('trusty')
        ),
        parameters.Parameter(
            'InstanceType',
            Value='t2.medium'
        ),
        parameters.Parameter(
            'AvailabilityZones',
            Source=vpc_stack,
            Type=parameters.Parameter.PARAMETER,
            Variable='AvailabilityZones'
        ),
        parameters.Parameter(
            'PublicSubnets',
            Source=vpc_stack,
            Type=parameters.Parameter.OUTPUT,
            Variable='PublicSubnets'
        ),
        parameters.Parameter(
            'LoadBalancerSg',
            Source=platform_stack,
            Type=parameters.Parameter.OUTPUT,
            Variable='LoadBalancerSg'
        ),
        parameters.Parameter(
            'AppSg',
            Source=platform_stack,
            Type=parameters.Parameter.OUTPUT,
            Variable='AppSg'
        )
    ]
))
