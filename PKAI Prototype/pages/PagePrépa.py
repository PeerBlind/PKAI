import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import necessary libraries and database configuration
import streamlit as st
import pandas as pd
import pyodbc
from io import StringIO
from streamlit_sortables import sort_items
import time
from database_auth import get_database_connection, fetch_questions
import json
from Interviews_Questions.HelpQuestion import suggestQuestions, answerQuestions,read_pdf

st.set_page_config(layout="wide")

# Fetch unique authors from the database with caching

max_questions = st.session_state.get("max_questions", 30)

with open("Interviews_Questions/PreparedQuestions.json", 'r') as file:
    data = json.load(file)

if "selected_questions" not in st.session_state:
    st.session_state.selected_questions = data["Questions"]
if "exceeded_max_limit" not in st.session_state:
    st.session_state.exceeded_max_limit = False


# Create two columns for layout
col1, col2 = st.columns(2)
col1, col2 = st.columns([8, 10]) 

# First column: Select and add questions
with col1:

    # Upload PDF
    st.subheader("🤖 Enhance your Business Process Discovery 🕵🏻")
    st.markdown("Upload Documentation")
    pdf_file = st.file_uploader("Choose a PDF file", type="pdf")


    process_input = st.text_input("Enter the process you want to analyze:")
    question_input = st.text_input("Enter your question about documentation you want to analyze:")

    if pdf_file and process_input:
        # Read the uploaded PDF file
        with st.spinner("Reading and processing the documentation..."):
            documentation = read_pdf(pdf_file)

        # Suggest questions
        if st.button("Generate Questions"):
            with st.spinner("Generating relevant questions..."):
                
                try:
                    suggested_questions = suggestQuestions(documentation, process_input)
                    st.subheader("Suggested Questions")
                    st.write(suggested_questions)
                except Exception as e:
                    st.error(f"An error occurred: {e}")


    if pdf_file and question_input:
                # Read the uploaded PDF file
        with st.spinner("Reading and processing the documentation..."):
            documentation = read_pdf(pdf_file)

        # Suggest questions
        if st.button("Answer"):
            with st.spinner("Finding relevant insights..."):
                
                try:
                    answerQuestions = answerQuestions(documentation, question_input)
                    st.subheader("Insights from documentation")
                    st.write(answerQuestions)
                except Exception as e:
                    st.error(f"An error occurred: {e}")


    st.subheader("Add a New Question (user suggestions)")
    with st.form("new_question_form"):
        new_question = st.text_input("New Question")
        submitted = st.form_submit_button("Add Question")

        if submitted and new_question:
            st.session_state.selected_questions.append(new_question)
            st.rerun()

# Second column: Organize selected questions
with col2:
    st.header("Organize Your Selected Interview Questions")

    # Initialiser l'état de session si nécessaire
    if "selected_questions" not in st.session_state:
        st.session_state.selected_questions = []  # Exemple de questions sélectionnées : ["Question 1", "Question 2"]

    # Ajouter la logique principale
    if st.session_state.selected_questions:
        # Trier les questions
        sorted_questions = sort_items(items=st.session_state.selected_questions, direction="vertical")
        st.session_state.selected_questions = sorted_questions

        # Sous-titre pour les questions triées
        st.subheader("Selected Questions")
        expected_outputs = {}

        for i, question in enumerate(sorted_questions, 1):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{i}. {question}")

                # Champ pour ajouter un expected output
                key = f"expected_output-{i}"
                expected_output = st.text_input(f"Expected Output:", key=key)
                expected_outputs[question] = expected_output
                # Assigner "None" si aucun expected output n'est défini
                expected_outputs[question] = expected_output if expected_output.strip() else "None"

            with col2:
                # Bouton pour supprimer une question
                if st.button(f"Remove", key=f"remove-{i}"):
                    st.session_state.selected_questions.remove(question)
                    st.rerun()

        # Validation des questions et expected outputs
        if st.button("Validate and Continue"):
            st.session_state["validated_questions"] = [
                {"question": question, "expected_output": expected_outputs[question]}
                for question in sorted_questions
            ]
            st.session_state["validated"] = True
            st.success("Questions and expected outputs have been validated!")
            st.write("Validated Questions:", st.session_state["validated_questions"])

            
    else:
        st.write("No questions selected.")

    if "validated" in st.session_state  and "ValidatedCANVA" not in st.session_state:
        st.session_state["ValidatedCANVA"] = {}
        Questions = []
        Expected_Outputs = ["None", "None"] #For starting and For the first introductive question

        Questions += [item["question"] for item in st.session_state["validated_questions"]]
        Expected_Outputs += [item["expected_output"] for item in st.session_state["validated_questions"]]

        st.session_state["ValidatedCANVA"]["Questions"] = Questions
        st.session_state["ValidatedCANVA"]["Expected Outputs"] = Expected_Outputs

        #st.write (st.session_state)

# Define template download functionality
def generate_template_csv():
    template_data = pd.DataFrame(columns=["question_description", "question_expectedOutput"])
    csv = StringIO()
    template_data.to_csv(csv, index=False)
    return csv.getvalue().encode('utf-8')

# Sidebar section for CSV import
st.sidebar.title("Suggest your own survey")
st.sidebar.download_button(
    label="Download Template CSV",
    data=generate_template_csv(),
    file_name="question_template.csv",
    mime="text/csv"
)

# Delimiter Selection
delimiter = st.sidebar.selectbox("Select CSV Delimiter", options=[",", ";", "|"], index=0)

# CSV Upload and Mapping Section
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, delimiter=delimiter)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        df = None

    if df is not None:
        st.write("Preview of Uploaded CSV:")
        st.dataframe(df.head())
        csv_columns = list(df.columns)
        
        question_description_col = st.selectbox("Select column for Question Description", csv_columns)
        expected_output_col = st.selectbox("Select column for Expected Output", csv_columns)

        if st.button("Submit CSV"):
            existing_descriptions = fetch_existing_descriptions()
            ignored_questions = []
            new_questions = []

            connection = get_database_connection()
            if connection:
                cursor = connection.cursor()
                insert_query = """
                    INSERT INTO dbo.Questions (question_description, question_author, question_expectedOutput)
                    VALUES (?, 'CSV IMPORT', ?)
                """
                for _, row in df.iterrows():
                    question_description = row[question_description_col]
                    expected_output = row[expected_output_col]

                    if question_description in existing_descriptions:
                        ignored_questions.append(question_description)
                        continue

                    try:
                        cursor.execute(insert_query, (question_description, expected_output))
                        existing_descriptions.add(question_description)
                        new_questions.append(question_description)
                    except pyodbc.Error as e:
                        st.error(f"Error inserting row: {e}")
                        connection.rollback()
                        st.stop()
                connection.commit()
                cursor.close()
                connection.close()
                
                # Clear the question cache and refresh the list
                fetch_questions.clear()
                
                # Update selected questions in session state
                for question in new_questions:
                    if len(st.session_state.selected_questions) < st.session_state.get("max_questions", 5):
                        st.session_state.selected_questions.append(question)
                    else:
                        st.warning("Maximum of selected questions reached. Not all new questions may be selected.")
                        break

                # Display results
                if new_questions:
                    st.success("The following questions were successfully imported:")
                    for q in new_questions:
                        st.write(f"- {q}")
                
                if ignored_questions:
                    st.warning("The following duplicated questions were ignored:")
                    for q in ignored_questions:
                        st.write(f"- {q}")
                
                st.rerun()  # Refresh the display to show updated questions list