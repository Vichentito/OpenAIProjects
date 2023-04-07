import textwrap
import os
from time import time, sleep
import openai
import re


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = open_file('openaikey.txt')
history = [
    {"role": "system",
     "content": "Eres una IA de modelo de lenguaje entrenado para resumir textos en español."},
]


def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


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
        "Seleccione los archivos a imprimir (separados por comas), o presione Enter para imprimir todos: ")

    if seleccion:
        # Si el usuario seleccionó archivos específicos, convertir su selección a una lista
        seleccion = seleccion.split(",")
        seleccion = [int(s.strip()) for s in seleccion]
    else:
        # Si el usuario no seleccionó ningún archivo específico, imprimir todos los archivos
        seleccion = range(len(archivos))

    return [os.path.join(directorio, archivos[i-1]) for i in seleccion]


def summary(history, model='gpt-3.5-turbo', temp=0.6, top_p=1.0, tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            #print('Prompt:', history)
            response = openai.ChatCompletion.create(
                model=model,
                messages=history,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop,
            )
            text = response['choices'][0]['message']['content'].strip()
            text = re.sub('\s+', ' ', text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


if __name__ == '__main__':
    files = selection()
    # print(files)
    for file in files:
        print('\n\nProcessing', file)
        alltext = open_file(file)
        chunks = textwrap.wrap(alltext, 1000)
        result = list()
        count = 0
        for chunk in chunks:
            chunk = chunk.encode(encoding='ASCII', errors='ignore').decode()
            if count == 0:
                history.append(
                    {"role": "user", "content": f"Resume el texto siguiente: {chunk}"},
                )
            else:
                history.append(
                    {"role": "user", "content": f"Continua el resumen con la siguiente informacion: {chunk}"},
                )
            summary_text = summary(history)
            count = count + 1
            print('\n', file, count, 'of', len(chunks))
            result.append(summary_text)
        save_file('\n\n'.join(result), 'summaries/output_%s.txt' % file[6:])
