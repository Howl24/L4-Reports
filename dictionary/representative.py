from dictionary import Phrase

import word2vec
import time
import sys

from contextlib import contextmanager
from dictionary.constants import SIMILARITY_PERCENTAGE


@contextmanager
def timeit_context(name):
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    print('[{}] finished in {} ms'.format(name, int(elapsedTime * 1000)))


class Representative:

    session = None
    insert_stmt = None
    select_stmt = None
    table_name = "dict_representatives"

    def __init__(self, name, state, phrases=[]):
        self.name = name
        self.state = state
        self.phrases = phrases

    @classmethod
    def ByDictName(cls, dictionary_name):
        phrases = Phrase.ByDictName(dictionary_name)

        representatives = {}
        for phrase in phrases:
            rep_name = phrase.representative
            rep_state = phrase.state
            if rep_name not in representatives:
                representatives[rep_name] = Representative(rep_name, rep_state)

            representatives[rep_name].add_phrase(phrase)

        return list(representatives.values())

    @classmethod
    def FromPhrases(cls, phrases):
        similarity_model = word2vec.get_model()

        with timeit_context("Phrase Sort"):
            phrases.sort()

        with timeit_context("Double for"):
            for i in phrases:
                ws1 = i.name.split()

        print("Nro de frases: ", len(phrases))

        with timeit_context("Representative Build"):
            representatives = []

            for i in range(0, len(phrases)):
                # Print advance
                laps = int(len(phrases)/100) + 1
                if (i % laps) == 0:
                    print("Avance: ", int(i/laps), "%")
                    sys.stdout.flush()

                if phrases[i] is None:
                    continue

                rep_phrase = phrases[i]
                representative = Representative(rep_phrase.name,
                                                rep_phrase.state,
                                                [])

                for j in range(i, len(phrases)):
                    if phrases[j] is None:
                        continue

                    comp_phrase = phrases[j]

                    ws1 = rep_phrase.name.split()
                    ws2 = comp_phrase.name.split()

                    try:
                        similarity = similarity_model.wv.n_similarity(ws1, ws2)
                    except KeyError:
                        # word not in similarity model
                        if ws1 == ws2:
                            similarity = 1
                        else:
                            similarity = 0

                    if similarity > SIMILARITY_PERCENTAGE:
                        representative.add_phrase(comp_phrase)
                        phrases[j] = None

                phrases[i] = None
                representatives.append(representative)

        return representatives

    def add_phrase(self, phrase):
        self.phrases.append(phrase)
        return phrase

    def find_phrase(self, name):
        for phrase in self.phrases:
            if phrase.name == name:
                return phrase

    def __str__(self):
        lines = []
        lines.append("Representative: " + self.name)
        for phrase in self.phrases:
            lines.append(self.name + ", " + phrase.name)

        return "\n".join(lines)

    @classmethod
    def ExportAsCsv(cls,
                    representatives,
                    filename_representatives,
                    filename_review):

        # Representatives and similar phrases
        f_representatives = open(filename_representatives, 'w')
        print("Representante, Frase Similar", file=f_representatives)
        for rep in representatives:
            for phrase in rep.phrases:
                if rep.state is None or phrase.state is None:
                    state = ""
                    print(", ".join(["'"+rep.name+"'", "'" + phrase.name+"'"]),
                          file=f_representatives)

        # Only representatives to review
        f_review = open(filename_review, 'w')
        print("Representante, Aceptar?", file=f_review)
        for rep in representatives:
            if rep.state is None:
                state = ""
                print(", ".join(["'" + rep.name + "'", state]), file=f_review)

    @classmethod
    def ExportUnreview(cls, representatives, filename):
        f = open(filename, 'w')
        print("Representante, Aceptar?", file=f)
        for rep in representatives:
            print(", ".join(["'" + rep.name + "'"]), file=f)

    @classmethod
    def ExportUnreviewPhrases(cls, representatives, filename):
        f = open(filename, 'w')
        print("Representante, Frase Similar", file=f)
        for rep in representatives:
            for phrase in rep.phrases:
                if rep.state is None or phrase.state is None:
                    print(", ".join(["'"+rep.name+"'",
                                     "'" + phrase.name+"'"]),
                          file=f)

    def set_state(self, state):
        self.state = state
