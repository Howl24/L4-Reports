import text_processor as tp
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn import cross_validation
from offer import Offer

class MultilabelClassifier:
    def __init__(self, career, field, labels, dictionary,
                 train_offers, predict_offers):
        self.career = career
        self.field = field
        self.labels = labels
        self.dictionary = dictionary
        self.train_offers = train_offers
        self.predict_offers = predict_offers

    def run(self):

        TRAINING_SOURCE = "symplicity"
        configurations = self.dictionary.configurations_by_source()
        train_conf = configurations[TRAINING_SOURCE]

        dict_phrases = self.dictionary.accepted_phrases
        vocab = [phrase.name for phrase in dict_phrases.values()]

        vectorizer = tp.build_vectorizer(train_conf, vocab)

        # Symplicity terms
        train_texts = []
        train_labels = []
        for offer, labels in self.train_offers:
            text = offer.get_text(train_conf.features)
            train_texts.append(text)
            train_labels.append(labels)

        mlb = MultiLabelBinarizer()
        train_labels = mlb.fit_transform(train_labels)
        print(train_labels)

        train_tfidf = vectorizer.fit_transform(train_texts).toarray()

        classifier = OneVsRestClassifier(MultinomialNB())

        predict_texts = []
        for offer in self.predict_offers:
            text = offer.get_text(configurations[offer.source].features)
            predict_texts.append(text)

        predict_tfidf = vectorizer.transform(predict_texts).toarray()
        cls = classifier.fit(train_tfidf, train_labels)
        predictions = cls.predict(predict_tfidf)

        score = cross_validation.cross_val_score(classifier,
                                                 train_tfidf,
                                                 train_labels,
                                                 cv=5)
        print(score)

        predictions = mlb.inverse_transform(predictions)
        results = zip(self.predict_offers, predictions)

        self.exportClassifiedOffers(results, self.career + "_" + self.field)

    def exportClassifiedOffers(self, results, filename):
        configurations = self.dictionary.configurations_by_source()
        offers_by_source = {}
        for offer, labels in results:
            if offer.source not in offers_by_source:
                offers_by_source[offer.source] = []
            offers_by_source[offer.source].append((offer, labels))

        for source, results in offers_by_source.items():
            offers = []
            for offer, labels in results:
                offers.append(offer)
                if self.field not in offer.features:
                    # Empty field feature
                    offer.features[self.field] = ""

                offer_labels = offer.features[self.field].split(",")
                for label in self.labels:
                    if label not in labels:
                        if label in offer_labels:
                            offer_labels.remove(label)
                    else:
                        if label not in offer_labels:
                            offer_labels.append(label)
                            
                offer.features[self.field] = ",".join(offer_labels)

            Offer.PrintAsCsv(offers, configurations[source],
                             filename + "_" + source + ".csv",
                             print_id=True, print_labels=True,
                             field=self.field, labels=self.labels)
