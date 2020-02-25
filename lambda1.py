"""
Lambda Function for Dining Suggestion
"""
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def validate_dining(location, cuisine, dining_date, dining_time, num_people):
    valid_cities = ['new york', 'los angeles', 'chicago', 'san francisco', 'seattle', 'washington dc', 'boston']
    valid_cuisines = ['chinese', 'japanese', 'mexican', 'italian', 'american', 'indian']
    if location is not None and location.lower() not in valid_cities:
        return build_validation_result(False,
                                       'Location',
                                       'Sorry that currently {} is not a valid destination. Could you try a different city?'.format(location))
    if cuisine is not None and cuisine.lower() not in valid_cuisines:
        return build_validation_result(False,
                                       'Location',
                                       'Sorry that currently {} is not a valid cuisine. Could you try a different cuisine?'.format(cuisine))
   

    if dining_date is not None:
        if not isvalid_date(dining_date):
            return build_validation_result(False, 'DiningDate', 'I did not understand that, what date would you like to have the cuisine?')
        # elif datetime.datetime.strptime(dining_date, '%Y-%m-%d').date() <= datetime.date.today():
        #     return build_validation_result(False, 'DiningDate', 'Not today, pick another day.')

    if dining_time is not None:
        if len(dining_time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'DiningTime', None)

        hour, minute = dining_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'DiningTime', None)
        if hour < 0 or hour > 24:
            return build_validation_result(False, 'DiningTime', 'I am sorry that it is not a valid time. Please enter a valid time.')

    if num_people is not None: 
        if (num_people < 1):
            return build_validation_result( False, 'NumPeople', 'The minimum number of people is 1. How many people do you have?')
        if (num_people > 100):
            return build_validation_result( False, 'NumPeople', 'The maximum number of people is 100. How many people do you have?')
        
    return build_validation_result(True, None, None)


def dining(intent_request):

    location = get_slots(intent_request)["Location"]
    cuisine = get_slots(intent_request)['Cuisine']
    dining_date = get_slots(intent_request)["DiningDate"]
    dining_time = get_slots(intent_request)["DiningTime"]
    num_people = safe_int(get_slots(intent_request)["NumPeople"])
    num_phone = get_slots(intent_request)["NumPhone"]
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_dining(location, cuisine, dining_date, dining_time, num_people)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        return delegate(session_attributes, get_slots(intent_request))
    elif source == 'FulfillmentCodeHook':
        # push info to SQS: location, cuisine, dining_date, dining_time, num_people
        # Create SQS client 
        sqs = boto3.client('sqs')
        # Get URL for SQS queue
        response = sqs.get_queue_url(QueueName='chatbot_slots')
        queue_url = response['QueueUrl']

        # Send message to SQS queue
        # supported 'DataType': string, number, binary
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageAttributes={
                'location': {
                    'DataType': 'String',
                    'StringValue': location
                },
                'cuisine': {
                    'DataType': 'String',
                    'StringValue': cuisine
                },
                'dining_date': {
                    'DataType': 'String',
                    'StringValue': dining_date
                },
                'dining_time': {
                    'DataType': 'String',
                    'StringValue': dining_time
                },
                'num_people': {
                    'DataType': 'Number',
                    'StringValue': str(num_people)
                },
                'phone': {
                    'DataType': 'String',
                    'StringValue': str(num_phone)
                }
            },
            MessageBody=(
                'Information about user inputs of Dining Chatbot.'
            )
        )
        # print("SQS messageID:"+str(response['MessageId']))
    
    # In a real bot, this would likely involve a call to a backend service.
    return close(intent_request['sessionAttributes'], 'Fulfilled', {'contentType': 'PlainText',
                     'content': 'Thanks, your requirement has been recorded: {}, {}, {}, {}'.format(location, dining_time, dining_date, num_people)})


def Greeting(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    return close(session_attributes, 'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Hi there, how can I help you?'
        }
    )

def Thank_You(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    return close(session_attributes, 'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'You are welcome! Thanks for using the service. See you next time!'
        }
    )

""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestions':
        return dining(intent_request)
    # Dispatch to your bot's intent handlers
    elif intent_name == 'Greeting':
        return Greeting(intent_request)
    elif intent_name == "ThankYou":
        return Thank_You(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
