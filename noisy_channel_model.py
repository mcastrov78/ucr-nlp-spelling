class NoisyChannelModel:

    def __init__(self):
        self.letters = 'abcdefghijklmnopqrstuvwxyz'
        letters_range = range(len(self.letters))
        self.delete_matrix = [[0 for i in letters_range] for j in letters_range]
        self.transpose_matrix = [[0 for i in letters_range] for j in letters_range]
        self.substitution_matrix = [[0 for i in letters_range] for j in letters_range]
        self.insert_matrix = [[0 for i in letters_range] for j in letters_range]

    def get_splits(self, word):
        splits = []

        for i in range(len(word) + 1):
            splits.append((word[:i], word[i:]))

        print('Splits ({}): {}'.format(len(splits), splits))

        return splits

    def get_delete_candidates_info(self, splits):
        deletes = []

        for left, right in splits:
            if right:
                if len(left) > 0:
                    word_with_delete = left + right[1:]
                    x = left[-1:]
                    y = right[0]
                    # print(x, y)

                    deletes.append(word_with_delete)

                    # ignore vowels with accents and other characters not in 'letters'
                    x_for_letter = self.letters.find(x)
                    y_for_letter = self.letters.find(y)
                    if x_for_letter >= 0 and y_for_letter >= 0:
                        self.delete_matrix[x_for_letter][y_for_letter] += 1

        print('Deletes ({}): {}'.format(len(deletes), deletes))
        print('delete_matrix:', self.delete_matrix)

        return deletes

    def get_transpose_candidates_info(self, splits):
        transposes = []

        for left, right in splits:
            if len(right) > 1:
                word_with_transpose = left + right[1] + right[0] + right[2:]
                x = right[0]
                y = right[1]
                # print(x, y)

                transposes.append(word_with_transpose)

                # ignore vowels with accents and other characters not in 'letters'
                x_for_letter = self.letters.find(x)
                y_for_letter = self.letters.find(y)
                if x_for_letter >= 0 and y_for_letter >= 0:
                    self.transpose_matrix[x_for_letter][y_for_letter] += 1

        print('Transposes ({}): {}'.format(len(transposes), transposes))
        print('transpose_matrix:', self.transpose_matrix)

        return transposes

    def get_substitution_candidates_info(self, splits):
        substitutions = []

        for left, right in splits:
            if right:
                for char in self.letters:
                    word_with_substitution = left + char + right[1:]
                    x = char
                    y = right[0]
                    # print(x, y)

                    substitutions.append(word_with_substitution)

                    # ignore vowels with accents and other characters not in 'letters'
                    x_for_letter = self.letters.find(x)
                    y_for_letter = self.letters.find(y)
                    if x_for_letter >= 0 and y_for_letter >= 0:
                        self.substitution_matrix[x_for_letter][y_for_letter] += 1

        print('Substitutions ({}): {}'.format(len(substitutions), substitutions))
        print('substitution_matrix:', self.substitution_matrix)

        return substitutions

    def get_insert_candidates_info(self, splits):
        inserts = []

        for left, right in splits:
            for char in self.letters:
                if left:
                    word_with_insert = left + char + right
                    x = left[-1:]
                    y = char
                    # print(x, y)

                    inserts.append(word_with_insert)

                    # ignore vowels with accents and other characters not in 'letters'
                    x_for_letter = self.letters.find(x)
                    y_for_letter = self.letters.find(y)
                    if x_for_letter >= 0 and y_for_letter >= 0:
                        self.insert_matrix[x_for_letter][y_for_letter] += 1

        print('Inserts ({}): {}'.format(len(inserts), inserts))
        print('insert_matrix:', self.insert_matrix)

        return inserts

    def generate_errors_and_matrixes(self, words_in_dict):
        print("Total de palabras en diccionario:", len(words_in_dict))

        with open('spelling_error_candidates.txt', 'w') as spelling_error_candidates:
            i = 0
            for word_in_dict in words_in_dict:
                word_splits = self.get_splits(word_in_dict)

                word_error_candidates = self.get_delete_candidates_info(word_splits) + \
                                        self.get_transpose_candidates_info(word_splits) + \
                                        self.get_substitution_candidates_info(word_splits) + \
                                        self.get_insert_candidates_info(word_splits)

                spelling_error_candidates.writelines('{}: {}\n'.format(word_in_dict, word_error_candidates))

                print(i)
                i += 1
                #if i > 10:
                #    break;

        with open('delete_matrix.txt', 'w') as delete_matrix_file:
            for row in self.delete_matrix:
                delete_matrix_file.write('{}\n'.format(row))

        with open('transpose_matrix.txt', 'w') as transpose_matrix_file:
            for row in self.transpose_matrix:
                transpose_matrix_file.write('{}\n'.format(row))

        with open('substitution_matrix.txt', 'w') as substitution_matrix_file:
            for row in self.substitution_matrix:
                substitution_matrix_file.write('{}\n'.format(row))

        with open('insert_matrix.txt', 'w') as insert_matrix_file:
            for row in self.insert_matrix:
                insert_matrix_file.write('{}\n'.format(row))
