from career import Career
from multilabel_classifier import MultilabelClassifier
from label import Label
import csv
from sample_generator import SampleGenerator
from offer import Offer

GET_OFFERS = "Obtener ofertas a clasificar"
SET_CAREER_LABELS = "Crear etiquetas para clasificación"
CLASSIFY_OFFERS = "Clasificar Areas de Conocimiento"
SAVE_CLASSIFICATION_REVIEW = "Guardar Revisión"
CLOSE = "Salir"

MODES = [SET_CAREER_LABELS,
         GET_OFFERS,
         CLASSIFY_OFFERS,
         SAVE_CLASSIFICATION_REVIEW,
         CLOSE,
        ]

MODE_MSG = "Seleccione una opción: "

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

            if mode == GET_OFFERS:
                self.get_offers()

            if mode == CLASSIFY_OFFERS:
                self.classify_offers()
        
            if mode == SAVE_CLASSIFICATION_REVIEW:
                self.save_classification_review()

    # --------------------------------------------------------------------------------------------

    def set_labels(self):
        
        career = self.read_career().name
        field = self.read_field_name()
        label_names = self.read_label_names()

        for label_name in label_names:
            label = Label(career, field, label_name)
            label.insert()

    def read_field_name(self):
        READ_FIELD_MSG = "Ingrese el nombre del campo que agrupe las etiquetas"
        FIELD = "Campo: "
        
        field = self.interface.read_string(READ_FIELD_MSG,
                                           FIELD)

        return field

    def read_label_names(self):
        READ_LABEL_MSG = "Ingrese el nombre de las etiquetas"
        LABEL_FIELD = "Etiqueta: "
        STOP_STRING = ""
        HINT = "(Etiqueta vacía para terminar.)"
        show_hint = True

        labels = self.interface.read_unlimited_string_list(READ_LABEL_MSG,
                                                           LABEL_FIELD,
                                                           STOP_STRING,
                                                           show_hint,
                                                           HINT)
        return labels

    # -------------------------------------------------------------------------------------------

    def select_labels(self, career):
        labels_by_field = Label.Select(career)

        CHOOSE_FIELD_MSG = "Seleccione un campo: "

        chosen_field = self.interface.choose_option(list(labels_by_field.keys()), CHOOSE_FIELD_MSG)
        labels = labels_by_field[chosen_field]

        return chosen_field, labels

    def get_offers(self):
        TRAINING_SOURCE = "symplicity"
        TRAINING_DATE_RANGE = [(1, 2016), (12, 2017)]
        TRAINING_MIN_WORD_COUNT = 50

        self.career = self.read_career().name
        field, labels = self.select_labels(self.career)

        sample_generator = SampleGenerator(self.interface)

        sample_generator.run(sources=[TRAINING_SOURCE],
                             date_range=TRAINING_DATE_RANGE,
                             min_cnt=TRAINING_MIN_WORD_COUNT,
                             career=self.career)

        offers = sample_generator.sample
        print("Sample offers: ", len(offers))
        sample_dict = sample_generator.dictionary

        configurations = sample_dict.configurations_by_source()

        filename = self.career + "_ofertas.csv"
        Offer.PrintAsCsv(offers,
                         configurations[TRAINING_SOURCE],
                         filename, 
                         print_id=True,
                         print_labels=True,
                         field=field,
                         labels=labels,
                         )

    def save_classification_review(self):
        READ_CLASSIFICATION_REVIEW = "Seleccione el archivo con las ofertas revisadas"

        source = self.read_source()
        dict_manager = DictionaryManager(self.interface)

        filename = dict_manager.read_import_filename(READ_CLASSIFICATION_REVIEW)

        with open(filename, "r") as f:
            reader = csv.reader(f, delimiter=",", quotechar="^")
            headers = next(reader)[1:]
            for row in reader:
                offer_id = row[0]
                offer_labels = row[1]

    def read_source(self):
        #TODO
        # Move to static file

        SELECT_SOURCE_MSG = "Seleccione la fuente de las ofertas revisadas"
        KEYSPACES = ["new_btpucp",
                     "new_aptitus",
                     "new_bumeran",
                     "new_cas",
                     "symplicity"]

        selected_source = self.interface.choose_option(KEYSPACES,
                                                       SELECT_SOURCE,MSG)

        return selected_source



    def classify_offers(self):

        # Replace by Database sample
        # Filter by career and feature 'AreasConocimiento' not empty

        #train_offers = []
        #with open("informatica_areas.csv", "r") as f:
        #    reader = csv.reader(f, delimiter=",", quotechar="^")
        #    for row in reader:
        #        train_offers.append((row[1], row[0]))

        #all_labels = set()
        #for offer, label in train_offers:
        #    all_labels.add(label)
        #all_labels = list(all_labels)

        # Replace when u have AreasConocimiento filled
        #train_offers = self.build_labeled_offers(self, offers, labels)

        TRAINING_SOURCE = "symplicity"
        TRAINING_DATE_RANGE = [(1, 2013), (12, 2017)]

        #self.career = self.read_career()
        self.career = Career("INGENIERÍA INFORMÁTICA")

        sample_generator = SampleGenerator(self.interface)
        sample_generator.run(sources=[TRAINING_SOURCE],
                             date_range=TRAINING_DATE_RANGE,
                             min_cnt=MIN_TRAINING_CNT)

        sample = sample_generator.sample
        self.dictionary = sample_generator.dictionary

        labeled_offers = []
        for offer, offer_label in train_offers:
            offer_labels = []
            for label in all_labels:
                if label == offer_label:
                    offer_labels.append(1)
                else:
                    offer_labels.append(0)

            labeled_offers.append((offer, offer_labels))

        train_offers = labeled_offers
        predict_offers = sample_generator.read_offers()

        self.classifier = MultilabelClassifier(self.career,
                                               self.dictionary,
                                               train_offers,
                                               predict_offers)

        self.classifier.run()


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


    def save_classification_review(self):
        pass


    def read_career(self):
        # TODO 
        # Move to static library
        CHOOSE_CAREER_MSG = "Seleccione la carrera a clasificar:"
        careers = sorted(Career.Select())
                
        career = self.interface.choose_option(careers, CHOOSE_CAREER_MSG)
        return career
