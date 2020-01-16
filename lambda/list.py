import boto3
from botocore.exceptions import ClientError
import json
import os

client = boto3.client('dynamodb')

def create_return_value(success, url_dict=None):
    if success:
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
                "Access-Control-Allow-Credentials" : True, # Required for cookies, authorization headers with HTTPS
                "Content-Type": "application/json"
            },
            'body': json.dumps(url_dict)
        }
    else:
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
                "Access-Control-Allow-Credentials" : True, # Required for cookies, authorization headers with HTTPS
                "Content-Type": "application/json"
            },
            'body': json.dumps("Internal Server Error")
        }


def get_list():
    try:
        response = client.scan(
            TableName=os.environ["TABLE_NAME"]
        )

        url_dict = {item["ShortUrl"]["S"]:item["Link"]["S"] for item in response["Items"]}

        return create_return_value(True, url_dict)

    except ClientError as e:
        print(e.response["Error"]["Message"])
        return create_return_value(False)

def lambda_handler(event, context):
    return get_list()