import language_model
import db_support
import ast


class NoisyChannelModel:

    LETTERS = 'abcdefghijklmnopqrstuvwxyzáéíóúüñ'
    SPELLING_ERROR_CANDIDATES_FILE = 'spelling_error_candidates.txt'
    DELETE_MATRIX_FILE = 'delete_matrix.txt'
    TRANSPOSE_MATRIX_FILE = 'transpose_matrix.txt'
    SUBSTITUTION_MATRIX_FILE = 'substitution_matrix.txt'
    INSERT_MATRIX_FILE = 'insert_matrix.txt'

    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.db = db_support.DBSupport()

        letters_range = range(len(self.LETTERS))
        self.delete_matrix = [[0 for i in letters_range] for j in letters_range]
        self.transpose_matrix = [[0 for i in letters_range] for j in letters_range]
        self.substitution_matrix = [[0 for i in letters_range] for j in letters_range]
        self.insert_matrix = [[0 for i in letters_range] for j in letters_range]

    # get all possibilities of splitting the word up in 2 pieces
    def get_splits(self, word):
        splits = []

        for i in range(len(word) + 1):
            splits.append((word[:i], word[i:]))

       # print('Splits ({}): {}'.format(len(splits), splits))

        return splits

    # increase counter for coordinates x, y  in matrix
    def increase_matrix_counter(self, matrix, x, y):
        x_for_letter = self.LETTERS.find(x)
        y_for_letter = self.LETTERS.find(y)
        if x_for_letter >= 0 and y_for_letter >= 0:
            matrix[x_for_letter][y_for_letter] += 1

    # del[X, Y] = Deletion of Y after X
    # Y (Deleted Letter)
    def get_delete_candidates_info(self, splits, real_words=False, populate_matrix=True):
        deletes_non_word_candidates = []
        deletes_word_candidates = dict()

        for left, right in splits:
            if right:
                if len(left) > 0:
                    # generate error candidate
                    word_with_delete = left + right[1:]
                    x_value = left[-1:]
                    y_value = right[0]

                    if not real_words:
                        # only interested in non word candidates
                        if word_with_delete not in self.dictionary:
                            deletes_non_word_candidates.append(word_with_delete)
                    else:
                        # only interested in word candidates
                        if word_with_delete in self.dictionary:
                            deletes_word_candidates[word_with_delete] = (x_value, y_value)

                    if populate_matrix:
                        self.increase_matrix_counter(self.delete_matrix, x_value, y_value)

        #print('Deletes non-word candidates ({}): {}'.format(len(deletes_non_word_candidates), deletes_non_word_candidates))
        print('Deletes word candidates ({}): {}'.format(len(deletes_word_candidates), deletes_word_candidates))
        #print('Delete_Matrix:', self.delete_matrix)

        return deletes_non_word_candidates, deletes_word_candidates

    # rev[X, Y] = Reversal of XY
    def get_transpose_candidates_info(self, splits, real_words=False, populate_matrix=True):
        transposes_non_word_candidates = []
        transposes_word_candidates = dict()

        for left, right in splits:
            if len(right) > 1:
                # generate error candidate
                word_with_transpose = left + right[1] + right[0] + right[2:]
                x_value = right[0]
                y_value = right[1]

                if not real_words:
                    # only interested in non word candidates
                    if word_with_transpose not in self.dictionary:
                        transposes_non_word_candidates.append(word_with_transpose)
                else:
                    # only interested in word candidates
                    if word_with_transpose in self.dictionary:
                        transposes_word_candidates[word_with_transpose] = (x_value, y_value)

                if populate_matrix:
                    self.increase_matrix_counter(self.transpose_matrix, x_value, y_value)

        #print('Transposes non-word candidates ({}): {}'.format(len(transposes_non_word_candidates), transposes_non_word_candidates))
        print('Transposes word candidates ({}): {}'.format(len(transposes_word_candidates), transposes_word_candidates))
        #print('Transpose_Matrix:', self.transpose_matrix)

        return transposes_non_word_candidates, transposes_word_candidates

    # sub[X, Y] = Substitution of X(incorrect) for Y(correct)
    # Y(correct)
    def get_substitution_candidates_info(self, splits, real_words=False, populate_matrix=True):
        substitutions_non_word_candidates = []
        substitutions_word_candidates = dict()

        for left, right in splits:
            if right:
                for char in self.LETTERS:
                    # generate error candidate
                    word_with_substitution = left + char + right[1:]
                    x_value = char
                    y_value = right[0]

                    if not real_words:
                        # only interested in non word candidates
                        if word_with_substitution not in self.dictionary:
                            substitutions_non_word_candidates.append(word_with_substitution)
                    else:
                        # only interested in word candidates
                        if word_with_substitution in self.dictionary:
                            substitutions_word_candidates[word_with_substitution] = (x_value, y_value)

                    if populate_matrix:
                        self.increase_matrix_counter(self.substitution_matrix, x_value, y_value)

        #print('Substitution non-word candidates ({}): {}'.format(len(substitutions_non_word_candidates), substitutions_non_word_candidates))
        print('Substitution word candidates ({}): {}'.format(len(substitutions_word_candidates), substitutions_word_candidates))
        #print('Substitution_Matrix:', self.substitution_matrix)

        return substitutions_non_word_candidates, substitutions_word_candidates

    # add[X, Y] = Insertion of Y after X
    # Y (Inserted Letter)
    def get_insert_candidates_info(self, splits, real_words=False, populate_matrix=True):
        inserts_non_word_candidates = []
        inserts_word_candidates = dict()

        for left, right in splits:
            for char in self.LETTERS:
                if left:
                    # generate error candidate
                    word_with_insert = left + char + right
                    x_value = left[-1:]
                    y_value = char

                    if not real_words:
                        # only interested in non word candidates
                        if word_with_insert not in self.dictionary:
                            inserts_non_word_candidates.append(word_with_insert)
                    else:
                        # only interested in word candidates
                        if word_with_insert in self.dictionary:
                            inserts_word_candidates[word_with_insert] = (x_value, y_value)

                    if populate_matrix:
                        self.increase_matrix_counter(self.insert_matrix, x_value, y_value)

        #print('Insert non-word candidates ({}): {}'.format(len(inserts_non_word_candidates), inserts_non_word_candidates))
        print('Insert word candidates ({}): {}'.format(len(inserts_word_candidates), inserts_word_candidates))
        #print('Insert_Matrix:', self.insert_matrix)

        return inserts_non_word_candidates, inserts_word_candidates

    # generate all error candidates for all words in dictionary and save a file with that info and one per matrix
    def generate_errors_and_matrixes(self):
        print("Modelo del Canal Ruidoso - Total de palabras en diccionario:", len(self.dictionary))

        with open(self.SPELLING_ERROR_CANDIDATES_FILE, 'w') as spelling_error_candidates:
            i = 0
            for word_in_dict in self.dictionary:
                word_splits = self.get_splits(word_in_dict)

                word_error_candidates = self.get_delete_candidates_info(word_splits)[0] + \
                                        self.get_transpose_candidates_info(word_splits)[0] + \
                                        self.get_substitution_candidates_info(word_splits)[0] + \
                                        self.get_insert_candidates_info(word_splits)[0]

                #print('Errores candidatos para {}({}): {}\n'.format(word_in_dict, len(word_error_candidates), word_error_candidates))
                spelling_error_candidates.writelines('{}: {}\n'.format(word_in_dict, word_error_candidates))

                i += 1
                if (i % 10000) == 0:
                    print("Modelo del Canal: ", i)
                #if i > 10:
                #    break

        # write all confusion matrixes to file
        with open(self.DELETE_MATRIX_FILE, 'w') as delete_matrix_file:
            for row in self.delete_matrix:
                delete_matrix_file.write('{}\n'.format(row))

        with open(self.TRANSPOSE_MATRIX_FILE, 'w') as transpose_matrix_file:
            for row in self.transpose_matrix:
                transpose_matrix_file.write('{}\n'.format(row))

        with open(self.SUBSTITUTION_MATRIX_FILE, 'w') as substitution_matrix_file:
            for row in self.substitution_matrix:
                substitution_matrix_file.write('{}\n'.format(row))

        with open(self.INSERT_MATRIX_FILE, 'w') as insert_matrix_file:
            for row in self.insert_matrix:
                insert_matrix_file.write('{}\n'.format(row))

    # generate all possible correction candidates for misspelled word and their probabilities
    def generate_correction_probabilities(self, word):
        word_splits = self.get_splits(word)
        correction_probabilities = dict()

        # load matrixes from from files
        self.load_matrixes()

        # process DELETE probabilities using INSERT candidates for word
        insert_candidates = self.get_insert_candidates_info(word_splits, True, False)[1]
        for insert_candidate in insert_candidates:
            #print('Insert Candidate: {}. Values: {}'.format(insert_candidate, insert_candidates[insert_candidate]))
            # search in opposite operation's matrix: delete
            confusion_value = self.get_value_from_matrix(self.delete_matrix, insert_candidates[insert_candidate][0], insert_candidates[insert_candidate][1])
            substring_for_count = insert_candidates[insert_candidate][0] + insert_candidates[insert_candidate][1]
            correction_probabilities[insert_candidate] = self.get_correction_probability(insert_candidate, confusion_value, substring_for_count)

        # process transpose candidates
        transpose_candidates = self.get_transpose_candidates_info(word_splits, True, False)[1]
        for transpose_candidate in transpose_candidates:
            #print('Transpose Candidate: {}. Values: {}'.format(transpose_candidate, transpose_candidates[transpose_candidate]))
            # search in same operation matrix but reversing x and y coordinates
            confusion_value = self.get_value_from_matrix(self.transpose_matrix, transpose_candidates[transpose_candidate][1], transpose_candidates[transpose_candidate][0])
            substring_for_count = transpose_candidates[transpose_candidate][1] + transpose_candidates[transpose_candidate][0]
            correction_probabilities[transpose_candidate] = self.get_correction_probability(transpose_candidate, confusion_value, substring_for_count)

        # process substitution candidates
        substitition_candidates = self.get_substitution_candidates_info(word_splits, True, False)[1]
        for substitition_candidate in substitition_candidates:
            #print('Substitution Candidate: {}. Values: {}'.format(substitition_candidate, substitition_candidates[substitition_candidate]))
            # search in same operation matrix but reversing x and y coordinates
            confusion_value = self.get_value_from_matrix(self.substitution_matrix, substitition_candidates[substitition_candidate][1], substitition_candidates[substitition_candidate][0])
            substring_for_count = substitition_candidates[substitition_candidate][0]
            correction_probabilities[substitition_candidate] = self.get_correction_probability(substitition_candidate, confusion_value, substring_for_count)

        # process INSERT probabilities using delete candidates for word
        delete_candidates = self.get_delete_candidates_info(word_splits, True, False)[1]
        for delete_candidate in delete_candidates:
            #print('Delete Candidate: {}. Values: {}'.format(delete_candidate, delete_candidates[delete_candidate]))
            # search in opposite operation matrix: insert
            confusion_value = self.get_value_from_matrix(self.insert_matrix, delete_candidates[delete_candidate][0], delete_candidates[delete_candidate][1])
            substring_for_count = delete_candidates[delete_candidate][0]
            correction_probabilities[substitition_candidate] = self.get_correction_probability(delete_candidate, confusion_value, substring_for_count)

        print("PROBABILIDADES: ", correction_probabilities)
        return correction_probabilities

    # load matrix from ffile
    def load_matrix_from_file(self, filename, matrix):
        with open(filename, 'r', encoding= language_model.LanguageModel.FILE_ENCODING) as matrix_file:
            i = 0
            for line in matrix_file:
                matrix[i] = ast.literal_eval(line)
                i += 1

    # load all matrixes
    def load_matrixes(self):
        self.load_matrix_from_file(self.DELETE_MATRIX_FILE, self.delete_matrix)
        self.load_matrix_from_file(self.TRANSPOSE_MATRIX_FILE, self.transpose_matrix)
        self.load_matrix_from_file(self.SUBSTITUTION_MATRIX_FILE, self.substitution_matrix)
        self.load_matrix_from_file(self.INSERT_MATRIX_FILE, self.insert_matrix)

    # get value for coordinates x, y  in matrix
    def get_value_from_matrix(self, matrix, x, y):
        value = 0
        x_for_letter = self.LETTERS.find(x)
        y_for_letter = self.LETTERS.find(y)

        #print('x = {} ({}), y = {} ({})'.format(x, x_for_letter, y, y_for_letter))
        if x_for_letter >= 0 and y_for_letter >= 0:
            value = matrix[x_for_letter][y_for_letter]

        return value

    # implements formula P(x|w) = del[xi-1;wi] / count[xi-1wi]
    def get_correction_probability(self, correction_candidate, confusion_value, substring_for_count):
        # channel probability P(x|w) = del[xi-1;wi] / count[xi-1wi]
        count_value = self.db.get_substring_frequency(substring_for_count)
        channel_probability = confusion_value / count_value

        # language probability P(w)
        language_probability = self.db.get_word_probability(correction_candidate)

        # correction probability P(x|w)P(w)
        #print("Probability: {} * {} =  {}".format(channel_probability, language_probability, channel_probability * language_probability)
        return channel_probability * language_probability

    # get the most likely correct for misspelled word based on the highest priority
    def get_higher_probability_correction(self, probabilites):
        higher_probability_value = 0
        higher_probability_word = ""

        for probability_key in probabilites.keys():
            if probabilites[probability_key] > higher_probability_value:
                higher_probability_value = probabilites[probability_key]
                higher_probability_word = probability_key

        return higher_probability_word

    # get the most likely correct for misspelled word
    def get_best_correction(self, word):
        correction_probabilities = self.generate_correction_probabilities(word)
        return self.get_higher_probability_correction(correction_probabilities)
