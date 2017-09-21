from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
import text_processor as tp
from dictionary import Phrase
from offer import Offer
from sklearn import cross_validation


class CareerClassifier:
    def __init__(self, career, dictionary, labeled_offers, new_offers):
        self.career = career
        self.dictionary = dictionary
        self.labeled_offers = labeled_offers
        self.new_offers = new_offers

    def run(self):
        TRAINING_SOURCES = ["symplicity"]

        configurations = self.dictionary.configurations_by_source()
        configuration = configurations[TRAINING_SOURCES[0]]

        dict_phrases = self.dictionary.accepted_phrases
        vocab = [phrase.name for phrase in dict_phrases.values()]

        vectorizer = tp.build_vectorizer(configuration, vocab)

        #Symplicity terms
        labeled_texts = []
        labels = []
        for offer,label in self.labeled_offers:
            text = offer.get_text(configuration.features)
            labeled_texts.append(text)
            labels.append(label)

        tf_idf = vectorizer.fit_transform(labeled_texts).toarray()

        classifier = MultinomialNB()
        #classifier = GaussianNB()
        #classifier = MLPClassifier()

        predict_texts = []
        print(len(self.new_offers))
        for offer in self.new_offers:
            text = offer.get_text(configurations[offer.source].features)
            predict_texts.append(text)

        pred_tf_idf = vectorizer.transform(predict_texts).toarray()
        predictions = classifier.fit(tf_idf, labels).predict(pred_tf_idf)

        score = cross_validation.cross_val_score(classifier, tf_idf, labels, cv=10)
        print(score)

        ok = []
        no_ok = []
        for idx, pred in enumerate(predictions):
            if pred == 1:
                ok.append(self.new_offers[idx])
            else:
                no_ok.append(self.new_offers[idx])

        Offer.PrintAsCsv([x for x,y in self.labeled_offers if y == 1], self.dictionary.configurations, "Training.csv")
        Offer.PrintAsCsv(ok, self.dictionary.configurations, "Yes.csv")
        Offer.PrintAsCsv(no_ok, self.dictionary.configurations, "No.csv")
