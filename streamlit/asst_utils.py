# Note that the OpenAI assistants library is in beta and subject to change
# This code was written for:
# Streamlit 1.35.0
# OpenAI 1.30.5

import streamlit as st
from openai import OpenAI
import time

class Data_Assistant:

    assistant_name = "data-analyst-v0.1"
    system_prompt = """You are a data analyst. 
                       Use the attached data file to create a graph from the data with the instructions given."""
    prompt = "Display a bar chart of 'Year' against 'Annual CO2 emissions'"
    image_file_name = "image_output.png"

    def __init__(self):
        self.get_client()

    def get_client(self):
        self.client = OpenAI(api_key=st.secrets["openaikey"])

    def upload_file_for_assistant(self, file_to_upload):
    # Check if file is already uploaded to OpenAI
        filelist = self.client.files.list(purpose="assistants")
        filenames =  [x.filename for x in filelist.data]

        # Upload a file with an "assistants" purpose or use existing one
        if not file_to_upload.name in filenames:
            file = self.client.files.create(
                file=file_to_upload,
                purpose='assistants'
            )
        else:
            for f in filelist:
                if f.filename == file_to_upload.name:
                    file = self.client.files.retrieve(f.id)
                    break

        return file


    def get_assistant(self, file):
        # Check if assistant already exists
        assistant_list = self.client.beta.assistants.list()
        assistant_names =  [x.name for x in assistant_list.data]

        if not self.assistant_name in assistant_names:
        # Create an assistant using the file ID
            assistant = self.client.beta.assistants.create(
                name = "data-analyst-v0.1",
                instructions=self.system_prompt,
                model="gpt-4o",
                temperature=0,
                tools=[{"type": "code_interpreter"}],
                tool_resources={
                "code_interpreter": {
                    "file_ids": [file.id]
                    }
                }
            )
        else:
            for a in assistant_list:
                if a.name == self.assistant_name:
                    assistant = self.client.beta.assistants.retrieve(a.id)
                    break
        return assistant   

    def create_thread(self, file, prompt):
        self.thread = self.client.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content": prompt,
                "attachments": [
                    {
                    "file_id": file.id,
                    "tools": [{"type": "code_interpreter"}]
                    }
                ]
                }
            ]
        )
        return self.thread

    def get_image_file(self):
        # Find the file that has been created
        filelist = self.client.files.list(purpose="assistants_output")
        #st.write(filelist)
        image_list = [x for x in filelist.data if self.image_file_name in x.filename]
        #st.write(image_list)
        if len(image_list) > 0:
            return image_list[0].id # should be only one
        else: 
            return None
        
    def run_assistant_and_wait_for_result(self, assistant, thread, status_field, display_messages = False):
        return # uncomment this for debugging so the model does not run
        id = self.get_image_file()
        if id: self.client.files.delete(id)

        
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions=f"create a downloadable file for the graph. The file should be called {self.image_file_name}",
        )   
        
        while run.status == 'queued' or run.status == 'in_progress':
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            time.sleep(1.0)
            status_field.write(f"Status: {run.status}")

        if run.status == 'completed': 
            messages = self.client.beta.threads.messages.list(
                        thread_id=thread.id)
            if display_messages: status_field.write(messages)
            
        return run.status

    def get_generated_image(self):
        id = self.get_image_file()
        self.client.files.retrieve(id)
        image_data = self.client.files.content(id)

        return image_data.read()
    
    def delete_ALL_assistant_generated_files(self):
            # THIS IS DESTRUCTIVE - ONLY USE IF YOU UNDERSTAND THE CONSEQUENCES
            # OTHERWISE USE THE OPENAI DASHBOARD TO REMOVE FILES
            # THIS FUNCTION WILL REMOVE *ALL* ASSISTANT GENERATED FILES 
            # NO MATTER WHEN THEY WERE CREATED, NOT JUST FOR THE CURRENT SESSION
            filelist = self.client.files.list(purpose="assistants_output")
            for f in filelist:
                self.client.files.delete(f.id)
                

