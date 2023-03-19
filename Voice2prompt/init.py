import sounddevice as sd
import numpy as np
import openai
import io
import os
import math
import threading
import tempfile
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pygame.mixer as mixer
import re
from time import sleep


# Configuración de grabación
DURACION = 10 * 60  # 10 minutos en segundos
RATE = 16000  # frecuencia de muestreo
CHANNELS = 1  # mono
FILENAME = 'grabacion.wav'

# Variable global para controlar la grabación
recording = True


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


# Establece tu clave API de OpenAI
openai.api_key = open_file('openaikey.txt')

# Función para detener la grabación cuando se presiona 'Enter'


def stop_recording():
    global recording
    recording = False

# Función para grabar audio


def grabar_audio(stop_event, audio_buffer, rate=44100, chunk_size=1024, channels=1):
    global recording
    recording = True

    with sd.InputStream(samplerate=rate, channels=channels, callback=lambda indata, frames, time, status: audio_buffer.append(indata.copy())):
        while not stop_event.is_set():
            sd.sleep(100)

    audio_data = np.concatenate(audio_buffer, axis=0)
    return audio_data

# Función para dividir el audio en segmentos


def dividir_audio(filename, duracion_segmento):
    from pydub import AudioSegment
    audio = AudioSegment.from_wav(filename)
    duracion_total = len(audio)
    num_segmentos = math.ceil(duracion_total / (duracion_segmento * 1000))

    segmentos = []
    for i in range(num_segmentos):
        inicio = i * duracion_segmento * 1000
        fin = inicio + duracion_segmento * 1000
        segmento = audio[inicio:fin]
        segmentos.append(segmento)

    return segmentos

# Función para convertir audio a texto con la API de Whisper


def speech_to_text(archivo_audio):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_audio_file_path = os.path.join(temp_dir, "temp_audio.wav")
        archivo_audio.export(temp_audio_file_path, format='wav')
        with open(temp_audio_file_path, "rb") as audio_file:
            response = openai.Audio.transcribe("whisper-1", audio_file)
    # print(response)
    if response['text']:
        transcript = response['text']
        completion = gpt3_completion(prompt=transcript)
        combined_text = "Transcripcion: " + transcript + "\nCompletion: " + completion
        with open("output.txt", "w", encoding='utf-8') as output_file:
            output_file.write(combined_text)
        return combined_text
    else:
        print(f'Error en la API de Whisper: {response["status"]}')
        return None


def gpt3_completion(prompt, engine='gpt-4', temp=0.7,
                    top_p=1.0, tokens=3000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.ChatCompletion.create(
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
            # print(text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

# Función para procesar los segmentos de audio y actualizar la interfaz gráfica


def procesar_segmentos(segmentos, text_widget):
    for i, segmento in enumerate(segmentos):
        print(f"Procesando segmento {i + 1} de {len(segmentos)}")
        texto = speech_to_text(segmento)
        if texto:
            text_widget.insert(tk.END, f"Segmento {i + 1}: \n{texto}\n")
        else:
            text_widget.insert(
                tk.END, f"Error al procesar el segmento {i + 1}\n")
        text_widget.see(tk.END)

# Función para manejar el evento de grabación


def on_grabar_button_click(grabar_button, detener_button, text_widget):
    grabar_button.config(state=tk.DISABLED)
    detener_button.config(state=tk.NORMAL)

    global stop_event, audio_buffer, t
    stop_event = threading.Event()
    audio_buffer = []
    t = threading.Thread(target=grabar_audio, args=(stop_event, audio_buffer))
    t.start()

# Función para manejar el evento de detener


def on_detener_button_click(grabar_button, detener_button, text_widget, reproducir_button):
    detener_button.config(state=tk.DISABLED)
    grabar_button.config(state=tk.NORMAL)

    stop_event.set()
    t.join()

    audio_data = np.concatenate(audio_buffer, axis=0)
    write(FILENAME, 44100, audio_data)

    segmentos = dividir_audio(FILENAME, 10 * 60)
    audio_data = np.array(segmentos[0].get_array_of_samples())
    reproducir_button.config(state=tk.NORMAL)

    threading.Thread(target=procesar_segmentos,
                     args=(segmentos, text_widget)).start()


def on_cerrar_ventana(root):
    global recording
    recording = False
    root.destroy()


def on_mouse_scroll(event, canvas):
    if event.delta:
        canvas.yview_scroll(-1 * (event.delta // 120), "units")
    else:
        canvas.yview_scroll(1 if event.num == 5 else -1, "units")

# Función para crear la interfaz gráfica


def crear_interfaz():
    root = tk.Tk()
    root.title("Grabador y transcriptor de audio")
    root.geometry("600x600")
    # Inicializa el mezclador de Pygame para reproducir audio
    mixer.init()

    main_frame = ttk.Frame(root, padding="12 12 12 12")
    main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    grabar_button = ttk.Button(main_frame, text="Grabar", command=lambda: on_grabar_button_click(
        grabar_button, detener_button, text_widget))
    grabar_button.grid(column=0, row=0, padx=(
        0, 5), pady=(0, 5), sticky=(tk.W, tk.E))

    detener_button = ttk.Button(main_frame, text="Detener", command=lambda: on_detener_button_click(
        grabar_button, detener_button, text_widget), state=tk.DISABLED)
    detener_button.grid(column=1, row=0, padx=(
        5, 0), pady=(0, 5), sticky=(tk.W, tk.E))

    reproducir_button = ttk.Button(main_frame, text="Reproducir", state=tk.DISABLED,
                                   command=lambda: mixer.music.load(FILENAME) or mixer.music.play())
    reproducir_button.grid(column=2, row=0, padx=(
        5, 0), pady=(0, 5), sticky=(tk.W, tk.E))

    text_widget = ScrolledText(main_frame, wrap=tk.WORD, width=70, height=30)
    text_widget.grid(column=0, row=1, columnspan=3, padx=(
        0, 0), pady=(5, 0), sticky=(tk.W, tk.E, tk.N, tk.S))

    # Modifica la llamada al evento on_detener_button_click
    detener_button.config(command=lambda: on_detener_button_click(
        grabar_button, detener_button, text_widget, reproducir_button))

    main_frame.rowconfigure(3, weight=1)

    # Vincula la función on_cerrar_ventana al evento de cierre de la ventana
    root.protocol("WM_DELETE_WINDOW", lambda: on_cerrar_ventana(root))

    root.mainloop()


if __name__ == '__main__':
    crear_interfaz()
