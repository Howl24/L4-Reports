from career import Career
from multilabel_classifier import MultilabelClassifier
from label import Label
import csv
from sample_generator import SampleGenerator
from dictionary import DictionaryManager
from offer import Offer
from utils import read_import_filename

from offer.constants import OFFER_ID_FIELD
from offer.constants import OFFER_YEAR_FIELD
from offer.constants import OFFER_MONTH_FIELD
from offer.constants import OFFER_SOURCE_FIELD

from multilabel_classifier.constants import MODES
from multilabel_classifier.constants import MODE_MSG
from multilabel_classifier.constants import SET_CAREER_LABELS
from multilabel_classifier.constants import GET_OFFERS_TO_LABEL
from multilabel_classifier.constants import SAVE_CLASSIFICATION_REVIEW
from multilabel_classifier.constants import CLASSIFY_OFFERS
from multilabel_classifier.constants import CLOSE

from multilabel_classifier.constants import READ_FIELD_MSG
from multilabel_classifier.constants import FIELD
from multilabel_classifier.constants import READ_LABEL_MSG
from multilabel_classifier.constants import LABEL_FIELD
from multilabel_classifier.constants import READ_LABELS_STOP_STRING
from multilabel_classifier.constants import READ_LABELS_HINT
from multilabel_classifier.constants import CHOOSE_FIELD_MSG

from multilabel_classifier.constants import TRAINING_SOURCE
from multilabel_classifier.constants import TRAINING_DATE_RANGE
from multilabel_classifier.constants import TRAINING_MIN_OFFER_CNT

from multilabel_classifier.constants import READ_LABELED_OFFERS_FILENAME_MSG
from multilabel_classifier.constants import CHOOSE_CAREER_MSG


class ClassificationManager:
    def __init__(self, interface, dictionary=None, classifier=None):
        self.interface = interface
        self.dictionary = dictionary
        self.classifier = classifier

    def run(self):
        Career.ConnectToDatabase()
        Career.PrepareStatements()

        Label.ConnectToDatabase()
        Label.PrepareStatements()

        mode = None
        while mode != CLOSE:
            mode = self.interface.choose_option(MODES, MODE_MSG)

            if mode == SET_CAREER_LABELS:
                self.set_labels()

            if mode == GET_OFFERS_TO_LABEL:
                self.get_offers_to_label()

            if mode == SAVE_CLASSIFICATION_REVIEW:
                self.save_classification_review()

            if mode == CLASSIFY_OFFERS:
                self.classify_offers()

    # --------------------------------------------------------------------

    def set_labels(self):
        career = self.read_career().name
        field = self.read_field_name()
        label_names = self.read_label_names()

        for label_name in label_names:
            label = Label(career, field, label_name)
            label.insert()

    def read_field_name(self):
        field = self.interface.read_string(READ_FIELD_MSG,
                                           FIELD)

        return field

    def read_label_names(self):
        show_hint = True

        labels = self.interface.read_unlimited_string_list(
                READ_LABEL_MSG,
                LABEL_FIELD,
                READ_LABELS_STOP_STRING,
                show_hint,
                READ_LABELS_HINT)

        return labels

    # ------------------------------------------------------------------

    def select_labels(self, career):
        labels_by_field = Label.Select(career)

        fields = list(labels_by_field.keys())
        chosen_field = self.interface.choose_option(fields,
                                                    CHOOSE_FIELD_MSG)
        labels = labels_by_field[chosen_field]

        return chosen_field, labels

    def get_offers_to_label(self):
        self.career = self.read_career().name
        field, labels = self.select_labels(self.career)

        sample_generator = SampleGenerator(self.interface)

        sample_generator.min_cnt = TRAINING_MIN_OFFER_CNT
        sample_generator.run(sources=[TRAINING_SOURCE],
                             date_range=TRAINING_DATE_RANGE,
                             career=self.career)

        offers = sample_generator.sample
        print("Sample offers: ", len(offers))
        sample_dict = sample_generator.dictionary

        conf = sample_dict.configurations_by_source()[TRAINING_SOURCE]

        filename = self.career + "_ofertas.csv"
        Offer.PrintAsCsv(offers,
                         conf,
                         filename,
                         print_id=True,
                         print_labels=True,
                         field=field,
                         labels=labels,
                         )
    # --------------------------------------------------------------------

    def save_classification_review(self):
        self.career = self.read_career().name
        field, labels = self.select_labels(self.career)

        filename = read_import_filename(self.interface,
                                        READ_LABELED_OFFERS_FILENAME_MSG)

        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for idx, row in enumerate(reader):
                id = row[OFFER_ID_FIELD]
                year = int(row[OFFER_YEAR_FIELD])
                month = int(row[OFFER_MONTH_FIELD])
                source = row[OFFER_SOURCE_FIELD]

                offer = Offer.Select(year, month, id, source)

                if field not in offer.features:
                    # Empty field feature
                    offer.features[field] = ""

                offer_labels = offer.features[field].split(",")
                for label in labels:
                    mark = row[label]
                    if mark == "":
                        # Remove
                        if label in offer_labels:
                            offer_labels.remove(label)

                    else:
                        # Add
                        if label not in offer_labels:
                            offer_labels.append(label)

                # Update field feature
                offer.features[field] = ",".join(offer_labels)
                offer.insert()

    # -------------------------------------------------------------

    def classify_offers(self):
        self.career = self.read_career().name
        field, labels = self.select_labels(self.career)
        # self.career = Career("INGENIERÍA INFORMÁTICA")

        dict_manager = DictionaryManager(self.interface)
        self.dictionary = dict_manager.select_old_dictionary()

        train_offers = self.read_train_offers(field, labels)

        sample_generator = SampleGenerator(self.interface)
        predict_offers = sample_generator.read_offers(career=self.career)

        self.classifier = MultilabelClassifier(self.career,
                                               field,
                                               labels,
                                               self.dictionary,
                                               train_offers,
                                               predict_offers)

        self.classifier.run()

    def read_train_offers(self, field, labels):
        sample_generator = SampleGenerator(self.interface)
        offers = sample_generator.read_offers(sources=[TRAINING_SOURCE],
                                              date_range=TRAINING_DATE_RANGE,
                                              career=self.career)

        train_offers = []
        for offer in offers:
            if field in offer.features:
                offer_labels = offer.features[field].split(",")
                if offer_labels:
                    train_offer_labels = []
                    for label in labels:
                        if label in offer_labels:
                            train_offer_labels.append(label)

                    train_offers.append((offer, train_offer_labels))

        return train_offers

    def read_career(self):
        # TODO
        # Move to static library
        careers = sorted(Career.Select())

        career = self.interface.choose_option(careers, CHOOSE_CAREER_MSG)
        return career
