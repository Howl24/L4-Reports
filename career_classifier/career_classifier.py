from sklearn.naive_bayes import MultinomialNB
from offer import Offer
from sklearn import cross_validation
from career_classifier.constants import TRAINING_SOURCE
import text_processor as tp


class CareerClassifier:
    def __init__(self, career, dictionary, train_offers, predict_offers):
        self.career = career
        self.dictionary = dictionary
        self.train_offers = train_offers
        self.predict_offers = predict_offers

    def run(self):
        configurations = self.dictionary.configurations_by_source()
        train_conf = configurations[TRAINING_SOURCE]

        dict_phrases = self.dictionary.accepted_phrases
        vocab = [phrase.name for phrase in dict_phrases.values()]

        vectorizer = tp.build_vectorizer(train_conf, vocab)

        # Symplicity terms
        train_texts = []
        train_labels = []
        for offer, label in self.train_offers:
            text = offer.get_text(train_conf.features)
            train_texts.append(text)
            train_labels.append(label)

        train_tfidf = vectorizer.fit_transform(train_texts).toarray()

        classifier = MultinomialNB()

        predict_texts = []
        for offer in self.predict_offers:
            text = offer.get_text(configurations[offer.source].features)
            predict_texts.append(text)

        predict_tfidf = vectorizer.transform(predict_texts).toarray()
        clf = classifier.fit(train_tfidf, train_labels)
        predictions = clf.predict(predict_tfidf)

        score = cross_validation.cross_val_score(classifier,
                                                 train_tfidf,
                                                 train_labels,
                                                 cv=10)
        print(score)

        career_offers = []
        no_career_offers = []
        for idx, pred in enumerate(predictions):
            if pred == 1:
                career_offers.append(self.predict_offers[idx])
            else:
                no_career_offers.append(self.predict_offers[idx])

        self.exportClassifiedOffers(career_offers, self.career)
        self.exportClassifiedOffers(no_career_offers, "No_" + self.career)

    def exportClassifiedOffers(self, classified_offers, filename):
        configurations = self.dictionary.configurations_by_source()
        offers_by_source = {}
        for offer in classified_offers:
            if offer.source not in offers_by_source:
                offers_by_source[offer.source] = []
            offers_by_source[offer.source].append(offer)

        for source, offers in offers_by_source.items():
            Offer.PrintAsCsv(offers, configurations[source],
                             filename + "_" + source + ".csv", print_id=True)
