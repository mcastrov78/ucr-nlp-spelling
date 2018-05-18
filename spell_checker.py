import argparse
import db_support
import language_model
import noisy_channel_model

# arguments handling and help
parser = argparse.ArgumentParser()
parser.add_argument('--create', help='build or re-build the Language Model at the DB level',
                    action='store_true')
parser.add_argument("word", help="word to spell check")
args = parser.parse_args()

# counter for the total of tokens processed from the corpus
total_tokens_in_corpus = 0

languageModel = language_model.LanguageModel();
db = db_support.DBSupport();

if args.create:
    print('Building DB and Language Model ...')

    # init DB
    db.drop_db()
    db.init_db()

    # load dictionary and load de language model
    languageModel.load_dictionary()
    words_in_comments = languageModel.create_language_model()

    # persist the Language Model
    db.persist_counter(words_in_comments, languageModel.total_of_tokens)

chosen_word = args.word.lower()
chosen_word_frequency = db.get_word_frequency(chosen_word)

if chosen_word_frequency == 0:
    chosen_word_frequency = db.get_word_frequency(languageModel.UNKNOWN_WORD)
    chosen_word_probability = db.get_word_probability(languageModel.UNKNOWN_WORD)
else:
    chosen_word_probability = db.get_word_probability(chosen_word)

total_words_in_language_model = db.get_language_model_size()

db.close_db()

print('Palabra: ', chosen_word)
#print('Modelo de Lenguaje - Tamaño: ', total_words_in_language_model)
print('Modelo de Lenguaje - Frecuencia de la palabra: ', chosen_word_frequency)
print('Modelo de Lenguaje - Probabilidad de la palabra: ', chosen_word_probability)





noisy_channel = noisy_channel_model.NoisyChannelModel()

#load_dictionary()
#print(len(words_in_dict))

word = 'casa'
test_dictionary = set()
test_dictionary.add(word)

noisy_channel.generate_errors_and_matrixes(test_dictionary)
