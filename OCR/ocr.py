import os
from time import sleep
from PIL import Image
import pytesseract
import datetime


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def convert_pdf2txtTesseract(src_dir, dest_dir):
    files = os.listdir(src_dir)
    files = [i for i in files if '.png' in i]
    output = ''
    for file in files:
        try:
            # Extract Text
            print("Total imgs: ", len(files),
                  " Reading page: ", files.index(file)+1)
            output += pytesseract.image_to_string(
                Image.open(f"imgs/"+file))
            output += '\n\n'
            sleep(1)
        except Exception as oops:
            print(oops, file)
    # Obtener la fecha y hora actual
    now = datetime.datetime.now()

    # Crear una cadena de texto con la marca de tiempo
    timestamp = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]
    save_file(f'extracted/output_{timestamp}.txt',
              output.strip())


if __name__ == '__main__':
    convert_pdf2txtTesseract('imgs/', 'extracted/')
