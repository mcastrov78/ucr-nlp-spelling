from nltk.tokenize import word_tokenize
from collections import Counter
import sqlite3
import argparse

UNKNOWN_WORD = '<UNK>'

# arguments handling and help
parser = argparse.ArgumentParser()
parser.add_argument('--create', help='build or re-build the Language Model at the DB level',
                    action='store_true')
parser.add_argument("word", help="word to spell check")
args = parser.parse_args()

# DB will be used to avoid loading all data every time
connection = sqlite3.connect('language_model.db')
cursor = connection.cursor()

# counter for the total of tokens processed from the corpus
total_tokens_in_corpus = 0
# words in the dictionary should be unique, so we can use a set
words_in_dict = set()
# in a Counter elements are stored as dictionary keys and their counts are stored as dictionary values
words_in_comments = Counter()


def init_db():
    cursor.execute('CREATE TABLE IF NOT EXISTS '
                   'language_model(word TEXT PRIMARY KEY, frequency INTEGER, probability REAL, updated_at DATETIME)')
    connection.commit()


def drop_db():
    cursor.execute('DROP TABLE IF EXISTS language_model')
    connection.commit()


def close_db():
    cursor.close()
    connection.close()


def persist_counter(total_tokens):
    for element in words_in_comments.items():
        #print(element)
        probability = element[1] / total_tokens
        cursor.execute('INSERT INTO language_model(word, frequency, probability, updated_at) '
                       'VALUES(?, ?, ?, datetime("now", "localtime"))', (element[0], element[1], probability))
    connection.commit()


def get_language_model_size():
    size = 0

    cursor.execute('SELECT SUM(frequency) FROM language_model')
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


def get_word_probability(word):
    frequency = 0

    cursor.execute('SELECT probability FROM language_model WHERE word = ?', [word])
    result = cursor.fetchone()
    if result:
        frequency = result[0]

    return frequency


def load_dictionary():
    with open('diccionarioCompletoEspañolCR.txt', 'r', encoding='UTF-8') as dictionary:
        for line in dictionary:
            # convert to lowercase and remove line breaks
            line = line.lower().rstrip()
            words_in_dict.add(line)

    print('Número total de palabras en diccionario: ', len(words_in_dict))
    # print('Palabras en diccionario: ', words_in_dict)


def create_language_model():
    total_tokens = 0
    i = 0

    with open('datos_original.txt', 'r', encoding='UTF-8') as comments:
        for line in comments:
            # remove first character and convert to lowercase
            line = line[1:].lower()

            # language model will only contain words in comments that are part of the dictionary
            for word in word_tokenize(line):
                total_tokens += 1
                # if word is not in dictionary it adds to <UNK> count
                if word in words_in_dict:
                    words_in_comments.update([word])
                else:
                    words_in_comments.update([UNKNOWN_WORD])

            i += 1
            if (i % 10000) == 0:
                print(i)
            #if i >= 10000:
            #    break

    print('Ultima línea: ', i)
    print('Número total de tokens en el corpus: ', total_tokens)
    print('Número total de palabras verificadas en diccionario: ', len(words_in_comments) - 1)
    #print("Palabras en comentarios: ", words_in_comments)

    return total_tokens


# build or re-build the DB and Language Model, if required
if args.create:
    print('Building DB and Language Model ...')

    # init DB
    drop_db()
    init_db()

    # load dictionary and load de language model
    load_dictionary()
    total_tokens_in_corpus = create_language_model()

    # persist the Language Model
    persist_counter(total_tokens_in_corpus)

chosen_word = args.word.lower()
chosen_word_frequency = get_word_frequency(chosen_word)

if chosen_word_frequency == 0:
    chosen_word_frequency = get_word_frequency(UNKNOWN_WORD)
    chosen_word_probability = get_word_probability(UNKNOWN_WORD)
else:
    chosen_word_probability = get_word_probability(chosen_word)

total_words_in_language_model = get_language_model_size()

close_db()

print('Palabra: ', chosen_word)
#print('Modelo de Lenguaje - Tamaño: ', total_words_in_language_model)
print('Modelo de Lenguaje - Frecuencia de la palabra: ', chosen_word_frequency)
print('Modelo de Lenguaje - Probabilidad de la palabra: ', chosen_word_probability)





letters = 'abcdefghijklmnopqrstuvwxyz'
delete_matrix = [[0 for i in range(len(letters))] for j in range(len(letters))]
transpose_matrix = [[0 for i in range(len(letters))] for j in range(len(letters))]
substitution_matrix = [[0 for i in range(len(letters))] for j in range(len(letters))]
insert_matrix = [[0 for i in range(len(letters))] for j in range(len(letters))]

