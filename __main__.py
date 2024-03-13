import json
import pulumi
import pulumi_aws as aws
from pulumi_aws import s3

region = "us-west-2"
table_name = "craigray-homework"


#############################################
# Lambda Permissions
#############################################

iam_policy_document = aws.iam.get_policy_document(statements=[
    {
        'effect': 'Allow',
        'actions': ['dynamodb:PutItem'],
        'resources': ['*'],
    }
])

policy_one = aws.iam.Policy("policy_one",
    name="CraigRayHWLambdaPolicy",
    policy=iam_policy_document.json)

role = aws.iam.Role("role", 
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com",
            },
        }],
    }),
    managed_policy_arns=[
        aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE,
        policy_one.arn,
        ]
    )


#############################################
# Lambda Function
#############################################

lambda_fn = aws.lambda_.Function("fn",
    runtime="python3.9",
    handler="handler.handler",
    role=role.arn,
    code=pulumi.FileArchive("./function"))


#############################################
# S3 Bucket
#############################################

bucket = s3.BucketV2("bucket", bucket="craigray-pulumi-hw-bucket")

bucket_notification = aws.s3.BucketNotification(
    "bucket-notification",
    bucket = bucket.id,
    lambda_functions = [
        aws.s3.BucketNotificationLambdaFunctionArgs(
            lambda_function_arn = lambda_fn.arn,
            events = ["s3:ObjectCreated:*"],
        )
    ],
)


#############################################
# Lambda Bucket Permissions
#############################################

allow_bucket = aws.lambda_.Permission("allow_bucket",
    statement_id="AllowExecutionFromS3Bucket",
    action="lambda:InvokeFunction",
    function=lambda_fn.arn,
    principal="s3.amazonaws.com",
    source_arn=bucket.arn)


#############################################
# Dynamo DB Table
#############################################

dynamo_table = aws.dynamodb.Table(
    table_name,
    attributes = [
        {
            "name": "id",
            "type": "S"
        }
    ],
    hash_key = "id",
    billing_mode = "PAY_PER_REQUEST",
    stream_enabled = False,
    tags = {
        "Name": table_name,
        "Environment": "homework"
    },
    opts=pulumi.Alias(name = table_name)
)

pulumi.export("table_name", dynamo_table.name)