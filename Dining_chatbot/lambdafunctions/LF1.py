import json
import os
import boto3

# Initialize the SQS client
sqs = boto3.client('sqs')


QUEUE_URL = os.environ['QUEUE_URL']

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        "sessionState": {
            "dialogAction": {
                "slotToElicit": slot_to_elicit,
                "type": "ElicitSlot"
            },
            "intent": {
                "name": intent_name,
                "slots": slots
            },
            "sessionAttributes": session_attributes
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": message
            }
        ]
    }


def handle_greeting_intent(intent):
    return {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message': {
                'contentType': 'PlainText',
                'content': "Hello! How can I assist you with dining suggestions today?"
            }
        }
    }

def handle_thank_you_intent(intent):
    return {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message': {
                'contentType': 'PlainText',
                'content': "You're welcome! Enjoy your meal."
            }
        }
    }

# Function to validate Location and Cuisine
def validate_slot(slot_name, slot_value):
    valid_locations = ['Manhattan', 'NYC', 'New York City']
    valid_cuisines = ['Chinese', 'Italian', 'Mexican']
    
    if slot_name == 'Location':
        return slot_value in valid_locations, f"Please choose a valid location: {', '.join(valid_locations)}"
    elif slot_name == 'Cuisine':
        return slot_value in valid_cuisines, f"Please choose a valid cuisine: {', '.join(valid_cuisines)}"
    return True, ""
    
def handle_dining_suggestions_intent(intent, session_id):
    slots = intent['interpretations'][0]['intent']['slots']
    session_attributes = intent.get('sessionAttributes', {})
    intent_name = 'DiningSuggestionsIntent'
    # Define the required slots and their corresponding messages
    required_slots = {
        'Location': 'What city or city area are you looking to dine in?',
        'Cuisine': 'What type of cuisine would you like to try?',
        'DiningTime': 'What time would you like to dine?',
        'Number': 'How many people are in your party?',
        'Email': "What's your email address to send the recommendations?"
    }
    # Check if all required slots are filled
    for slot_name, prompt in required_slots.items():
        if slots.get(slot_name) is None or not slots[slot_name].get('value'):
            return elicit_slot(session_attributes, intent_name, slots, slot_name, prompt)
        
        slot_value = slots[slot_name]['value'].get('interpretedValue', slots[slot_name]['value'])
        
        if slot_name in ['Location', 'Cuisine']:
            is_valid, error_message = validate_slot(slot_name, slot_value)
            if not is_valid:
                return elicit_slot(session_attributes, intent_name, slots, slot_name, error_message)

       
    # All slots are filled, process the dining suggestion request
    location = slots['Location']['value'].get('interpretedValue', slots['Location']['value'])
    cuisine = slots['Cuisine']['value'].get('interpretedValue', slots['Cuisine']['value'])
    dining_time = slots['DiningTime']['value'].get('interpretedValue', slots['DiningTime']['value'])
    num_people = slots['Number']['value'].get('interpretedValue', slots['Number']['value'])
    email = slots['Email']['value'].get('interpretedValue', slots['Email']['value'])
    
    message = {
        'Location': location,
        'Cuisine': cuisine,
        'DiningTime': dining_time,
        'Number': num_people,
        'Email': email, 
        'userId' : session_id
    }
    
    # Send the message to SQS
    try:
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message)
        )
        print(f"Message sent to SQS: {message}")
    except Exception as e:
        print(f"Error sending message to SQS: {str(e)}")
        # You might want to handle this error more gracefully
    

    
    # Confirm to the user that their request was received
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": intent_name,
                "slots": slots,
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": f"Thank you! I've received your request for {cuisine} restaurant suggestions in {location} for {num_people} people at {dining_time}. I'll send my recommendations to {email} shortly."
            }
        ]
    }

def dispatch_handler(intent, session_id):
    intent_name = intent['interpretations'][0]['intent']['name']
    
    if intent_name == 'GreetingIntent':
        return handle_greeting_intent(intent)
    elif intent_name == 'ThankYouIntent':
        return handle_thank_you_intent(intent)
    elif intent_name == 'DiningSuggestionsIntent':
        return handle_dining_suggestions_intent(intent, session_id)
    else:
        return {
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Failed',
                'message': {
                    'contentType': 'PlainText',
                    'content': "I'm sorry, I'm not sure how to help you at this moment! :("
                }
            }
        }

def lambda_handler(event, context):
    session_id = event['sessionId']
    return dispatch_handler(event, session_id)