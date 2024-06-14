# [From Data to Visualization with the OpenAI Assistants API and GPT-4o](https://medium.com/towards-data-science/from-data-to-visualization-with-the-openai-assistants-api-and-gpt-4o-69af0cac5118)

## We explore the Code Completion tool from OpenAI's Assistants API to create visualizations directly from data


This folder contains the code and data to support the article above - in particular, it implements a Streamlit app based on the original code (see parent folder).

## Description and files

We explore chart creation using OpenAI's Assistants and Code Interpreter.

_Files_

- the main Streamlit app code is in the file `app.py`
- ``world_cf.csv`` is the data file
- ``meals2.csv`` is a data file
- ``asst_utils.py`` is an implementation of the original Jupter Note code in the form of a library class.
- ``.streamlit`` this folder does not exist in the repo but should be present and contain a Streamlit secrets file that contains a vaild OpenAI API key

### _Important note number 1! You must read this before running the code._ 

In the file ``asst_utils.py`` beginning on line 98 you will see that the method that runs the model has a `return` statement inserted at the beginning meaning that the code in this method will not be called. This is deliberate - the idea being that you will not accidentally be spending money until you are happy that the app is running. When you have the code running, comment out or delete this line.

    def run_assistant_and_wait_for_result(self, assistant, thread, status_field, display_messages = False):
            # comment out the next line to run the model
            # uncomment it for debugging so the model does not run
            return 
            id = self.get_image_file()
            if id: self.client.files.delete(id)

### _Important note number 2!_

There is a facility to deleted the files that are created by the assistant. __*THIS IS DESTRUCTIVE*__. It will delete __*ALL*__ files no matter when they were created and no matter which assistant created them, so use with care. If you are not sure, then delete unwanted files with the OpenAI dashboard.

---
### If you find this content useful, please consider one or more of the following:

-  #### Follow me on  [Medium](https://medium.com/@alan-jones) where you can read all my articles along with thousands of others for $5 a month  
-  #### Buy my book [ _Streamit from Scratch_](https://alanjones2.github.io/streamlitfromscratch/)
-  #### Subscribe to my [free newsletter](https://technofile.substack.com/)
-  #### Visit my [web page](alanjones2.github.io)

<a href='https://ko-fi.com/M4M64THKG' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

---

_MIT licensed - if you use this code publicly then attribution is not necessary but is appreciated._

_Please note that the code in this repo is for educational and demonstration purposes. It should not be considered suitable for production._