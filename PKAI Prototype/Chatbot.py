#Packages Import
import json
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from Chatbots.ChatbotFunctions import CheckAndFollowUp, Reporting
from support_Functions.Json_To_Miner import To_Miner
from Sketch_To_BPMN import Sketch_to_BPMN
import streamlit_mermaid as stmd
from support_Functions.Functions import mm, graphCreation, GetRunningMemory, ProcessSummary, generate_hash_with_random_digits, FlowSummary
import streamlit as st
import os
from support_Functions.utils import  text_to_speech, autoplay_audio, speech_to_text
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *
import os



load_dotenv()
model = os.getenv('LLM_MODEL', 'gpt-4o')
client = OpenAI()


def main(SessionsType, granularityScore):

    st.set_page_config(layout="wide") # Set page configuration first
  
    st.markdown(    # Set up styling with CSS
        """
        <style>
        .main-title {font-size: 2.5em; font-weight: bold; text-align: center; color: #4A4A4A;}
        .subtitle {font-size: 1.2em; font-weight: bold; text-align: center; color: #6D6D6D;
    }
        </style>
        """, 
        unsafe_allow_html=True
    )

    filepath = "Interviews_Questions/PreparedQuestions.json"  # Path to your JSON file

    if "Download" not in st.session_state:
        st.session_state["Download"] = False
        
    if "Mode" not in st.session_state:
        st.session_state["Mode"] = "Writing"
    
    if "feedback" not in st.session_state:
        st.session_state["feedback"] = []

    if "initialized" not in st.session_state:
        if "ValidatedCANVA" in st.session_state:
                st.session_state["CANVA"] = st.session_state["ValidatedCANVA"]
        else:  
            with open(filepath, 'r') as file:
                data = json.load(file)
                st.session_state["CANVA"] = data
        
        st.session_state["initialized"] = True
    #st.write (st.session_state)


    st.markdown("<h1 class='main-title'>💬 Process Discovery Assistant 🪄</h1>", unsafe_allow_html=True)
    
    # Create a mode selection option
    mode_options = ["Writing", "Audio"]
    selected_mode = st.selectbox("Choose Input Mode", mode_options, index=mode_options.index(st.session_state["Mode"]))
    st.session_state["Mode"] = selected_mode

    col0, col1, col2, col3 = st.columns([1, 10, 10, 2])  # Adjust column width ratios if needed

    if st.session_state["Mode"] == "Audio":
        with col0:
            container0 = st.container(height=520, border=False)
            # Create footer container for the microphone and text input
            footer_container = st.container()
            with footer_container:
                # Audio input
                audio_bytes = audio_recorder(text ="Record", icon_size= "2x")        

    with col1: #Session_State and Variables Init
        st.markdown('<div class="subtitle">Provide Insights</div>', unsafe_allow_html=True)
        container1 = st.container(height=500)
        with container1:
            if "messages" not in st.session_state:
                # Initialize chat messages
                st.session_state["messages"] = [{"role": "assistant", "content": "Hello, are you ready to model your process? 👇"}]

            if "transcript_to_edit" not in st.session_state:
                st.session_state.transcript_to_edit = None

            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

    with col2: #Mermaid Schema Init
        st.markdown('<div class="subtitle">Model Overview</div>', unsafe_allow_html=True)
        container2 = st.container(height=500)
        #First Mermaid
        if "Mermaid" not in st.session_state.keys():
            st.session_state["Mermaid"] = ""

        with container2:#Display previous mermaid
            if st.session_state["Mermaid"] != "":
                graph = st.session_state["Mermaid"]
                stmd.st_mermaid(graph, width=700, height=500, key= generate_hash_with_random_digits(graph))

            message = GetRunningMemory(st.session_state)

    with col3: #Mermaid Schema Update
        container3 = st.container(height=20, border = False)
        if st.button("Update Model" ):
            st.session_state["feedback"] = []
            feedback = st.text_input("Feedback on the Model:")
            if feedback:
                st.session_state["feedback"] += [feedback]
                with col2: #Mermaid Schema Drawing
                    with container2:
                        if "Mermaid" in st.session_state.keys():
                            #When there is already an existings mermaid graph.
                            mermaid = st.session_state["Mermaid"]
                            ProcessDescription = FlowSummary(message)

                            ProcessDescription += " \n\n Note: Take care to this aspect to generate the Mermaid Flow chart: " + str(feedback)

                            graph = graphCreation(ProcessDescription, mermaid)
                            st.session_state["Mermaid"] = graph
                            mm(graph)
                            stmd.st_mermaid(graph, width=700, height=500, key= generate_hash_with_random_digits(graph))
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.session_state["show_image"] = False
            if len(message)< 300:
                st.write("Not enough information. Answer to more questions")

            else:  
                with col2: #Mermaid Schema Drawing
                    with container2:
                        if "Mermaid" in st.session_state.keys():
                            #When there is already an existings mermaid graph.
                            mermaid = st.session_state["Mermaid"]
                            ProcessDescription = FlowSummary(message)
                            # Generate and display Mermaid graph in second column

                            graph = graphCreation(ProcessDescription, mermaid)
                            st.session_state["Mermaid"] = graph
                            mm(graph)
                            stmd.st_mermaid(graph, width=700, height=500, key= generate_hash_with_random_digits(graph))
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.session_state["show_image"] = False
    

       
    if st.session_state["Mode"] == "Audio":  #Chatbot Audio Version                                                                                                                               
        if audio_bytes: 
            with st.spinner("Transcribing..."):
                webm_file_path = "temp_audio.mp3"
                with open(webm_file_path, "wb") as f:
                    f.write(audio_bytes)

                transcript = speech_to_text(webm_file_path)
                #os.remove(webm_file_path)  # Clean up the audio file after transcription

                if transcript:
                    st.session_state.transcript_to_edit = transcript  # Store transcript for editing
                    st.session_state["EditingMode"] = 0
        with col1:
            with container1:
                # Display the option to edit the transcript if needed
                if st.session_state.transcript_to_edit and st.session_state["EditingMode"] == 0:
                    with st.chat_message("user"):
                        edit_input = st.text_input("Edit your answer if necessary", st.session_state.transcript_to_edit)

                        if st.button("Submit Answer", key="submit_answer_button"):
                            st.write("Input validated")

                            st.session_state.transcript_to_edit = None  # Clear the editable transcript
                            st.session_state["EditingMode"] = 1
                            transcript = None
                            audio_bytes = None
                            #os.remove(webm_file_path)  # Clean up the audio file after transcription
                            prompt = edit_input
      
                            st.session_state.messages.append({"role": "user", "content": edit_input})
                            #st.write({"role": "user", "content": prompt})

                            with col1:
                                with container1:
                                    with st.spinner("Thinking🤔..."):
                                        prompt, question = CheckAndFollowUp(prompt, GranularityScore = granularityScore)
                                        audio_file = text_to_speech(question)
                                        st.session_state.messages.append({"role": "assistant", "content": question})

                                        with st.chat_message("assistant"):
                                                st.markdown(question)
                                                autoplay_audio(audio_file)

    if st.session_state["Mode"] == "Writing": #Chatbot Writing Version
        if prompt := st.chat_input("Please provide a lot of process insights 🫵"):

            st.session_state.messages.append({"role": "user", "content": prompt})
            with col1:
                with container1:
                    with st.chat_message("user"):
                        st.markdown(prompt)
                
                    with st.spinner("Thinking🤔..."):
                        prompt, question = CheckAndFollowUp(prompt, GranularityScore = granularityScore)    
                        st.session_state.messages.append({"role": "assistant", "content": question})
                    
                    with st.chat_message("assistant"):
                        st.markdown(question)
             

        # Finish interview button positioned in the bottom-right corner
    
    with col3: # Final Outputs Sending
        container = st.container(height=340, border = False)
        #col31, col32, col33 = st.columns([0.19, 1.1, 0.001])
        with col3:
          if st.button("Stop Interview", key = "Stopping"):
            st.write ("Thank you, information will be send !")
            Memory = GetRunningMemory(st.session_state)
            print ("ok1")
            with st.spinner("Modeling 🚀 ..."):
              Processflow = FlowSummary(Memory)
            
            with st.spinner("Modeling 🚀 ..."):
              ProcessMemory = ProcessSummary(Memory)
              Sketch = To_Miner(ProcessMemory)
              Sketch_to_BPMN(Sketch, modelpathI = "Outputs/sketch (1).bpmn", modelPathO = "Outputs/bpmn (1).png")
              st.image("Outputs/bpmn (1).png", caption="Process model") # Heroku Mode (Path)
              
              st.write("Documentation has been sent")

            feedback =  st.session_state["feedback"]
            Reporting(Processflow, ProcessMemory, Memory, feedback)
            st.session_state["Download"] = True


    with col1:
      if st.session_state["Download"] == True:
        with open("Outputs.docx", "rb") as file1:
          file1_data = file1.read()

        
        with open("Outputs/sketch (1).bpmn", "rb") as file3:
            file3_data = file3.read()


        st.download_button(
                label="Download Process Documentation (Word)",
                data=file1_data,
                file_name="Process_Documentation.docx",
                mime="Process Documentation.document"
            )

        st.download_button(
                label="Download BPMN Diagram",
                data=file3_data,
                file_name="bpmn_diagram.bpmn",
                mime="High Level Process model.bpmn")
        
        if st.session_state["Mermaid"] != "":
            stmd.st_mermaid(graph, width=1500, height=2500, key= generate_hash_with_random_digits(graph))

if __name__ == "__main__":
    main(SessionsType = "Interviews", granularityScore = 6)
