# Library versions used
# Note that the OpenAI assistants library is in beta 
# and subject to change, so it is important to use the 
# the correct version
# Streamlit 1.35.0
# OpenAI 1.30.5

import streamlit as st
from openai import OpenAI
import time

client = OpenAI(api_key=st.secrets["openaikey"])

# set some useful values
assistant_name = "data-analyst-v0.1"

# This utility function waits for a run to complete. 
# The code is copied directly from the OpenAI Cookbook.
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

import json

# This utility function uses the IPython function 'display' to pretty-print the JSON of the
# various entities created in the Assistants API. This code is copied directly from the OpenAI Cookbook.

def show_json(obj):
    st.write(json.loads(obj.model_dump_json()))

def get_local_file():
   # TODO download a file and save it locally
   return "world_df.csv"

def upload_file_for_assistant(filename):
   # Check if file is already uploaded to OpenAI
    filelist = client.files.list(purpose="assistants")
    filenames =  [x.filename for x in filelist.data]

    # Upload a file with an "assistants" purpose or use existing one
    if not filename in filenames:
        file = client.files.create(
            file=open(filename, "rb"),
            purpose='assistants'
        )
    else:
        for f in filelist:
            if f.filename == filename:
                file = client.files.retrieve(f.id)
                break

    return file

def get_assistant(file):
    # Check if assistant already exists
    assistant_list = client.beta.assistants.list()
    assistant_names =  [x.name for x in assistant_list.data]

    if not assistant_name in assistant_names:
    # Create an assistant using the file ID
        assistant = client.beta.assistants.create(
            name = "data-analyst-v0.1",
            instructions="You are a data analyst",
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}],
            tool_resources={
            "code_interpreter": {
                "file_ids": [file.id]
            }
            }
        )
    else:
        for a in assistant_list:
            if a.name == assistant_name:
                assistant = client.beta.assistants.retrieve(a.id)
                break
    return assistant   

def create_thread(file):
    thread = client.beta.threads.create(
        messages=[
            {
            "role": "user",
            "content": "Using the csv file attached, display a graph of 'Year' against 'Anuual CO2 emissions",
            "attachments": [
                {
                "file_id": file.id,
                "tools": [{"type": "code_interpreter"}]
                }
            ]
            }
        ]
    )
    return thread

def run_assistant_and_wait_for_result(assistant, thread):
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="create a downloadable file for the graph",
    )   
    wait_on_run(run, thread)

def get_generated_image():
    # Find the file that has been created
    filelist = client.files.list(purpose="assistants_output")
    image_list = [x for x in filelist.data if "png" in x.filename]
    id = image_list[-1].id # the last in the list is the latest

    client.files.retrieve(id)

    image_data = client.files.content(id)
    return image_data.read()


### Main code starts here ###

# Get a local file to upload to the assistant
filename = get_local_file()
# upload the file and retrieve the file object
file = upload_file_for_assistant(filename)
# Retrieve existing, or create new, assistant
assistant = get_assistant(file)

thread = create_thread(file)

run_assistant_and_wait_for_result(assistant, thread)

# If things go wrong you might want to see the messages
#messages = client.beta.threads.messages.list(thread_id=thread.id)
#show_json(messages)

image_data_bytes = get_generated_image()

# If you want to save the file, do something like this...
#with open("./my-image.png", "wb") as file:
#    file.write(image_data_bytes)

#Display the chart
st.image(image_data_bytes)