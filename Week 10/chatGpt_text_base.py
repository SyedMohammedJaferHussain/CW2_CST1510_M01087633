from openai import OpenAI
client = OpenAI(api_key='your-api-keys'
prompt = "What is the best AI related job available right now?"

completion = client.chat.completions.create(
  model="gpt-5.1",
  messages=[
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt}
  ]
)

print(completion.choices[0].message.content)

#print(completion)

