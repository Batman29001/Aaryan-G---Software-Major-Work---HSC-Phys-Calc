import openai

openai.api_key = "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"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Say hi."}
    ]
)

print(response.choices[0].message.content)