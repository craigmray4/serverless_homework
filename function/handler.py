from datetime import datetime
import os, boto3, json

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = "craigray-pulumi-hw-table"

def handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    # loop through all files captured by the event
    for item in event['Records']:

        timestamp = str(datetime.now())
        key = event['Records'][0]['s3']['object']['key']

        print("---------")

        table.put_item(Item={
            'id': 'id',
            'filename': key,
            'timestamp': timestamp
            })
        
        print(f"Uploaded {key} to {TABLE_NAME}")
        print("---------")

