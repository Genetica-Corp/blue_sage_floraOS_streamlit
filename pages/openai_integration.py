import openai
import streamlit as st
import pandas as pd

class OpenAIIntegration:
    async def generate_insights(self, data_frame, engine="gpt-3.5-turbo", max_tokens=2500):
        prompt = f"Please summarize this data: {data_frame.to_json(orient='records')}"
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a data analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response['choices'][0]['message']['content'].strip()
        except openai.error.OpenAIError as e:
            st.error(f"Failed to generate insights due to an API error: {e}")
            return "Insight generation failed."

    async def generate_action_plan(self, insights, engine="gpt-3.5-turbo", max_tokens=2500):
        prompt = f"Based on these insights, please generate an action plan: {insights}"
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a data analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response['choices'][0]['message']['content'].strip()
        except openai.error.OpenAIError as e:
            st.error(f"Failed to generate action plan due to an API error: {e}")
            return "Action plan generation failed."

    async def text_to_speech(self, text, engine="text-to-speech"):
        try:
            response = await openai.Audio.create(
                model="whisper-1",
                prompt=text
            )
            return response.audio
        except openai.error.OpenAIError as e:
            st.error(f"Failed to convert text to speech due to an API error.")
            return None