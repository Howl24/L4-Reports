from interface import Interface
from dictionary import Dictionary
from offer import Offer
from sample_generator import SampleGenerator
import career_classifier
import multilabel_classifier

SAMPLE_GENERATOR = "Generador de Muestras"
CAREER_CLASSIFIER = "Clasificador de Carreras"
MULTILABEL_CLASSIFIER = "Clasificador de Areas de Conocimiento"
CLOSE = "Salir"
MODES = [SAMPLE_GENERATOR,
         CAREER_CLASSIFIER,
         MULTILABEL_CLASSIFIER,
         CLOSE,
         ]
MODE_MSG = "Escoja una opción: "


def replace_out():
    import sys
    file = open('out.txt', 'w')
    sys.stdout = file
    sys.stderr = file


def generate_sample(view):
    sample_generator = SampleGenerator(view)
    sample_generator.run(export=True)


def run_career_classifier(view):
    classification_manager = career_classifier.ClassificationManager(view)
    classification_manager.run()


def run_multilabel_classifier(view):
    classification_manager = multilabel_classifier.ClassificationManager(view)
    classification_manager.run()


def main():
    # Only for develop
    replace_out()

    view = Interface()
    cluster = Dictionary.ConnectToDatabase()
    Offer.ConnectToDatabase(cluster)

    mode = None
    while (mode != CLOSE):
        mode = view.choose_option(MODES, MODE_MSG)
        if mode == SAMPLE_GENERATOR:
            generate_sample(view)
        if mode == CAREER_CLASSIFIER:
            run_career_classifier(view)
        if mode == MULTILABEL_CLASSIFIER:
            run_multilabel_classifier(view)


if __name__ == "__main__":
    main()
