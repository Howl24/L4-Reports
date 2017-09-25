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

        CHOOSE_CAREERS_MSG = "Seleccione las carreras q desea ingresar"

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

        careers = sorted(list(careers))
        selected_careers = self.interface.choose_multiple(careers,
                                                          CHOOSE_CAREERS_MSG)
        for career in selected_careers:
            career.insert()

    def classify_offers(self):
        WAIT_CLASSIFICATION_MSG = "Clasificando ofertas ..."

        TRAINING_SOURCE = "symplicity"

        TRAINING_DATE_RANGE = [(1, 2015), (12, 2017)]
        MIN_TRAINING_CNT = 15

        self.career = self.read_career().name
        #self.career= Career("INGENIERÍA INFORMÁTICA").name

        sample_generator = SampleGenerator(self.interface)

        sample_generator.min_cnt = MIN_TRAINING_CNT
        print("Reading Training Offers ...")
        sample_generator.run(sources=[TRAINING_SOURCE],
                             date_range=TRAINING_DATE_RANGE)

        sample = sample_generator.sample
        self.dictionary = sample_generator.dictionary

        train_offers = self.build_train_offers(sample)

        sample_generator = SampleGenerator(self.interface)
        print("Reading Predict Offers ...")
        predict_offers = sample_generator.read_offers()

        self.classifier = CareerClassifier(self.career,
                                           self.dictionary,
                                           train_offers,
                                           predict_offers)

        self.interface.wait_function(WAIT_CLASSIFICATION_MSG,
                                     self.classifier.run)

    def build_train_offers(self, sample):
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