def get_splits(word):
    splits = []

    for i in range(len(word) + 1):
        splits.append((word[:i], word[i:]))
    #print('Splits ({}): {}'.format(len(splits), splits))

    return splits

def get_delete_candidates_info(splits):
    deletes = []

    for left, right in splits:
        if right:
            if len(left) > 0:
                word_with_delete = left + right[1:]
                x = left[-1:]
                y = right[0]
                #print(x, y)

                deletes.append(word_with_delete)

                # ignore vowels with accents and other characters not in 'letters'
                if letters.find(x) >= 0 and letters.find(y) >= 0:
                    delete_matrix[letters.find(x)][letters.find(y)] += 1

    #print('Deletes ({}): {}'.format(len(deletes), deletes))
    #print('delete_matrix:', delete_matrix)

    return deletes


def get_transpose_candidates_info(splits):
    transposes = []

    for left, right in splits:
        if len(right) > 1:
            word_with_transpose = left + right[1] + right[0] + right[2:]
            x = right[0]
            y = right[1]
            #print(x, y)

            transposes.append(word_with_transpose)

            # ignore vowels with accents and other characters not in 'letters'
            if letters.find(x) >= 0 and letters.find(y) >= 0:
                transpose_matrix[letters.index(x)][letters.index(y)] += 1

    #print('Transposes ({}): {}'.format(len(transposes), transposes))
    #print('transpose_matrix:', delete_matrix)

    return transposes


def get_substitution_candidates_info(splits):
    substitutions = []

    for left, right in splits:
        if right:
            for char in letters:
                word_with_substitution = left + char + right[1:]
                x = char
                y = right[0]
                #print(x, y)

                substitutions.append(word_with_substitution)

                # ignore vowels with accents and other characters not in 'letters'
                if letters.find(x) >= 0 and letters.find(y) >= 0:
                    substitution_matrix[letters.index(x)][letters.index(y)] += 1

    #print('Substitutions ({}): {}'.format(len(substitutions), substitutions))
    #print('substitution_matrix:', substitution_matrix)

    return substitutions


def get_insert_candidates_info(splits):
    inserts = []

    for left, right in splits:
        for char in letters:
            if left:
                word_with_insert = left + char + right
                x = left[-1:]
                y = char
                #print(x, y)

                inserts.append(word_with_insert)

                # ignore vowels with accents and other characters not in 'letters'
                if letters.find(x) >= 0 and letters.find(y) >= 0:
                    insert_matrix[letters.index(x)][letters.index(y)] += 1

    #print('Inserts ({}): {}'.format(len(inserts), inserts))
    #print('insert_matrix:', insert_matrix)

    return inserts


'''
word = 'casa'
word_splits = get_splits(word)
word_error_candidates = get_delete_candidates_info(word_splits) + get_transpose_candidates_info(word_splits) + \
                        get_substitution_candidates_info(word_splits) + get_insert_candidates_info(word_splits)

print('Word "{}" error candidates({}): {}'.format(word, len(word_error_candidates), word_error_candidates))
'''

load_dictionary()
print(len(words_in_dict))

with open('spelling_error_candidates.txt', 'w') as spelling_error_candidates:
    i = 0
    for word_in_dict in words_in_dict:
        word_splits = get_splits(word_in_dict)

        word_error_candidates = get_delete_candidates_info(word_splits) + get_transpose_candidates_info(word_splits) + \
                                get_substitution_candidates_info(word_splits) + get_insert_candidates_info(word_splits)

        spelling_error_candidates.writelines('{}: {}\n'.format(word_in_dict, word_error_candidates))

        print(i);
        i += 1;
        #if i > 10:
        #    break;

with open('delete_matrix.txt', 'w') as delete_matrix_file:
    for row in delete_matrix:
        delete_matrix_file.write('{}\n'.format(row))

with open('transpose_matrix.txt', 'w') as transpose_matrix_file:
    for row in transpose_matrix:
        transpose_matrix_file.write('{}\n'.format(row))

with open('substitution_matrix.txt', 'w') as substitution_matrix_file:
    for row in substitution_matrix:
        substitution_matrix_file.write('{}\n'.format(row))

with open('insert_matrix.txt', 'w') as insert_matrix_file:
    for row in insert_matrix:
        insert_matrix_file.write('{}\n'.format(row))
