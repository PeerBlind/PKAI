from docx import Document
import pandas as pd
from support_Functions.Functions import supprimer_contenu_bpmn
import json

def reset():

    #BPMN files:
    supprimer_contenu_bpmn("Outputs/sketch.bpmn")
    supprimer_contenu_bpmn("Empty BPMN.bpmn")

    #Question CANVA
    canva_filepath = "Interviews Questions/Question Canva.json"
    questions_filepath = "Interviews Questions/Questions.json"

    # Load content from Question Canva.json
    with open(canva_filepath, 'r') as canva_file:
        canva_data = json.load(canva_file)

    # Overwrite Questions.json with the content from Question Canva.json
    with open(questions_filepath, 'w') as questions_file:
        json.dump(canva_data, questions_file, indent=4)


reset()