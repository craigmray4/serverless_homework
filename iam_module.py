import pulumi
import pulumi_aws as aws
import json


class IAMModule(pulumi.ComponentResource):
    def __init__(self, name, opts = None):
        super().__init__('pkg:index:IAMModule', name, None, opts)

    iam_policy_document = aws.iam.get_policy_document(statements=[
        {
            'effect': 'Allow',
            'actions': ['dynamodb:PutItem'],
            'resources': ['*'],
        }
    ])

    policy_one = aws.iam.Policy("policy_one",
        name = "CraigRayHWLambdaPolicy",
        policy = iam_policy_document.json)

    role = aws.iam.Role("role", 
        assume_role_policy = json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com",
                },
            }],
        }),
        managed_policy_arns = [
            aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE,
            policy_one.arn,
            ]
        )