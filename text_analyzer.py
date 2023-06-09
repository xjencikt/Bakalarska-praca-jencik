import re


import bs4
import pandas as pd
import nltk.data
from bs4 import BeautifulSoup
from bs4.element import Comment
from abc import abstractmethod

from os import listdir
from os.path import isfile, join


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


class text_analyzer:

    def __init__(self):
        self.parent = None

    path = "../../../data/pdfs/ROCNE SPRAVY  2021"

    @abstractmethod
    def tag_visible(self):
        pass

    @abstractmethod
    def text_from_html(self):
        pass

    @abstractmethod
    def separate_string_to_sentences(_str: str):
        tokenizer = nltk.data.load('data/tokenizer/czech.pickle')
        sentences = tokenizer.tokenize(_str)
        return sentences

    @staticmethod
    def get_dummy_text(path: str):
        onlydirs = [f for f in listdir(path) if isfile(join(path, f))]
        data = []
        i = 0
        for files in onlydirs:
            i += 1
            if files.endswith('.xhtml'):
                xhtml = open(path + '/' + files, encoding="utf8").read()
                data.append(text_from_html(xhtml))

        data.append("Počet spracovaných xhtml súborov:" + str(i - 1))
        df = pd.DataFrame(data)
        return df.to_csv('All_text_from_datas.csv', encoding="utf-16")

    @staticmethod
    def get_libre_open_office_header():
        data = []
        xhtml = open('../../../data/pdfs/ROCNE SPRAVY  2021/GEOCOMPLEX_COPY.xhtml', encoding="utf8").read()
        soup = BeautifulSoup(xhtml, 'html.parser')
        headers = soup.find_all(['h{}'.format(i) for i in range(1, 7)])
        with open('open_office_headers.txt', 'w', encoding="utf8") as f:
            for header in headers:
                print(header.get_text().strip())
                data.append(header.get_text().strip())
                f.write(header.get_text().strip())
                f.write("\n")

        if not data:
            return print("EMPTY")
        return data

    @staticmethod
    def get_pdf2html_header():
        data = []
        xhtml = open('../../../data/pdfs/ROCNE SPRAVY  2021/GEOCOMPLEX_COPY.xhtml',
                     encoding="utf8").read()
        soup = BeautifulSoup(xhtml, 'html.parser')
        headers = soup.find_all("div", {"class": "hc"})
        for header in headers:
            print(header.get_text().strip())
            data.append(header.get_text().replace("\n", "").strip)

        if not data:
            return print("EMPTY")
        return data

    @staticmethod
    def write_xhtml(new_file):
        with open(new_file, "w", encoding="utf8") as file_html:
            file_html.write("""<?xml version='1.0' encoding='utf-8' standalone='no'?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>Test page</title>
      </head>
      <body>
        <p>Hello world</p>
      </body>
    </html>""")
        file_html.close()

    @staticmethod
    def append_to_xhtml(open_file, new_file):
        xhtml = open(open_file, encoding="utf8").read()
        soup2 = BeautifulSoup(xhtml, 'html.parser')

        for match in soup2.findAll('span'):
            match.unwrap()

        with open(new_file, "w", encoding="utf8") as outf:
            outf.write(str(soup2))

    @staticmethod
    def get_text(open_file):
        def tag_visible(element):
            if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]',
                                       'xbrli:context', 'ix:references', 'ix:header', 'link:schemaRef',
                                       'xbrli:context', "ix:relationship", "xbrli:measure", "xbrli:unit",
                                       "xbrli:entity", "xbrli:period", "xbrli:scenario", "xbrli:identifier",
                                       "xbrli:segment", "xbrli:explicitMember", "xbrli:typedMember",
                                       "xbrli:balance", "xbrli:startDate", "xbrli:endDate", "xbrli:instant",
                                       "xbrli:forever", "xbrli:periodType", "xbrli:entityIdentifier",
                                       "xbrli:entityScheme"]:
                return False
            if isinstance(element, Comment):
                return False
            return True

        openfile = open(open_file, encoding="utf8").read()
        soup = BeautifulSoup(openfile, 'html.parser')

        data = []
        text = soup.get_text()

        text_without_znbsp = re.sub('﻿', '', text)
        text_without_nbsp = re.sub(' ', '', text_without_znbsp)
        text_without_blank = re.sub('\ {2,}', '', text_without_nbsp)

        # Add a new line after every comma
        text_with_newlines = re.sub(',', ',\n', text_without_blank)

        data.append(text_with_newlines.strip())

        df = pd.DataFrame(data)
        return df.to_csv('data_from_text.csv', encoding="utf-16")

open_file = 'ROCNE SPRAVY  2021/test/highlighted/ACROSS FUNDING správa 2021.xhtml'
new_file = 'ROCNE SPRAVY  2021/test/highlighted/ACROSS FUNDING správa 2021-COPY.xhtml'
searched_word = 'Payment titles'

text_analyzer.get_text(open_file)


