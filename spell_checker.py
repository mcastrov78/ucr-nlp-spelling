from nltk.tokenize import word_tokenize
from collections import Counter
import sqlite3
import argparse

# arguments handling and help
parser = argparse.ArgumentParser()
parser.add_argument('--create', help='build or re-build the Language Model at the DB level',
                    action='store_true')
parser.add_argument("word", help="word to spell check")
args = parser.parse_args()

# DB will be used to avoid loading all data every time
connection = sqlite3.connect('language_model.db')
cursor = connection.cursor()

# words in the dictionary should be unique, so we can use a set
words_in_dict = set()
# in a Counter elements are stored as dictionary keys and their counts are stored as dictionary values
words_in_comments = Counter()


def init_db():
    cursor.execute('CREATE TABLE IF NOT EXISTS '
                   'language_model(word TEXT PRIMARY KEY, frequency INTEGER, updated_at DATETIME)')
    connection.commit()


def drop_db():
    cursor.execute('DROP TABLE IF EXISTS language_model')
    connection.commit()


def close_db():
    cursor.close()
    connection.close()


def persist_counter():
    for element in words_in_comments.items():
        #print(element)
        cursor.execute('INSERT INTO language_model(word, frequency, updated_at) '
                       'VALUES(?, ?, datetime("now", "localtime"))', element)
    connection.commit()


def get_language_model_size():
    size = 0

    cursor.execute('SELECT COUNT(*) FROM language_model')
    result = cursor.fetchone()
    if result:
        size = result[0]

    return size


def get_word_frequency(word):
    frequency = 0

    cursor.execute('SELECT frequency FROM language_model WHERE word = ?', [word])
    result = cursor.fetchone()
    if result:
        frequency = result[0]

    return frequency


def load_dictionary():
    with open('diccionarioCompletoEspañolCR.txt', 'r', encoding='Latin-1') as dictionary:
        for line in dictionary:
            # convert to lowercase and remove line breaks
            line = line.lower().rstrip()
            words_in_dict.add(line)

    print('Número de palabras en diccionario: ', len(words_in_dict))
    # print('Palabras en diccionario: ', words_in_dict)


def create_language_model():
    i = 0

    with open('datos_original.txt', 'r', encoding='UTF-8') as comments:
        for line in comments:
            # remove first character and convert to lowercase
            line = line[1:].lower()

            # language model will only contain words in comments that are part of the dictionary
            for word in word_tokenize(line):
                if word in words_in_dict:
                    words_in_comments.update([word])

            i += 1
            if (i % 10000) == 0:
                print(i)
            #if i >= 10000:
            #    break

    print("Ultima línea: ", i)
    print("Número de palabras en comentarios: ", len(words_in_comments))
    #print("Palabras en comentarios: ", words_in_comments)


# build or re-build the DB and Language Model, if required
if args.create:
    print('Building DB and Language Model ...')

    # init DB
    drop_db()
    init_db()

    # load dictionary and load de language model
    load_dictionary()
    create_language_model()

    # persist the Language Model
    persist_counter()

chosen_word = args.word.lower()
chosen_word_frequency = get_word_frequency(chosen_word)
total_words_in_language_model = get_language_model_size()
chosen_word_probability = chosen_word_frequency / total_words_in_language_model

close_db()

print('Palabra: ', chosen_word)
print('Modelo de Lenguaje - Tamaño: ', total_words_in_language_model)
print('Modelo de Lenguaje - Frecuencia de la palabra: ', chosen_word_frequency)
print('Modelo de Lenguaje - Probabilidad de la palabra: ', chosen_word_probability)
