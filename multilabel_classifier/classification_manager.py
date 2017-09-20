class ClassificationManager:
    def __init__(self, interface, dictionary=None, classifier=None):
        self.interface = interface
        self.dictionary = dictionary
        self.classifier = classifier

    def run(self):
        Career.ConnectToDatabase()
        Career.PrepareStatements()

        mode = None
        while mode != CLOSE:
            mode = self.interface.choose_option(MODES, MODE_MSG)

            if mode == CLASSIFY_OFFERS:
                self.classify_offers()
        
            if mode == SAVE_CLASSIFICATION_REVIEW:
                self.save_classification_review()

    def classify_offers(self):
        pass


    def save_classification_review(self):



