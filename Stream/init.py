import openai
import uuid
import time
import subprocess


conversation_history = []
session = str(uuid.uuid4())


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = open_file('openaikey.txt')

user_input = input("User: ")

conversation_history.append({'role': 'user', 'content': user_input})
response = openai.ChatCompletion.create(
    model='gpt-4',
    messages=conversation_history,
    temperature=0.9,
    max_tokens=4000,
    stream=True
)
chunks = ["GPT-4:"]
chunk_counter = 0
for idx, chunk in enumerate(response):
    delta = chunk['choices'][0]['delta']
    if 'content' in delta:
        content = delta['content']
        content_utf8 = content.encode('utf-8', 'replace').decode('utf-8')
        chunks.append(content_utf8)
        chunk_counter += 1

        if chunk_counter % 20 == 0:
            print("".join(chunks))
        time.sleep(0.1)

subprocess.run("printf '\033c'", shell=True)
#print('\033c', end='')

print("".join(chunks))

# Agrega esta línea al final de la función get_response
conversation_history.append(
    {'role': 'assistant', 'content': "".join(chunks)})
