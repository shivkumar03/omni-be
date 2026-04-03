import groq, datetime, os
from dotenv import load_dotenv
load_dotenv()
client = groq.Groq(api_key=os.getenv("GROQ_API_KEY", ""))
today = datetime.datetime.now().strftime("%A, %d %B %Y")
r = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": f"You are OMNI AI assistant. Today is {today}. Answer accurately."},
        {"role": "user",   "content": "Who is the current Prime Minister of India?"}
    ],
    max_tokens=200
)
print("Answer:", r.choices[0].message.content)
