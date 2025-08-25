from prompts.gentle_christian import prompt
from config import client

def ai_answer(msg):
    ai_input = prompt(msg)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": ai_input}],
        temperature=0.8
    )

    return response.choices[0].message.content.strip()