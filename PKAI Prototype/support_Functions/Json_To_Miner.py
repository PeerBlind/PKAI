from openai import OpenAI
from dotenv import load_dotenv
from support_Functions.Algo_Converter_JSON import algo
from support_Functions.Algo_Converter_JSONtrial import algo2
from support_Functions.Algo3 import algo3
import os
import json
import streamlit as st
import concurrent.futures
import threading
import time
from call_function_with_timeout import SetTimeout


load_dotenv()
model = os.getenv('LLM_MODEL', 'gpt-4o')
client = OpenAI()

def run_with_timeout(func, args=(), kwargs={}, timeout = 1):
    """Runs a function with a timeout. Raises TimeoutError if it exceeds the limit."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            Sketcher = None
            raise TimeoutError(f"The function '{func.__name__}' exceeded the time limit of {timeout} seconds.")
            

Algo_with_TimeOut = SetTimeout(algo, timeout= 1)
Algo2_with_TimeOut = SetTimeout(algo2, timeout= 1)
Algo3_with_TimeOut = SetTimeout(algo3, timeout= 1)

def check_Gateway(jsonrep):
    if "Gateway" in jsonrep['steps'][0].keys():
        print ("oui")
        for e in range(len(jsonrep['steps'])):
            if "Task" in jsonrep['steps'][e]:
                print("ok")
                Action = jsonrep['steps'][0]["Gateway"]["decision task"]
                Actor = jsonrep['steps'][e]["Task"]["Actor"]
                break
        #print (jsonrep)
        jsonrep['steps'].insert(0, {'Task': {'Actor': Actor, 'Action': Action[:-1], 'Type': 'Receive', 'Gateway Path': ''}})
        print (jsonrep)
    return jsonrep
    

def To_Miner(Flow):
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful BPMN Modeler tutor. From the discussion that will be provided, help me"
                    "by identifying the different tasks, events and gateways. Gateways can be exclusive, take care to report all activities and flows details "
                    "For the attribute, put '' instead of not completing it "
                    "in the case where there is no previous gateway path."
                ),
            },
            {
                "role": "user",
                "content": "Please model the following processes:" + Flow,
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "Processstructure",
                "strict": False,
                "schema": {
                    "type": "object",
                    "required": ["steps"],
                    "properties": {
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "Task": {
                                        "type": "object",
                                        "required": ["Actor", "Action", "Type", "Gateway Path"],
                                        "properties": {
                                            "Actor": {"type": "string"},
                                            "Action": {"type": "string"},
                                            "Type": {"enum": ["Send", "Receive"], "type": "string"},
                                            "Gateway Path": {"type": "string"},
                                        },
                                    },
                                    "Event": {
                                        "type": "object",
                                        "required": ["Name", "Type", "Gateway Path"],
                                        "properties": {
                                            "Name": {"type": "string"},
                                            "Type": {"enum": ["Receive", "Timer", "Send"], "type": "string"},
                                            "Gateway Path": {"type": "string"},
                                        },
                                    },
                                    "Gateway": {
                                        "type": "object",
                                        "required": ["type", "branches", "Previous Gateway Path"],
                                        "properties": {
                                            "Path": {
                                                "type": ["array", "null"],
                                                "items": {"type": "string"},
                                                "minItems": 2,
                                            },
                                            "type": {"enum": ["Exclusive Gateways"], "type": "string"},
                                            "decision task": {
                                                "if": {
                                                    "properties": {"type": {"enum": ["Exclusive Gateways"]}},
                                                },
                                                "then": {
                                                    "required": ["decision task"],
                                                },
                                                "type": "string",
                                                "nullable": True,
                                                "description": (
                                                    "For an exclusive gateway, represents the question that decides the path"
                                                ),
                                            },
                                            "Event Branches": {
                                                "if": {
                                                    "properties": {"type": {"enum": ["Event Gateways"]}},
                                                },
                                                "then": {
                                                    "required": ["Event Branches"],
                                                },
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "required": ["Event Name", "Event Type"],
                                                    "properties": {
                                                        "Event Name": {"type": "string"},
                                                        "Event Type": {
                                                            "enum": ["Message", "Timer", "Start", "Finish"],
                                                            "type": "string",
                                                        },
                                                        "Gateway Path": {"type": "string"},
                                                    },
                                                },
                                                "description": (
                                                    "Directly specify events within the event gateway"
                                                ),
                                            },
                                            "Previous Gateway Path": {
                                                "type": "string",
                                                "description": "Path leading to the current gateway",
                                            },
                                        },
                                        "additionalProperties": False,
                                    },
                                },
                                "additionalProperties": False,
                            },
                        },
                    },
                    "additionalProperties": False,
                },
            },
        },
    )
    json_rep= json.loads(response.choices[0].message.content)

    print("json_rep: " + str(json_rep))

    json_rep = check_Gateway(jsonrep=json_rep)

    try:
        is_done, is_timeout, erro_message, Sketcher = Algo_with_TimeOut(json_rep) 
        if is_done == False:
            Sketcher = None
    except TimeoutError as e:
        print(e)
        Sketcher = None 
    except Exception as e:
        print(f"Error in algo function: {e}")
        Sketcher = None

    if Sketcher == None:
        print ("failed with algo1")
        try:
            is_done, is_timeout, erro_message, Sketcher = Algo2_with_TimeOut(json_rep) 
            if is_done == False:
                Sketcher = None 
        except TimeoutError as e:
            print(e)
            Sketcher = None
        except Exception as e:
            print(f"Error in algo function: {e}")
            Sketcher = None
        
    if Sketcher == None:
        print ("failed with algo2")
        try:
            is_done, is_timeout, erro_message, Sketcher = Algo3_with_TimeOut(json_rep)  # Wrap the `algo` call in a try-except block.
            if is_done == False:
                Sketcher = None
        except TimeoutError as e:
            print(e)
            Sketcher = None
        except Exception as e:
            print(f"Error in algo function: {e}")
            Sketcher = None


        if Sketcher == None:
            print ("failed with algo3")
            st.write("Modeling Failed, please retry")
            Sketcher = "Failed: Model"
            return Sketcher

    return Sketcher
