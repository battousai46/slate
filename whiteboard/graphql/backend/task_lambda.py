import json


def handler(event, context):
    # Log the incoming event for debugging purposes
    print("Received event:", json.dumps(event))

    # For an AppSync GraphQL query that expects a 'hello' field,
    # simply return a greeting message.
    return "Hello from Lambda!"
