import gensim

MODEL_FILENAME = "word2vec/model"


def get_model():
    model = gensim.models.Word2Vec.load(MODEL_FILENAME)
    model.init_sims(replace=True)
    return model
