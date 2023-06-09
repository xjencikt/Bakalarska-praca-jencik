import re
import bs4

import os

from bs4 import BeautifulSoup
from bs4.element import Comment


def remove_span(dir):
    xhtml = open(dir,
                 encoding="utf8").read()

    soup2 = bs4.BeautifulSoup(xhtml, 'html.parser')

    for match in soup2.findAll('span'):
        match.unwrap()

    with open(dir,
              "w", encoding="utf8") as outf:
        outf.write(str(soup2))


def remove_div(dir):
    xhtml = open(dir, encoding="utf8").read()
    soup = bs4.BeautifulSoup(xhtml, 'html.parser')

    for div_tag in soup.findAll('div'):
        br_tag = soup.new_string(" ")
        div_tag.insert_before(br_tag)
        div_tag.unwrap()

    with open(dir, "w", encoding="utf8") as outf:
        outf.write(str(soup))


def remove_img(dir):
    xhtml = open(dir,
                 encoding="utf8").read()

    soup2 = bs4.BeautifulSoup(xhtml, 'html.parser')

    for match in soup2.findAll('img'):
        match.unwrap()

    with open(dir,
              "w", encoding="utf8") as outf:
        outf.write(str(soup2))


def remove_non_ascii(text):
    exceptions = ['á', 'ä', 'č', 'ď', 'é', 'í', 'ĺ', 'ľ', 'ň', 'ó', 'ô', 'ŕ', 'š', 'ť', 'ú', 'ý', 'ž',
                  'Á', 'Ä', 'Č', 'Ď', 'É', 'Í', 'Ĺ', 'Ľ', 'Ň', 'Ó', 'Ô', 'Ŕ', 'Š', 'Ť', 'Ú', 'Ý', 'Ž']

    cleaned_text = ''.join([char if char.isascii() or char in exceptions else ' ' for char in text])
    return cleaned_text


def highlight_one_libreOffice(file_path, dictionary, new_dir):
    with open(file_path, encoding="utf8") as file_html:
        highlight = file_html.read()

        remove_non_ascii(highlight)

        base_name = os.path.basename(file_path)
        base_name_without_extension = os.path.splitext(base_name)[0]

        soup = bs4.BeautifulSoup(highlight, 'html.parser')

        color_index = 0  # Initialize the color index
        for key, value in dictionary.items():
            word, color = value  # Extract word and color from dictionary value
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            highlight_color = color

            results = soup.body.find_all(string=pattern, recursive=True)

            for result in results:
                print("Found '" + result + "' with key '" + key + "' in the XHTML.")
                newtag = soup.new_tag('span', style="background-color: {};".format(highlight_color))
                result.wrap(newtag)

            color_index = (color_index + 1) % len(dictionary)

        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

        new_file_path = os.path.join(new_dir, base_name_without_extension + ".xhtml")

        with open(new_file_path, "w", encoding="utf8") as outf:
            outf.write(str(soup))


def highlight_one_pdf2htmlEX(file_path, dictionary, new_dir):
    new_path = create_test_doc(file_path)
    remove_span(new_path)
    remove_div(new_path)
    remove_img(new_path)

    with open(new_path, 'r', encoding='utf-8') as file:
        html = file.read()

    soup = BeautifulSoup(html, 'html.parser')

    merged_html = str(soup)

    cleaned_merged_html = remove_non_ascii(merged_html)

    cleaned_merged_html = cleaned_merged_html.replace('  ', ' ')

    with open(new_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_merged_html)

    print("Merging of div elements completed.")
    color_index = 0
    for key, value in dictionary.items():
        word, color = value  # Extract word and color from dictionary value
        if word.lower() in cleaned_merged_html.lower():
            cleaned_merged_html = cleaned_merged_html.lower().replace(
                word.lower(), f'<span style="background-color: {color};">{word}</span>'
            )
            print(f"Found '{word}' from dictionary with key '{key}' in the HTML.")

            color_index = (color_index + 1) % len(dictionary)

    cleaned_merged_html = cleaned_merged_html.replace(' <?xml version="1.0" encoding="utf-8"?>',
                                                      '<?xml version="1.0" encoding="utf-8"?>')

    soup = BeautifulSoup(cleaned_merged_html, 'html.parser')

    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    new_file_path = os.path.join(new_dir, os.path.basename(file_path))

    with open(new_file_path, "w", encoding="utf8") as outf:
        outf.write(str(soup))


