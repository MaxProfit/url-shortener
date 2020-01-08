import boto3
from botocore.exceptions import ClientError
import json
import os

client = boto3.client('dynamodb')

def create_return_value(success, name=None, link=None):
    if success:
        return {
            'statusCode': 301,
            'headers': {
                "Location": link
            }
        }
    else:
        return {
            'statusCode': 409,
            'body': json.dumps("{} already exists in the database!".format(name))
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
    return return_url(event["pathParameters"]["name"])