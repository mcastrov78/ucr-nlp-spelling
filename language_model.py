from nltk.tokenize import word_tokenize
from collections import Counter


class LanguageModel:

    UNKNOWN_WORD = '<UNK>'
    FILE_ENCODING = 'UTF-8'

    def __init__(self):
        self.total_of_tokens = 0

    # load dictionary from file
    def load_dictionary(self, dictionary_filename):
        # words in the dictionary should be unique, so we can use a set
        words_in_dict = set()

        with open(dictionary_filename, 'r', encoding=self.FILE_ENCODING) as dictionary:
            for line in dictionary:
                # convert to lowercase and remove line breaks
                line = line.lower().rstrip()
                words_in_dict.add(line)

        print('Número total de palabras en diccionario: ', len(words_in_dict))
        # print('Palabras en diccionario: ', words_in_dict)

        return words_in_dict

    # create language model from corpus file and against dictionary
    def create_language_model(self, corpus_filename, dictionary):
        # in a Counter elements are stored as dictionary keys and their counts are stored as dictionary values
        valid_words_in_comments = Counter()
        i = 0

        with open(corpus_filename, 'r', encoding=self.FILE_ENCODING) as comments:
            for line in comments:
                # remove first character and convert to lowercase
                line = line[1:].lower()

                # language model will only contain words in comments that are part of the dictionary
                self.total_of_tokens = 0
                for word in word_tokenize(line):
                    self.total_of_tokens += 1
                    # if word is not in dictionary it adds to <UNK> count
                    if word in dictionary:
                        valid_words_in_comments.update([word])
                    else:
                        valid_words_in_comments.update([self.UNKNOWN_WORD])

                i += 1
                if (i % 10000) == 0:
                    print(i)
                #if i >= 10000:
                #    break

        print('Ultima línea: ', i)
        print('Número total de tokens en el corpus: ', self.total_of_tokens)
        print('Número total de palabras verificadas en diccionario: ', len(valid_words_in_comments) - 1)
        # print("Palabras en comentarios: ", words_in_comments)

        return valid_words_in_comments
