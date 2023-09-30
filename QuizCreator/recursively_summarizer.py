import textwrap
import os
from time import time, sleep
import openai
import re


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = open_file('openaikey.txt')


def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def gpt3_completion(prompt, engine='text-davinci-003', temp=0.6, top_p=1.0, tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            return text
        except Exception as oops:
            filename = '%s_gpt3.txt' % time()
            with open('gpt3_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt +
                              '\n\n==========\n\nRESPONSE:\n\n' + oops)
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def selection():
    # Obtener la lista de archivos en un directorio
    directorio = "files/"
    archivos = os.listdir(directorio)

    # Mostrar la lista de archivos al usuario
    print("Archivos disponibles en la carpeta:")
    for i, archivo in enumerate(archivos):
        print(f"{i+1}. {archivo}")

    # Preguntar al usuario qué archivos imprimir
    seleccion = input(
        "Seleccione los para generar el examen (separados por comas), o presione Enter para generar de todos: ")

    if seleccion:
        # Si el usuario seleccionó archivos específicos, convertir su selección a una lista
        seleccion = seleccion.split(",")
        seleccion = [int(s.strip()) for s in seleccion]
    else:
        # Si el usuario no seleccionó ningún archivo específico, imprimir todos los archivos
        seleccion = range(len(archivos))

    return [os.path.join(directorio, archivos[i-1]) for i in seleccion]


if __name__ == '__main__':
    files = selection()
    # print(files)
    for file in files:
        print('\n\nProcessing', file)
        alltext = open_file(file)
        chunks = textwrap.wrap(alltext, 4000)
        result = list()
        count = 0
        for chunk in chunks:
            count = count + 1
            prompt = open_file('prompt.txt').replace('<<INFO>>', chunk)
            prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
            summary = gpt3_completion(prompt)
            print('\n', file, count, 'of', len(chunks))
            result.append(summary)
        save_file('\n\n'.join(result), 'quizes/quiz_%s.txt' % file[6:])