def identify_generator(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        print(file)
        soup = BeautifulSoup(file, 'lxml')
        libreoffice = soup.find(
            text=lambda text: isinstance(text, Comment) and 'This file was converted to xhtml by LibreOffice' in text)
        if libreoffice:  # viem
            return 'LibreOffice'
        openoffice = soup.find(text=lambda text: isinstance(text,
                                                            Comment) and 'This file was converted to xhtml by OpenOffice.org' in text)
        if openoffice:  # viem
            return 'OpenOffice'
        xmlmind = soup.find('meta', {'name': 'generator'})
        if xmlmind and 'XMLmind Word To XML' in xmlmind['content']:  # viem
            return 'XMLmind'
        msword = soup.find('meta', {'name': 'Generator'})
        if msword and 'Microsoft Word' in msword['content']:
            return 'MSWord'
        integix = soup.find(text=lambda text: isinstance(text, Comment) and 'INTEGIX by' in text)
        if integix:  # viem
            return 'INTEGIXbyEz-XBRL'
        # if pdf_iris_unknown:
        #     return 'pdf2htmlEX'
        # if IrisBusinessService:
        #     return 'IrisBusinessService'
        return 'Unknown'


def highlightDir(dir, dictionary, new_dir):
    for filename in os.listdir(dir):
        if not filename.endswith(".xhtml"):
            continue
        with open(os.path.join(dir, filename), encoding="utf8"):
            identifier = identify_generator(os.path.join(dir, filename))
            print(identifier)
            if identifier == 'LibreOffice' or \
                    identifier == 'OpenOffice' or \
                    identifier == 'XMLmind' or \
                    identifier == 'MSWord' or \
                    identifier == 'INTEGIXbyEz-XBRL':
                highlight_one_libreOffice(os.path.join(dir, filename), dictionary, new_dir)
            else:
                highlight_one_pdf2htmlEX(os.path.join(dir, filename), dictionary, new_dir)


def create_test_doc(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html = file.read()

    soup = BeautifulSoup(html, 'html.parser')

    base_name = os.path.basename(file_path)
    base_name_without_extension = os.path.splitext(base_name)[0]

    new_dir = os.path.join(os.path.dirname(file_path), "highlighted")
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    new_file_path = os.path.join(new_dir, base_name_without_extension + ".xhtml")
    with open(new_file_path, "w", encoding="utf8") as outf:
        outf.write(str(soup))

    return new_file_path


def main():
    dir = "ROCNE SPRAVY  2021/test/"
    new_path = "ROCNE SPRAVY  2021/test/highlighted/"
    dictionary = {
        "word1": ("Telefónne číslo:", "red"),
        "word2": ("Webové sídlo, kde sa nachádzajú regulované informácie", "lightblue"),
        "word3": ("náklady na činnosť v oblasti výskumu a vývoja", "green"),
        "word4": ("Ruská invázia na Ukrajinu sa začala", "yellow"),
        "word5": ("Production processes is performed", "orange"),
        "word6": ("yplývajúcom z platného znenia Obchodného zákonníka", "purple"),
        "word7": ("Ročná finančná správa za rok 2021", "red"),
        "word8": ("Informácie o činnosti valného zhromaždenia", "lightblue"),
        "word9": ("Účtovná závierka", "green"),
        "word10": ("Statement of Financial Position", "yellow")
    }




    highlightDir(dir, dictionary, new_path)


if __name__ == '__main__':
    main()
