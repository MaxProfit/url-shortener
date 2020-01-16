import boto3
from botocore.exceptions import ClientError
import json
import uuid
import os

client = boto3.client('dynamodb')

def create_lambda_proxy_response(status_code, response_string):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin' : '*', # Required for CORS support to work
            'Access-Control-Allow-Credentials' : True, # Required for cookies, authorization headers with HTTPS
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response_string)
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

        return create_lambda_proxy_response(200, "Success! {} was added to the database".format(name))
    except ClientError as e:
        print(e.response["Error"]["Message"])
        return create_lambda_proxy_response(500, "Seems to be a server error... logging!")
    
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
        return create_lambda_proxy_response(409, "{} already exists in the database!".format(name))
    else:
        return create_item(name, link)

def lambda_handler(event, context):
    try:
        body_json = json.loads(event["body"])
        if "link" not in body_json:
            return create_lambda_proxy_response(400, "You need to format your body as a \"link\": \"(Destination)\"")

        link = body_json["link"]
        if ("pathParameters" not in event or
            event["pathParameters"] is None or
            "name" not in event["pathParameters"]):
            return create_random(link)
        else:
            name = event["pathParameters"]["name"]
            return create_named(name, link)
    except json.JSONDecodeError:
        return create_lambda_proxy_response(400, "You need to format your body as json with structure of \"link\": \"(Destination)\"")

