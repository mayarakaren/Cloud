import json
import boto3
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = event['bucket_name']
    file_path = event['file_path']
    key = os.path.basename(file_path)

    try:
        s3.upload_file(file_path, bucket_name, key)
        response = {
            'statusCode': 200,
            'body': json.dumps(f'File {file_path} uploaded to bucket {bucket_name} with key {key}')
        }
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': json.dumps(f'Error uploading file: {str(e)}')
        }
    return response
