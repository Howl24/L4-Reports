from dictionary import DictionaryManager
from sample_generator import SampleGenerator
from career_classifier import CareerClassifier
from career_classifier import Career
from offer import Offer

MODE_MSG = "Escoja una acción: "

UPDATE_CAREERS = "Actualizar Carreras Symplicity"
CLASSIFY_OFFERS = "Clasificar Ofertas"
SAVE_CLASSIFICATION_REVIEW = "Guardar Revisión"
CLOSE = "Salir"

MODES = [UPDATE_CAREERS,
         CLASSIFY_OFFERS,
         SAVE_CLASSIFICATION_REVIEW,
         CLOSE,
        ]

SYMPLICITY_SOURCE = "symplicity"
SYMPLICITY_CAREER_FEATURES = ["Majors/Concentrations"]


class ClassificationManager:

    def __init__(self, interface, dictionary=None, classifier=None):
        self.interface = interface
        self.dictionary = dictionary
        self.classifier = classifier

    def run(self):
        # TODO
        # Add save_classification
        Career.ConnectToDatabase()
        Career.PrepareStatements()

        mode = None
        while mode != CLOSE:
            mode = self.interface.choose_option(MODES, MODE_MSG)
            if mode == UPDATE_CAREERS:
                self.update_careers()

            if mode == CLASSIFY_OFFERS:
                self.classify_offers()

            if mode == SAVE_CLASSIFICATION_REVIEW:
                self.save_classification_review()

    def save_classification_review(self):
        pass

    def update_careers(self):
        careers = set()
        offers = Offer.SelectAll(SYMPLICITY_SOURCE)
        for offer in offers:
            for feature in SYMPLICITY_CAREER_FEATURES:
                if feature in offer.features:
                    offer_careers = offer.features[feature].split(",")
                    for career in offer_careers:
                        name = career.strip()
                        if name != "":
                            career = Career(name=name)
                            careers.add(career)

        for career in careers:
            career.insert()

    def classify_offers(self, export=False):

        READ_NEW_OFFERS_MSG = "Escogerá las ofertas a clasificar: "
        #TRAINING_SOURCES = ["symplicity"]
        TRAINING_SOURCES = ["symplicity"]

        TRAINING_DATE_RANGE = [(1, 2016), (12, 2017)]
        MIN_TRAINING_CNT = 50

        #self.career = self.read_career()
        self.career= Career("INGENIERÍA INFORMÁTICA").name

        sample_generator = SampleGenerator(self.interface)

        sample_generator.run(sources=TRAINING_SOURCES,
                             date_range=TRAINING_DATE_RANGE,
                             min_cnt=MIN_TRAINING_CNT,
                             career=self.career)

        sample = sample_generator.sample
        self.dictionary = sample_generator.dictionary

        labeled_offers = self.build_labeled_offers(sample)

        #for (offer,label) in labeled_offers:
        #    print(offer.careers, label)


        self.interface.show_msg_list(READ_NEW_OFFERS_MSG)
        predict_offers = sample_generator.read_offers()

        self.classifier = CareerClassifier(self.career,
                                           self.dictionary,
                                           labeled_offers,
                                           predict_offers)

        self.classifier.run()

        if export:
            filename = self.dictionary.name + "_careers.csv"
            Offer.PrintAsCsv(self.classifier.classified_offers,
                             self.dictionary.configurations,
                             filename,
                             careers=True)

    def build_labeled_offers(self, sample):
        labeled_offers = []
        for offer in sample:
            if self.career in offer.careers:
                label = 1
            else:
                label = 0

            labeled_offers.append((offer, label))

        return labeled_offers

    def read_career(self):
        CHOOSE_CAREER_MSG = "Seleccione la carrera a clasificar:"
        careers = sorted(Career.Select())
                
        career = self.interface.choose_option(careers, CHOOSE_CAREER_MSG)
        return career
