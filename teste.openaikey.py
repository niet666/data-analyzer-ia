import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("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"))

resposta = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Você é um assistente de teste."},
        {"role": "user", "content": "Olá, tudo funcionando?"}
    ]
)

print(resposta.choices[0].message.content)
