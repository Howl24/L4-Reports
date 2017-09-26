from sample_generator import SampleGenerator
from career_classifier import CareerClassifier
from career_classifier import Career
from utils import read_import_filename
from offer import Offer
from offer.constants import OFFER_ID_FIELD
from offer.constants import OFFER_YEAR_FIELD
from offer.constants import OFFER_MONTH_FIELD
from offer.constants import OFFER_SOURCE_FIELD
import csv

from career_classifier.constants import MODE_MSG
from career_classifier.constants import UPDATE_CAREERS
from career_classifier.constants import CLASSIFY_OFFERS
from career_classifier.constants import SAVE_CLASSIFICATION_REVIEW
from career_classifier.constants import CLOSE
from career_classifier.constants import MODES

from career_classifier.constants import CHOOSE_CAREER_MSG
from career_classifier.constants import READ_CAREER_OFFERS_FILENAME_MSG

from career_classifier.constants import CHOOSE_CAREERS_MSG
from career_classifier.constants import SYMPLICITY_SOURCE
from career_classifier.constants import SYMPLICITY_CAREER_FEATURES

from career_classifier.constants import TRAINING_SOURCE
from career_classifier.constants import TRAINING_DATE_RANGE
from career_classifier.constants import MIN_TRAINING_CNT
from career_classifier.constants import WAIT_CLASSIFICATION_MSG


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
            if mode == UPDATE_CAREERS:
                self.update_careers()

            if mode == CLASSIFY_OFFERS:
                self.classify_offers()

            if mode == SAVE_CLASSIFICATION_REVIEW:
                self.save_classification_review()

    def save_classification_review(self):
        self.career = self.read_career().name

        filename = read_import_filename(self.interface,
                                        READ_CAREER_OFFERS_FILENAME_MSG)

        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for idx, row in enumerate(reader):
                try:
                    id = row[OFFER_ID_FIELD]
                    year = int(row[OFFER_YEAR_FIELD])
                    month = int(row[OFFER_MONTH_FIELD])
                    source = row[OFFER_SOURCE_FIELD]
                except ValueError:
                    print("Valor incorrecto en la fila ", idx)
                except KeyError:
                    print("Valor faltante en la fila ", idx)

                offer = Offer.Select(year, month, id, source)
                offer.careers.add(self.career)
                offer.insert()

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

        careers = sorted(list(careers))
        selected_careers = self.interface.choose_multiple(careers,
                                                          CHOOSE_CAREERS_MSG)
        for career in selected_careers:
            career.insert()

    def classify_offers(self):

        self.career = self.read_career().name
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
        careers = sorted(Career.Select())

        career = self.interface.choose_option(careers, CHOOSE_CAREER_MSG)
        return career
