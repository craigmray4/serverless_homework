import json
import pulumi
import pulumi_aws as aws
from pulumi_aws import s3


TABLE_NAME = "craigray-pulumi-hw-table"
FUNCTION_NAME = "craigray-pulumi-hw-function"
BUCKET_NAME = "craigray-pulumi-hw-bucket"
ENVIRONMENT = "homework"


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


#############################################
# Lambda Function
#############################################

lambda_fn = aws.lambda_.Function(FUNCTION_NAME,
    name = FUNCTION_NAME,
    runtime = "python3.9",
    handler = "handler.handler",
    role = role.arn,
    code = pulumi.FileArchive("./function"),
    tags = {
           "Name": FUNCTION_NAME,
           "Environment": ENVIRONMENT
    }
)


#############################################
# S3 Bucket
#############################################

bucket = s3.BucketV2("bucket", bucket=BUCKET_NAME,
        tags = {
            "Name": BUCKET_NAME,
            "Environment": ENVIRONMENT
        }
)

bucket_notification = aws.s3.BucketNotification(
    "bucket-notification",
    opts = pulumi.ResourceOptions(depends_on = [bucket, lambda_fn]),
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
    statement_id = "AllowExecutionFromS3Bucket",
    action = "lambda:InvokeFunction",
    function = lambda_fn.arn,
    principal = "s3.amazonaws.com",
    source_arn = bucket.arn)


#############################################
# Dynamo DB Table
#############################################

dynamo_table = aws.dynamodb.Table(
    TABLE_NAME,
    name = TABLE_NAME,
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
        "Name": TABLE_NAME,
        "Environment": ENVIRONMENT
    },
)

pulumi.export("table_name", dynamo_table.name)
pulumi.export("bucket_name", bucket.bucket)
pulumi.export("function_name", lambda_fn.name)