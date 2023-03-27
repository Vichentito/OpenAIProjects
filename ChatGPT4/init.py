import openai
import time
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import threading
import uuid


response_start = None
response_end = "1.0"
conversation_history = []
previous_chunks = []
session = str(uuid.uuid4())


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def update_text(chunks):
    global response_start, response_end
    response_text.config(state=tk.NORMAL)
    try:
        response_text.delete(response_start, response_end)
        for chunk in chunks:
            response_text.insert(response_start, chunk)
            response_start = response_text.index(tk.END)
        response_end = response_text.index(tk.END)
        response_text.see(tk.END)
    finally:
        response_text.config(state=tk.DISABLED)


def get_response(user_input):
    global response_start, response_end, previous_chunks
    conversation_history.append({'role': 'user', 'content': user_input})

    # response = openai.ChatCompletion.create(
    #     model='gpt-4',
    #     messages=conversation_history,
    #     temperature=0.9,
    #     max_tokens=4000,
    #     stream=True
    # )
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=conversation_history,
        temperature=0.9,
        max_tokens=4000,
        user=session
    )
    # print(responseNS['choices'][0]['message']['content'])
    # print(response)
    chunks = ["GPT-4:"]
    # Not steaming
    content = response['choices'][0]['message']['content']
    content_utf8 = content.encode('utf-8', 'replace').decode('utf-8')
    chunks.append(content_utf8)
    response_text.after(0, update_text, chunks)
    previous_chunks.extend(chunks)
    # Streaming
    # for idx, chunk in enumerate(response):
    #     delta = chunk['choices'][0]['delta']
    #     if 'content' in delta:
    #         content = delta['content']
    #         content_utf8 = content.encode('utf-8', 'replace').decode('utf-8')
    #         if content_utf8 not in previous_chunks:
    #             chunks.append(content_utf8)
    #             previous_chunks.extend(chunks)
    #             response_text.after(0, update_text, chunks)
    #             # print("".join(chunks))
    #             time.sleep(0.1)
    #             chunks.clear()

    # Agrega esta línea al final de la función get_response
    conversation_history.append(
        {'role': 'assistant', 'content': "".join(previous_chunks)})
    save_file(f'convs/conversation_history_{session}.txt', str(
        conversation_history))
    # print(conversation_history)


def center_window(root):
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def update_widget_width(widget, root):
    width = root.winfo_width()
    # Estima el ancho en caracteres, puedes ajustar el divisor según la fuente que estés usando
    char_width = int(width // 9)
    widget.configure(width=char_width)


def create_gui():
    global user_entry, response_text

    def on_enter_key(event):
        if event.state & 0x1 and event.keysym == 'Return':  # Shift + Enter
            user_entry.insert(tk.INSERT, '\n')
        elif event.keysym == 'Return':  # Enter
            submit_text()

    def submit_text():
        global response_start, response_end

        user_input = user_entry.get('1.0', tk.END).strip()
        user_entry.delete('1.0', tk.END)
        if user_input:
            response_text.config(state=tk.NORMAL)
            response_text.insert(tk.END, f"\nUsuario: {user_input}\n")
            response_start = response_text.index(tk.END)
            response_text.config(state=tk.DISABLED)

            threading.Thread(target=get_response, args=(user_input,)).start()

    root = tk.Tk()
    root.title("ChatGPT")
    root.geometry("700x580")

    frame = ttk.Frame(root, padding="10 10 10 10")
    frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    response_text = scrolledtext.ScrolledText(
        frame, wrap=tk.WORD, height=23, state=tk.DISABLED, font=("Arial", 11))
    response_text.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    user_entry = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=5)
    user_entry.grid(column=0, row=1, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Captura eventos de teclado en user_entry
    user_entry.bind('<KeyRelease>', on_enter_key)

    submit_button = ttk.Button(
        frame, text="Enviar", command=submit_text)
    submit_button.grid(column=0, row=2, sticky=tk.E)

    center_window(root)
    root.update()
    update_widget_width(user_entry, root)
    update_widget_width(response_text, root)

    root.mainloop()


def main():
    openai.api_key = open_file('openaikey.txt')
    create_gui()


if __name__ == "__main__":
    main()
