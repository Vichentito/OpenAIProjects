import os
import tiktoken
import openai
import re
from time import sleep

history = [
    {"role": "system",
     "content": "Eres una IA experta en programación"},
]


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def contar_tokens(texto, encoding_name):
    # print(f"Contando tokens para {encoding_name}")
    # print(f"Texto: {texto}")
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(texto))
    return num_tokens


def listar_archivos_y_carpetas(ruta):
    output = ''
    for directorio_raiz, directorios, archivos in os.walk(ruta):
        # Ignora la carpeta .git
        if '.git' in directorios:
            directorios.remove('.git')

        nivel = directorio_raiz.count(os.path.sep)
        indentacion = ' ' * 2 * nivel

        archivos_str = ', '.join(archivos)
        for carpeta in directorios:
            carpeta_ruta = os.path.join(directorio_raiz, carpeta)
            carpeta_archivos = [f for f in os.listdir(
                carpeta_ruta) if os.path.isfile(os.path.join(carpeta_ruta, f))]
            archivos_str_carpeta = ', '.join(carpeta_archivos)
            output += f"{indentacion}{carpeta}({archivos_str_carpeta})\n"
            # print(f"{indentacion}{carpeta}({archivos_str_carpeta})")

        if archivos:
            output += f"{indentacion}{archivos_str}\n"
            # print(f"{indentacion}{archivos_str}")
    return output


openai.api_key = open_file('openaikey.txt')


def gpt_completion(history, model='gpt-3.5-turbo', temp=0.6, top_p=1.0, tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
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


if __name__ == "__main__":
    ruta = "D:/Repositorios/OpenAIProjects"
    out = listar_archivos_y_carpetas(ruta)
    num_tokens = contar_tokens(out, 'gpt-4')
    history.append(
        {"role": "user", "content": f"De la siguiente lista de archivos y carpetas, que carpeta/archivo me serviria mas si deseo transcribir un audio?\n{out}"},
    )
    result = gpt_completion(history)
    print(result)
