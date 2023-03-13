import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse


def selection(input_urls=None, selected_indices=None, urls=None):
    with open("urlsInput.txt", "r") as f:
        input_urls = f.read().splitlines()

    for i, url in enumerate(input_urls):
        print(f"{i+1}. {url}")

    selected_indices_str = input(
        "Ingrese los números de las URLs que desea utilizar, separados por comas (o presione Enter para seleccionar todas): ")

    if selected_indices_str.strip() == "":
        selected_indices = None
        urls = input_urls
    else:
        selected_indices = [int(i.strip())
                            for i in selected_indices_str.split(",")]
        urls = [input_urls[i-1] for i in selected_indices]

    return urls


def scrap(urls):
    # Send a request to the URL and get the HTML content
    for url in urls:
        print("Scraping", url.split("?")[0])
        response = requests.get(url)
        html_content = response.content
        getTexts(html_content, urlparse(url).netloc)


def getTexts(html_content, filename):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    # Remove all script and style elements from the soup
    for script in soup(["script", "style"]):
        script.extract()

    # Remove all ads by looking for any elements with "ads" in their class name
    for ad in soup.find_all(class_=re.compile("ads")):
        ad.extract()

    # Extract information from the soup
    information = []

    main_tag = soup.find(name='main')
    if not main_tag:
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'img', 'table']):
            if tag.name == 'img':
                # Extract the URL of the image and add it to the information list
                image_url = tag.get('src')
                if image_url:
                    information.append(('image', image_url))
            elif tag.name in ['h1', 'h2', 'h3']:
                text = tag.get_text().strip()
                if text:
                    information.append(('title', text))
            elif tag.name == 'p':
                if (not tag.parent.has_attr('class') or not any(re.search(r'(nav|menu|form|footer)', class_name) for class_name in tag.parent.get('class'))):
                    # Excluye las etiquetas <p> que contengan enlaces o que estén dentro de elementos con las clases "nav", "menu" o "form"
                    if (not tag.has_attr('class') or not any(re.search(r'(nav|menu|form|footer)', class_name) for class_name in tag['class'])):
                        # Extrae el texto del párrafo, pero excluye los elementos <span>
                        # print(tag.name, tag.get('class'), tag.parent.name,
                        #       tag.parent.has_attr('class'), tag.parent.get('class'))
                        text = tag.get_text().strip()
                        if text:
                            # Agrega el tipo de elemento y su texto a una lista de información
                            information.append(('paragraph', text))
            elif tag.name == 'table':
                # Extract information from the table
                for row in tag.find_all('tr'):
                    row_data = [cell.get_text().strip()
                                for cell in row.find_all('td')]
                    if row_data:
                        information.append(('table_row', row_data))
        # Write the information to a text file
        with open(f'outputs/output_{filename}.txt', 'w', encoding='utf-8') as f:
            for info_type, info_text in information:
                if info_type == 'table_row':
                    f.write(f'{info_type}: {", ".join(info_text)}\n')
                else:
                    f.write(f'{info_type}: {info_text}\n')
    else:
        for tag in main_tag.find_all(['h1', 'h2', 'h3', 'p', 'img', 'table']):
            if tag.name == 'img':
                # Extract the URL of the image and add it to the information list
                image_url = tag.get('src')
                if image_url:
                    information.append(('image', image_url))
            elif tag.name in ['h1', 'h2', 'h3']:
                text = tag.get_text().strip()
                if text:
                    information.append(('title', text))
            elif tag.name == 'p':
                if (not tag.parent.has_attr('class') or not any(re.search(r'(nav|menu|form|footer)', class_name) for class_name in tag.parent.get('class'))):
                    # Excluye las etiquetas <p> que contengan enlaces o que estén dentro de elementos con las clases "nav", "menu" o "form"
                    if (not tag.has_attr('class') or not any(re.search(r'(nav|menu|form|footer)', class_name) for class_name in tag['class'])):
                        # Extrae el texto del párrafo, pero excluye los elementos <span>
                        # print(tag.name, tag.get('class'), tag.parent.name,
                        #       tag.parent.has_attr('class'), tag.parent.get('class'))
                        text = tag.get_text().strip()
                        if text:
                            # Agrega el tipo de elemento y su texto a una lista de información
                            information.append(('paragraph', text))
            elif tag.name == 'table':
                # Extract information from the table
                for row in tag.find_all('tr'):
                    row_data = [cell.get_text().strip()
                                for cell in row.find_all('td')]
                    if row_data:
                        information.append(('table_row', row_data))
        # Write the information to a text file
        with open(f'outputs/output_{filename}.txt', 'w', encoding='utf-8') as f:
            for info_type, info_text in information:
                if info_type == 'table_row':
                    f.write(f'{info_type}: {", ".join(info_text)}\n')
                else:
                    f.write(f'{info_type}: {info_text}\n')


if __name__ == '__main__':
    urls = selection()
    scrap(urls)
