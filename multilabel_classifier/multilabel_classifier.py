import text_processor as tp
from sklearn.naive_bayes import MultinomialNB
from sklearn.multiclass import OneVsRestClassifier


class MultilabelClassifier:
    def __init__(self, career, dictionary, train_offers, predict_offers):
        self.career = career
        self.dictionary = dictionary
        self.train_offers = train_offers
        self.predict_offers = predict_offers

    def run(self):

        TRAINING_SOURCE = "symplicity"
        configurations = self.dictionary.configurations_by_source()
        configuration = configurations[TRAINING_SOURCE]

        dict_phrases = self.dictionary.accepted_phrases
        vocab = [phrase.name for phrase in dict_phrases.values()]

        vectorizer = tp.build_vectorizer(configuration, vocab)

        train_texts = []
        train_labels = []
        for offer, labels in self.train_offers:
            # Current offer is offer_text
            #text = offer.get_text(configuration.features)

            train_texts.append(text)
            train_labels.append(label)

        train_tf_idf = vectorizer.fit_transform(train_texts).toarray()

        predict_texts = []
        for offer in self.predict_offers:
            text = offer.get_text(configurations[offer.source].features)
            predict_texts.append(text)

        pred_tf_idf = vectorizer.transform(predict_texts).toarray()

        classifier = OneVsRestClassifier(MultinomialNB())
        predictions = classifier.fit(train_tf_idf, train_labels).predict(pred_tf_idf)
        score = cross_validation.cross_val_score(classifier, tf_idf, labels, cv=10)
