import sqlite3


class DBSupport:
    DB_FILENAME = 'language_model.db'

    def __init__(self):
        # DB will be used to avoid loading all data every time
        self.connection = sqlite3.connect(self.DB_FILENAME)
        self.cursor = self.connection.cursor()

    def init_db(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS '
                       'language_model(word TEXT PRIMARY KEY, frequency INTEGER, probability REAL, updated_at DATETIME)')
        self.connection.commit()

    def drop_db(self):
        self.cursor.execute('DROP TABLE IF EXISTS language_model')
        self.connection.commit()

    def close_db(self):
        self.cursor.close()
        self.connection.close()

    def persist_counter(self, words_in_comments, total_tokens_in_corpus):
        for element in words_in_comments.items():
            probability = element[1] / total_tokens_in_corpus
            self.cursor.execute('INSERT INTO language_model(word, frequency, probability, updated_at) '
                           'VALUES(?, ?, ?, datetime("now", "localtime"))', (element[0], element[1], probability))
            self.connection.commit()

    def get_language_model_size(self):
        size = 0

        self.cursor.execute('SELECT SUM(frequency) FROM language_model')
        result = self.cursor.fetchone()
        if result:
            size = result[0]

        return size

    def get_word_frequency(self, word):
        frequency = 0

        self.cursor.execute('SELECT frequency FROM language_model WHERE word = ?', [word])
        result = self.cursor.fetchone()
        if result:
            frequency = result[0]

        return frequency

    def get_word_probability(self, word):
        frequency = 0

        self.cursor.execute('SELECT probability FROM language_model WHERE word = ?', [word])
        result = self.cursor.fetchone()
        if result:
            frequency = result[0]

        return frequency

    def get_substring_frequency(self, substring):
        frequency = 0

        self.cursor.execute('SELECT SUM(frequency) FROM language_model where word like ? order by word', ['%' + substring + '%'])
        result = self.cursor.fetchone()
        if result:
            frequency = result[0]

        return frequency


