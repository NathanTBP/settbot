import os
import json
import requests
import time
import logging
from openai import OpenAI
#from app import create_app

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

ACCESS_TOKEN = os.getenv("ZAP_KEY")
NATHAN_WAID = os.getenv("NATHAN_WAID")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("ZAP_VERSION")

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

SETT_BOT_ID = os.getenv("SETT_BOT_ID")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def send_message(formated_text_message):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

    response = requests.post(url, data=formated_text_message, headers=headers)
    if response.status_code == 200:
        print("Status:", response.status_code)
        print("Content-type:", response.headers["content-type"])
        print("Body:", response.text)
        return response
    else:
        print(response.status_code)
        print(response.text)
        return response

def send_whatsapp_message(recipient):
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "template",
        "template": {"name": "hello_world", "language": {"code": "en_US"}},
    }
    response = requests.post(url, headers=headers, json=data)
    return response

def run_assistant(client,thread):
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve(SETT_BOT_ID)

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Wait for completion
    while True:
        if run.status == "completed":
                # Retrieve the Messages
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            new_message = messages.data[0].content[0].text.value
            print(f"Generated message: {new_message}")
            return new_message
        elif run.status in ["expired","failed","incomplete","cancelled"]:
            new_message = "Failed to execute assistant"
            print(f"Failed to execute assistant")
            return new_message
        else:
            # Be nice to the API
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            break



def generate_assistant_response(client,message_body, wa_id, name):
    # Check if there is already a thread_id for the wa_id
    # TODO
    
    if thread_id is None:
        print(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        print(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Run the assistant and get the new message
    new_message = run_assistant(client,thread)
    print(f"To {name}:", new_message)
    return new_message

def main():
    test = os.environ["OPEN_AI_KEY"]
    print(test)
    client = OpenAI()

    assistant = client.beta.assistants.retrieve(SETT_BOT_ID)
    
    #response = send_whatsapp_message()
    print(NATHAN_WAID)
    formated_text_message = get_text_message_input(
        recipient=NATHAN_WAID, text="Nathan, você está mandando muito bem! Cada ida à academia é um passo a mais rumo aos seus objetivos. Continue assim, porque você está se tornando mais forte e saudável a cada treino. Vamos nessa, campeão! 💪🏋️‍♂️"
    )
    response = send_message(formated_text_message)
    
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    main()
    logging.info("Flask app started")
    



