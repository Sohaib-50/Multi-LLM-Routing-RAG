from openai import OpenAI
client = OpenAI(api_key='sk-1234', base_url='http://localhost:4000')
response = client.chat.completions.create(
    # model="zephyr-beta",
    model='gpt-4-omni',
    messages=[
        {"role": "user", "content": "What is the capital of Canada?"},
    ],
)
print(response)