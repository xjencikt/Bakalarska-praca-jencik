# Bakalárska-práca - Tomáš Jenčík

ROCNE SPRAVY  2021: testovacia databáza

all_text_info.csv: spracované textové dáta s rozdelenými častami
data_from_text.csv: spracované textové dáta v jednoduchom formáte (text rozdelený po čiarkách)

text_analyzer.py: spracovanie dokumentu a rozdelenie textu podľa čiarok. Vstupný parameter:
- open_file: cesta k danému priečinku.


highlight_all_files.py: vyznačenie vyhľadávaných výrazov v databáze. Vstupné parametre:
- dir = cesta k danému priečinku,
- dictionary = slovník slov s farbami prislúchajúcimi k slovnému výrazu,
- new_path = novo vytvorený dokument s označenými prvkami

xhtml_analysis_beautiful_soup_Libre_Office.ipynb: bližšie spracovanie Libre Office dokumentu
xhtml_analysis_beautiful_soup_Open_Office.ipynb: bližšie spracovanie Open Office dokumentu
xhtml_analysis_beautiful_soup_pdf2htmlEX.ipynb: bližšie spracovanie pdf2htmlEX dokumentu
doc_analysis_utils.ipynb: spracovanie dokumentov a nájdenie ich generátorov

Dokumenty .py je možné spustiť po nainštalovaní potrebných knižníc.
Pre spustenie .ipynb je potrebné mať nainštalované knižnice a potom jednotlivé časti kódu v notebooku spúšťať postupne.