import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(layout="wide")

# Home page content
st.title("Welcome to the Interview Process Modeling App")

st.subheader("Instructions: ")
st.write("""
**1.	Adopt the Organization’s Perspective, Not Your Personal Viewpoint.** \n
    o Example 1: “I’m cooking a pizza” (Incorrect) → “The cook is preparing a pizza” (Correct). \n
    o Example 2: “Pierre is managing delivery” (Incorrect) → “The delivery person is managing delivery” (Correct). \n\n
**2.	For Questions That Extend Beyond the Current Process (AS-IS): Avoid Guessing.**\n
If an action is not performed, not managed by you or your company, or you are unsure how it is handled, state it clearly.\n
    o Example 1:\n
         Question: “How do you ensure the delivery person delivers the pizza to the correct customer? Is there a system in place?”\n
         Response: “We should implement a tracking system to geolocate the delivery person” (Incorrect).\n
         Correct Response: “I don’t know,” “Currently not managed,” “Not handled,” or “Not within my scope.”\n\n
**3.	Avoid Implicit Statements: Be Explicit, Even When Something Seems Obvious.**\n
    o Example 1: “If ingredients run out, I go to the store to buy more. Then, I cook the pizza.” (Incorrect).\n
    o Example 2: “If ingredients are unavailable, I go to the store to buy more. Afterward, I can start cooking. If ingredients are available, I can cook immediately.” (Correct).\n\n
**4.	End the Session Properly:**\n
    o	Press the “Stop the Interview” button once (approximately 1 minute for modeling).\n
    o	Download both the documentation (.docx) and the Process model (.bpmn) files.\n

""")

st.sidebar.success("Select the Chatbot page to get started.")
