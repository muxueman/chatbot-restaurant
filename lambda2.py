"""
Lambda function integrated
"""

import json
import boto3
import urllib3
from boto3.dynamodb.conditions import Key, Attr
 

def lambda_handler(event, context):

    print("Testing CloudWatch: Call LF2 every minute.")
    # Create SQS client 
    sqs = boto3.client('sqs')
    # Get URL for SQS queue
    response = sqs.get_queue_url(QueueName='chatbot_slots')
    queue_url = response['QueueUrl']
    #print(queue_url)
    message = None
    # Receive a message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    try:
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']
        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print('Received and deleted message: %s' % message)
        # 2. gets a random restaurant recommendation for the cuisine collected through conversation from ElasticSearch
        # all information stored in sqs queue
        location = message['MessageAttributes']['location']['StringValue']
        cuisine = message['MessageAttributes']['cuisine']['StringValue']
        dining_date =  message['MessageAttributes']['dining_date']['StringValue']
        dining_time = message['MessageAttributes']['dining_time']['StringValue']
        num_people = message['MessageAttributes']['num_people']['StringValue']
        num_phone =  message['MessageAttributes']['phone']['StringValue']
        print(location, cuisine, dining_date, dining_time, num_people, num_phone)
        # use http request to search ElasticSearch index: restaurant
        sendMessage = "go to elastic search"
        
        # pick a restaurant randomly, get the business_ID (always pick first one here, need further work)
        http = urllib3.PoolManager()
        r = http.request('GET', 'https://search-restaurants-whaa3fqpkrbnkdv6c6no2i6ku4.us-east-1.es.amazonaws.com/_search?q='+str(cuisine))
        data=json.loads(r.data.decode('utf-8'))
        business_id = data['hits']['hits'][0]['_source']['business_id']
        print("elasticsearch result: " + business_id)
             
        # 3. get more information from DynamoDB
        # search DynamoDB using Business_ID
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('yelp-restaurants')
        response = table.query(
            KeyConditionExpression=Key('business_id').eq(business_id)
        )
        
        name = response['Items'][0]['business_name']
        address = response['Items'][0]['address']
        num_reviews = response['Items'][0]['num_reviews']
        rating = response['Items'][0]['rating']
        sendMessage = "Hello! For {}, we recommend the {} {} restaurant on {}. The place has {} of reviews and an average score of {} on Yelp. Enjoy!".format(location, name, cuisine, address, num_reviews, rating)
        print(sendMessage)
        
        # Create SS client
        sns = boto3.client('sns')
        # send message
        sns.publish(
            PhoneNumber = '+1'+num_phone,
            Message = sendMessage
        )
    except:
        print("SQS queue is now empty")
    # return 
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda LF2!')
    }
