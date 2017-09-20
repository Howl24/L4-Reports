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

        train_texts = []
        train_labels = []
        for offer, labels in self.train_offers:
            text = offer.get_text(configuration.features)
            train_texts.append(text)
            train_labels.append(label)

        td_idf = vectorizer.fit_transform(train_texts).toarray()

    def build_labeled_offers(self, offers, labels):
        labeled_offers = []
        for offer in offers:
            offer_labels = []
            for label in labels:
                if label in offer.features["AreasConocimiento"]:
                    offer_labels.append(1)
                else:
                    offer_labels.append(0)

            labeled_offers.append((offer, offer_labels))

        return labeled_offers
