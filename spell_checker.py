import argparse
import db_support
import language_model
import noisy_channel_model

DICTIONARY_FILE = 'diccionarioCompletoEspañolCR.txt'
CORPUS_FILE = 'datos_original.txt'

# arguments handling and help
parser = argparse.ArgumentParser()
parser.add_argument('--lang', help='build or re-build the Language Model',
                    action='store_true')
parser.add_argument('--channel', help='build or re-build the Noisy Channel Model',
                    action='store_true')
parser.add_argument("word", help="word to spell check")
args = parser.parse_args()

# create Language Model, Dictionary, and Noisy Chanel Model instances
languageModel = language_model.LanguageModel();
dictionary = languageModel.load_dictionary(DICTIONARY_FILE)
noisy_channel = noisy_channel_model.NoisyChannelModel(dictionary)

# initialize DB support
db = db_support.DBSupport();

# build or re-build the Language Model
if args.lang:
    print('Creando Modelo de Lenguaje ...')

    # new DB
    db.drop_db()
    db.init_db()

    # load dictionary and load de language model
    words_in_comments = languageModel.create_language_model(CORPUS_FILE, dictionary)

    # persist the Language Model on the DB
    db.persist_counter(words_in_comments, languageModel.total_of_tokens)

    # close DB
    db.close_db()

# build or re-build the Noisy Channel Model
if args.channel:
    print('Creando Modelo del Canal Sucio ...')

    # configure Noisy Channel Model
    noisy_channel.generate_errors_and_matrixes()

# process input word entered as parameter
chosen_word = args.word.lower()

print('Palabra: ', chosen_word)
print('Correción: ', noisy_channel.get_best_correction(chosen_word))
