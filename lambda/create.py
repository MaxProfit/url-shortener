import boto3
from botocore.exceptions import ClientError
import json
import uuid
import os

client = boto3.client('dynamodb')

def create_return_value(success, name):
    if success:
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
                "Access-Control-Allow-Credentials" : True # Required for cookies, authorization headers with HTTPS 
            },
            'body': json.dumps("Success! {} was added to the database".format(name))
        }
    else:
        return {
            'statusCode': 409,
            'headers': {
                "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
                "Access-Control-Allow-Credentials" : True # Required for cookies, authorization headers with HTTPS 
            },
            'body': json.dumps("{} already exists in the database!".format(name))
        }

def create_item(name, link):
    try:
        client.put_item(
            TableName=os.environ["TABLE_NAME"],
            Item={
                os.environ["PRIMARY_KEY"]: {
                    'S': name,
                },
                os.environ["POINTS_TO"]: {
                    'S': link
                }
            }
        )

        return create_return_value(True, name)
    except ClientError as e:
        print(e.response["Error"]["Message"])
        return create_return_value(False, name)
    
def check_exists(name):
    try:
        response = client.get_item(
            TableName=os.environ["TABLE_NAME"],
            Key={
                os.environ["PRIMARY_KEY"]: {
                    'S': name
                }
            }
        )

        # Checks if it exists in the response
        if 'Item' not in response:
            return False

    except ClientError as e:
        print(e.response["Error"]["Message"])
        return False
    return True

def create_random(link):
    name = str(uuid.uuid4())
    return create_item(name, link)

def create_named(name, link):
    if check_exists(name):
        return create_return_value(False, name)
    else:
        return create_item(name, link)

def lambda_handler(event, context):
    link = event["body"]
    if event["pathParameters"] is None:
        return create_random(link)
    else:
        name = event["pathParameters"]["name"]
        return create_named(name, link)