import json
import boto3

client = boto3.client('lex-runtime')

def lambda_handler(event, context):
    # TODO implement
    
    response = client.post_text(
        botName='DiningTest',
        botAlias='chatbot',
        userId='100',
        sessionAttributes={
        },
        requestAttributes={
        },
        inputText = event["messages"][0]["unstructured"]["text"]
    )

    return {
        'statusCode': 200,
        'body': json.dumps(response["message"])
    }
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps('I’m still under development. Please come back later.')
    # }

