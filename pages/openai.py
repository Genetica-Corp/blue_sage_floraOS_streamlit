import openai
import streamlit as st
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class OpenAIIntegration:
    def __init__(self):
        self.llm = OpenAI(temperature=0.7, openai_api_key=openai.api_key)

    async def generate_insights(self, data_frame, max_tokens=150):
        prompt = f"Please summarize this data: {data_frame.to_json(orient='records')}"
        template = PromptTemplate(
            input_variables=["data"],
            template="You are a data analyst. {data}"
        )
        chain = LLMChain(llm=self.llm, prompt=template)
        try:
            response = await chain.run(data=prompt)
            return response.strip()
        except openai.error.OpenAIError as e:
            st.error(f"Failed to generate insights due to an API error: {e}")
            return "Insight generation failed."

    async def chat_response(self, user_message, max_tokens=150):
        template = PromptTemplate(
            input_variables=["message"],
            template="You are a helpful assistant. {message}"
        )
        chain = LLMChain(llm=self.llm, prompt=template)
        try:
            response = await chain.run(message=user_message)
            return response.strip()
        except openai.error.OpenAIError as e:
            st.error(f"Failed to get response due to an API error: {e}")
            return "Failed to get response."