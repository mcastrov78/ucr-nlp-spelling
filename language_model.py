from nltk.tokenize import word_tokenize
from collections import Counter


class LanguageModel:

    UNKNOWN_WORD = '<UNK>'

    def __init__(self):
        # words in the dictionary should be unique, so we can use a set
        self.words_in_dict = set()
        # in a Counter elements are stored as dictionary keys and their counts are stored as dictionary values
        self.valid_words_in_comments = Counter()

        self.total_of_tokens = 0

    def load_dictionary(self):
        with open('diccionarioCompletoEspañolCR.txt', 'r', encoding='UTF-8') as dictionary:
            for line in dictionary:
                # convert to lowercase and remove line breaks
                line = line.lower().rstrip()
                self.words_in_dict.add(line)

        print('Número total de palabras en diccionario: ', len(self.words_in_dict))
        # print('Palabras en diccionario: ', words_in_dict)

    def create_language_model(self):
        total_tokens = 0
        i = 0

        with open('datos_original.txt', 'r', encoding='UTF-8') as comments:
            for line in comments:
                # remove first character and convert to lowercase
                line = line[1:].lower()

                # language model will only contain words in comments that are part of the dictionary
                self.total_of_tokens = 0;
                for word in word_tokenize(line):
                    self.total_of_tokens += 1
                    # if word is not in dictionary it adds to <UNK> count
                    if word in self.words_in_dict:
                        self.valid_words_in_comments.update([word])
                    else:
                        self.valid_words_in_comments.update([self.UNKNOWN_WORD])

                i += 1
                if (i % 10000) == 0:
                    print(i)
                if i >= 10000:
                    break

        print('Ultima línea: ', i)
        print('Número total de tokens en el corpus: ', self.total_of_tokens)
        print('Número total de palabras verificadas en diccionario: ', len(self.valid_words_in_comments) - 1)
        # print("Palabras en comentarios: ", words_in_comments)

        return self.valid_words_in_comments
