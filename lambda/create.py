import boto3
from botocore.exceptions import ClientError
import json
import uuid
import os

client = boto3.client('dynamodb')

def create_return_value(success, name=None):
    if success:
        return {
            'statusCode': 200,
            'body': json.dumps("Success!")
        }
    else:
        return {
            'statusCode': 409,
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
        resp = client.get_item(
            TableName=os.environ["TABLE_NAME"],
            Key={
                os.environ["PRIMARY_KEY"]: {
                    'S': name
                }
            }
        )

        try_this = resp["Item"]
        print(try_this)

    except ClientError as e:
        print(e.response["Error"]["Message"])
        return False
    except KeyError:
        print("KeyError")
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
    if event["pathParameters"] is None:
        return create_random(event["body"])
    else:
        return create_named(event["pathParameters"]["name"], event["body"])
