from datetime import datetime
import os, boto3, json

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

table_name = "craigray-homework"

def handler(event, context):
    table = dynamodb.Table(table_name)

    for item in event['Records']:
        timestamp = str(datetime.now())
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        print("---------")

        table.put_item(Item={
            'id': 'id',
            'filename': key,
            'timestamp': timestamp
            })
        
        print(f"Uploaded {key} to {table_name}")
        print("---------")

