# stratosphere

It's above [troposphere](https://github.com/cloudtools/troposphere).

Stratosphere aims to solve the issue of orchestrating AWS CloudFormation
deployments where a large number of separate, but closely related stacks are
used. In adopting such a pattern, you're either forced to use the Console,
which is slow, error-prone, and fairly mindless, or you can write custom
scripts to link various stacks together.

Stratosphere helps you by making the second option, writing custom scripts,
not-so-custom, as well as providing an API allowing extensibility for whatever
edge cases you may have.

## VPC Example

```python
from stratosphere import Superstack, Stack
from stratosphere.parameters import Parameter
from stratosphere.providers import UbuntuAmiLookupProvider

superstack = Superstack()
superstack.region('us-east-1')

vpc_stack = superstack.add_stack(Stack(
    'Vpc',
    StackName='dev-vpc',
    CloudFormationTemplate='vpc.json',
    Parameters=[
        Parameter(
            'EnvName',
            Value='dev'
        ),
        Parameter(
            'CidrBlock',
            Value='10.0'
        ),
        Parameter(
            'AvailabilityZones',
            Value='us-east-1c,us-east-1d,us-east-1e'
        )
    ]
))

superstack.add_stack(Stack(
    'RatpackApp',
    StackName='dev-app',
    CloudFormationTemplate='app.json',
    DependsOn=[vpc_stack],
    Parameters=[
        Parameter(
            'VpcId',
            Source=vpc_stack,
            Type=Parameter.OUTPUT,
            Variable='VpcId'
        ),
        Parameter(
            'KeyName',
            Value='dev-ratpack'
        ),
        Parameter(
            'ImageId',
            Provider=UbuntuAmiLookupProvider('trusty',
                                             type='instance-store')
        ),
        Parameter(
            'InstanceType',
            Value='t2.medium'
        ),
        Parameter(
            'AvailabilityZones',
            Source=vpc_stack,
            Type=Parameter.PARAMETER,
            Variable='AvailabilityZones'
        ),
        Parameter(
            'PublicSubnets',
            Source=vpc_stack,
            Type=Parameter.OUTPUT,
            Variable='PublicSubnets'
        ),
        Parameter(
            'LoadBalancerSg',
            Source=platform_stack,
            Type=Parameter.OUTPUT,
            Variable='LoadBalancerSg'
        ),
        Parameter(
            'AppSg',
            Source=platform_stack,
            Type=Parameter.OUTPUT,
            Variable='AppSg'
        )
    ]
))
```

## Parameters

A Stack Parameter can be given a value in one of three ways:

Raw Values:
```python
Parameter(
    'MyParam',
    Value='foo'
)
```

Stack Variables, using one of `PARAMETER`, `RESOURCE` or `OUTPUT`:
```python
Parameter(
    'MyParam',
    Source=another_stack,
    Type=Parameter.OUTPUT,
    Variable='PrivateSubnets'
)
```

Or using a Provider, a dynamically generated value:
```python
Parameter(
    'MyParam`,
    Provider=UbuntuAmiLookupProvider('trusty')
)
```

## Providers

Providers offer an additional level of dynamicism to your Superstack.
Stratosphere currently ships with one: `UbuntuAmiLookupProvider`, which
will return you the latest official Ubuntu AMI that matches the filters
you provide it.

## Loaders

Writing Python not for you? Perhaps YAML, JSON? Whatever your DSL of choice,
you can write your own loader to construct your own flavor of the DSL.

# See Also

A lot of inspiration was taken from [cumulus](https://github.com/cotdsa/cumulus),
another project that does the same thing as this one.
