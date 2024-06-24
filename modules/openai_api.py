import os
import requests
import json
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field

class CategorizeResponse (BaseModel):
    result: bool = Field(desciption="The result of my query, is it an important email or not")

class SummarizeResponse (BaseModel):
    result: str = Field(desciption="The result of my summarized query")

def summarize_text(text):
    model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, api_key=os.getenv('OPENAI_KEY'))
    structured_llm = model.with_structured_output(SummarizeResponse, method="json_mode")
    response = structured_llm.invoke("Summarize the following email concisely in one to two SHORT sentences. Respond in JSON with `result` key, leave key details in and preserve names, dates, and links especially: " + text)
    return response.result
    # """Sends text to the GPT API for summarization."""
    # openai_api_key = os.getenv('OPENAI_KEY')

    # api_url = 'https://api.openai.com/v1/chat/completions'
    # headers = {
    #     'Authorization': 'Bearer ' + openai_api_key,
    #     'Content-Type': 'application/json',
    # }
    # data = {
    #     'model' : 'gpt-3.5-turbo',
    #     'messages': [{"role": "user", "content": 'Summarize the following email concisely in one to two SHORT sentences, leave key details in and preserve names, dates, and links especially: ' + text}],
    # }
    # response = requests.post(api_url, headers=headers, data=json.dumps(data))
    # return response.json()

def categorize_text(text):
    model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, api_key=os.getenv('OPENAI_KEY'))
    structured_llm = model.with_structured_output(CategorizeResponse, method="json_mode")
    response = structured_llm.invoke("Analyze the following email body text, decide if it should be marked as important. Respond in JSON with `result` key. Important emails include: personal emails, time sensitive notifications, alerts, and action items, these should be responded with a yes. Things that should NOT be marked include promotions, ads, order updates, and welcome messages from brands, if they fit into those categories respond no. Here is the email: "  + text)
    return response.result

def summarize(transcript, percent):
    if percent == 100:
        return transcript

    # Summarize transcript using rapidapi
    api_url = "https://text-analysis12.p.rapidapi.com/summarize-text/api/v1.1"

    payload = {
        "language": "english",
        "summary_percent": percent,
        "text": transcript
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": os.getenv('RAPIDAPI_KEY'),
        "X-RapidAPI-Host": "text-analysis12.p.rapidapi.com"
    }

    response = requests.post(api_url, json=payload, headers=headers)
    if not response.json()['ok']:
        raise ValueError(response.json()['msg'])

    summarized_transcript = response.json()['summary']
    return summarized_transcript