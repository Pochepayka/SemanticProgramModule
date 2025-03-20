import gensim.downloader
from gensim.models import KeyedVectors
import os

def download_w2v_rus():
    # скачивание бинарника модели W2V_ru
    word2vec_rus = gensim.downloader.load('word2vec-ruscorpora-300')
    model_path = os.path.join(os.path.dirname(__file__), "models", "ru_word2vec.bin")
    word2vec_rus.save_word2vec_format(model_path, binary=True)
    return model_path


def load_w2v_rus():
    #использование W2V_ru из бинарника
    try:
        model = KeyedVectors.load_word2vec_format(os.path.join(os.path.dirname(__file__), "models", "ru_word2vec.bin"), binary=True)
    except:
        model = KeyedVectors.load_word2vec_format(download_w2v_rus(), binary=True)
        print("ru_word2vec.bin не удалось найти, он был загружен в models/ru_word2vec.bin")
    return model
