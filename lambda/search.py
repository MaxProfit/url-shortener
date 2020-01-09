import boto3
from botocore.exceptions import ClientError
import json
import os

client = boto3.client('dynamodb')

def create_return_value(success, name, link=None):
    if success:
        return {
            'statusCode': 301,
            'headers': {
                "Location": link,
                "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
                "Access-Control-Allow-Credentials" : True # Required for cookies, authorization headers with HTTPS 
            }
        }
    else:
        return {
            'statusCode': 404,
            'headers': {
                "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
                "Access-Control-Allow-Credentials" : True # Required for cookies, authorization headers with HTTPS 
            },
            'body': json.dumps("{} doesn't exist in the database!".format(name))
        }

def return_url(name):
    try:
        response = client.get_item(
            TableName=os.environ["TABLE_NAME"],
            Key={
                os.environ["PRIMARY_KEY"]: {
                    'S': name
                }
            }
        )

        link = response["Item"][os.environ["POINTS_TO"]]["S"]
        return create_return_value(True, name, link)
    except ClientError as e:
        print(e.response["Error"]["Message"])
        return create_return_value(False, name)

def lambda_handler(event, context):
    name = event["pathParameters"]["name"]
    return return_url(name)