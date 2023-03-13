import pypandoc
import os
from time import sleep
import PyPDF2
from PIL import Image
import pytesseract
from pdf2image import convert_from_path


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def convert_docx2txt(src_dir, dest_dir):
    files = os.listdir(src_dir)
    files = [i for i in files if '.docx' in i]
    for file in files:
        try:
            pypandoc.convert_file(
                src_dir+file, 'plain', outputfile=dest_dir+file.replace('.docx', '.txt'))
        except Exception as oops:
            print(oops, file)


def convert_pdf2txt(src_dir, dest_dir):
    files = os.listdir(src_dir)
    files = [i for i in files if '.pdf' in i]
    for file in files:
        try:
            reader = PyPDF2.PdfReader(src_dir+file)
            pages = len(reader.pages)
            output = ''
            for page in range(pages):
                print("Reading page ", page+1, " of ",
                      pages, " ", ((page+1)*100)/pages, "%")
                output += reader.pages[page].extract_text()
                output += '\n'
            save_file(dest_dir+file.replace('.pdf', '.txt'),
                      output.strip())
        except Exception as oops:
            print(oops, file)


def convert_pdf2txtTesseract(src_dir, dest_dir):
    files = os.listdir(src_dir)
    files = [i for i in files if '.pdf' in i]
    for file in files:
        try:
            images = convert_from_path(pdf_path=src_dir+file)
            for count, img in enumerate(images):
                img_name = f"page_{count}.png"
                if not os.path.exists(f"OCRIM/{file}"):
                    os.makedirs(f"OCRIM/{file}")
                img.save(f"OCRIM/{file}/"+img_name, "png")
            sleep(2)
            # Extract Text
            png_files = [f for f in os.listdir(f"OCRIM/{file}") if '.png' in f]
            output = ''
            for png_file in png_files:
                print("Total pages: ", len(png_files),
                      " Reading page: ", png_files.index(png_file)+1)
                output += pytesseract.image_to_string(
                    Image.open(f"OCRIM/{file}/"+png_file))
                output += '\n NEW PAGE \n'
            save_file(dest_dir+file.replace('.pdf', '.txt'),
                      output.strip())
        except Exception as oops:
            print(oops, file)


if __name__ == '__main__':
    # convert_docx2txt('docs/', 'converted/')
    #convert_pdf2txt('PDFS/', 'converted/')
    convert_pdf2txtTesseract('PDFS/', 'converted/')
