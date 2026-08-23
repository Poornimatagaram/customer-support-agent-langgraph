import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # reads your .env file

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-3.6-flash")

response = model.generate_content("Say hello in one short sentence.")
print(response.text)