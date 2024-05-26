# Streamit 1.35.0
# OpenAI 1.30.3

import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["openaikey"])

# set some useful values
filename = "world_df.csv"
assistant_name = "data-analyst-v0.1"

# Check if file is already uploaded to OpenAI
filelist = client.files.list(purpose="assistants")
filenames =  [x.filename for x in filelist.data]
file_uploaded = True if filename in filenames else False

# Upload a file with an "assistants" purpose or use existing one
if not file_uploaded:
  file = client.files.create(
    file=open(filename, "rb"),
    purpose='assistants'
  )
else:
  for f in filelist:
    if f.filename == filename:
      file = client.files.retrieve(f.id)
      break

# Check if assistant already exists
assistant_list = client.beta.assistants.list()
assistant_names =  [x.name for x in assistant_list.data]
assistant_exists = True if assistant_name in assistant_names else False

if not assistant_exists:
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
  
# Create a thread with instruction for creating a graph

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

# Run with streaming

from typing_extensions import override
from openai import AssistantEventHandler
 
# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.
 
class EventHandler(AssistantEventHandler):    
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
      
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)
 
# Then, we use the `stream` SDK helper 
# with the `EventHandler` class to create the Run 
# and stream the response.
 
with client.beta.threads.runs.stream(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="create a downloadable file for the graph",
  event_handler=EventHandler(),
) as stream:
  stream.until_done()


# Find the file that has been created

filelist = client.files.list(purpose="assistants_output")
image_list = [x for x in filelist.data if "png" in x.filename]
id = image_list[-1].id # the last in the list is the latest

client.files.retrieve(id)

# File

image_data = client.files.content(id)
image_data_bytes = image_data.read()

#with open("./my-image.png", "wb") as file:
#    file.write(image_data_bytes)

st.image(image_data_bytes)