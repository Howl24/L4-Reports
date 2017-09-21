from nltk.corpus import stopwords
from supportClust.supportClust import ProcessedText
import pandas as pd
import string
import ast

notValidString = string.punctuation + '123456789()•?¿{}[]'

stop_spanish = stopwords.words(
    'spanish') + ['etc', 'perú', 'según', 'cargo', 'pucp', 'btpucp', 'practicante', 'área']

stop_english = stopwords.words(
    'english') + ['Excel', 'excel', 'Word', 'word', 'point', 'Point', 'Power', 'power', 'mro']

stopWords = stop_spanish + list(set(stop_spanish) - set(stop_english))


def _get_basic_list(list_features):
    lista_dict = []
    i = 0
    list_delet_values = []
    for x in list_features:
        try:
            #json_data = ast.literal_eval(x.specialWords)
            #x.specialWords = json_data
            x.specialWords = dict(x.specialWords)
            lista_dict.append(x.specialWords)
        except SyntaxError:
            list_delet_values.append(i)
            i += 1
            continue
        i += 1
    for x in list_delet_values:
        del list_features[x]
    return lista_dict


def _get_list_import_stuffs(lista_dict, list_features):
    list_impt_stuffs = []
    i = 0
    for x in lista_dict:
        value = x["Description"].split() + x["Job Title"].split()
        list_impt_stuffs.append(value)
        list_features[i].specialWords = value
        i += 1
    return list_impt_stuffs, list_features


def _readCSV(nameOfFile='datalog.csv'):
    data = pd.read_csv(nameOfFile, error_bad_lines=False)
    list_features = []
    for x, y in list(zip(data["features"], data["id"])):
        list_features.append(ProcessedText(id_=y, specialWords=x))
    return list_features


def _get_carrers(lista_dict):
    # Get the unique of all the announcement
    carrers = []
    for x in lista_dict:
        carrersXOffer = x['Majors/Concentrations'].split(",")
        for y in carrersXOffer:
            word = y.strip()
            if word not in carrers:
                carrers.append(word)
    return carrers


def _get_carrers_for_dic(lista_dict):
    # Get the carrers for announcement
    carrers = []
    for x in lista_dict:
        carrersXOffer = x['Majors/Concentrations'].split(",")
        carrersXOffer = [i.strip() for i in carrersXOffer]
        carrers.append(carrersXOffer)
    return carrers


def is_decimal(number):
    try:
        float(number)
        return True
    except ValueError:
        pass
    return False


def have_a_number(stri):
    if stri.isdigit():
        return True
    if is_decimal(stri):
        return True
    for x in stri:
        if x.isdigit():
            return True
    return False


def have_trash_words(stri):
    for x in stri:
        if x in notValidString:
            return True
    return False


def clean_text(list_impt_stuffs):
    clean_list = []
    for words in list_impt_stuffs:
        new_list = []
        for x in words:
            x = x.lower()
            x = x.strip(notValidString)  # Clean the start and the end
            if len(x) <= 2:
                continue
            if x in stopWords:
                continue
            if have_a_number(x):
                continue
            if have_trash_words(x):
                continue
            new_list.append(x)
        if (len(new_list) > 0):
            clean_list.append(new_list)
    return clean_list

# http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/


def find_ngrams(input_list, n):
    return list(zip(*[input_list[i:] for i in range(n)]))
