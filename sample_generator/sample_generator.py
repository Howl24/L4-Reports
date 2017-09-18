from sample_generator.constants import SAMPLE_GENERATOR_TITLE
from dictionary import Dictionary
from dictionary import Phrase
from offer import Offer
import random
import text_processor as tp


DICTIONARY_CHOOSE_MSG = "Escoja el diccionario a utilizar: "
INSERT_MIN_QUANTITY_MSG = "Número mínimo de ocurrencias por palabra: "
SELECT_OFFERS_MSG = ["Seleccione las fuentes a utilizar: ",
                     "(puede seleccionar mas de una)"]
INT_RANGE = (0, None)
SOURCES = ["new_btpucp", "new_bumeran", "new_aptitus"]

READ_MIN_DATE_MSG = "Ingrese el mes y año de inicio"
READ_MAX_DATE_MSG = "Ingrese el mes y año de fin"
MONTH_MSG = "Mes: "
YEAR_MSG = "Año: "
MONTH_RANGE = (1, 12)
YEAR_RANGE = (2010, 2030)

READ_DATE_RANGE_HINT = "(La Fecha de fin debe ser mayor o igual a la de inicio)"



class SampleGenerator:

    def __init__(self, interface, dictionary=None, min_cnt=0, sources=None,
                 offers=[], counter={}):
        self.interface = interface
        self.dictionary = dictionary
        self.min_cnt = min_cnt
        self.offers = offers
        self.counter = counter

    def run(self, export=False, min_cnt=None, sources=None, date_range=None):
        Dictionary.PrepareStatements()
        dictionary_names = Dictionary.GetDictionaryNames()
        dict_name = self.interface.choose_option(dictionary_names,
                                                 DICTIONARY_CHOOSE_MSG)
        self.dictionary = Dictionary.ByName(dict_name)

        if self.min_cnt is None:
            #self.min_cnt = self.interface.read_int(INSERT_MIN_QUANTITY_MSG,
            #                                       INT_RANGE)
            self.min_cnt = 5
        else:
            self.min_cnt = min_cnt

        self.offers = self.read_offers(sources, date_range)
        self.sample = self.create_sample()

        if export:
            filename = self.dictionary.name + "_sample.csv"
            Offer.PrintAsCsv(sample, self.dictionary.configurations, filename)


    def read_offers(self, sources=None, date_range=None):
        if sources is None:
            min_sources = 1
            #sources = self.interface.choose_multiple(SOURCES,
            #                                         SELECT_OFFERS_MSG,
            #                                         min_sources)

            sources = ["new_btpucp"]
        else:
            sources = sources

        if date_range is None:
            #min_date, max_date = self.read_date_range()
            min_date = (1, 2016)
            max_date = (3, 2016)
        else:
            min_date = date_range[0]
            max_date = date_range[1]

        offers = []
        for source in sources:
            offers += Offer.ByDateRange(min_date,
                                        max_date,
                                        source)

        return offers

    def create_sample(self):

        dict_phrases = self.dictionary.accepted_phrases

        # Get only representatives
        representatives = self.dictionary.accepted_reps.values()
        self.initialize_counter(representatives)

        sample_offers = []
        for rep in representatives:
            while not self.check_representative_count(rep.name):
                offer = self.get_random_offer()
                if offer is None:
                    print("No hay suficientes ofertas")
                    break
                if self.update_count(offer, dict_phrases):
                    sample_offers.append(offer)

        return sample_offers

    def initialize_counter(self, representatives):
        for rep in representatives:
            self.counter[rep.name] = 0

    def check_representative_count(self, rep):
        return self.counter[rep] >= self.min_cnt

    def update_count(self, offer, dict_phrases):
        confs_by_source = self.dictionary.confs_by_source
        configuration = confs_by_source[offer.source]

        text = offer.get_text(configuration)
        phrases = Phrase.FromTexts([text], configuration)
        useful_offer = False
        offer_counter = {}

        for phrase in phrases:
            if phrase.name not in dict_phrases:
                continue

            rep_name = dict_phrases[phrase.name].representative
            if rep_name not in self.counter:
                continue

            offer_counter[rep_name] = 1

        if len(offer_counter) > 10:
            # Useful offer
            for rep_name in offer_counter:
                #print(rep_name, end=", ")
                self.counter[rep_name] += 1

            #print()
            return True
        else:
            return False

    def get_random_offer(self):
        if len(self.offers) == 0:
            return None
        else:
            rand = random.randint(0, len(self.offers)-1)
            rand_offer = self.offers[rand]
            self.offers.pop(rand)
            return rand_offer

    def get_random_text(self, text_list):
        if len(text_list) ==  0:
            return None
        else:
            rand = random.randint(0, len(text_list)-1)
            rand_text = text_list[rand]
            text_list.pop(rand)

            return rand_text

    def update_counter(self, text):
        phrases = self.dictionary.get_accepted_phrases()
        for phrase in phrases:
            if self.find_phrase(text) is True:
                self.inc_count(phrase)

    def read_date_range(self):
        msg_list = [MONTH_MSG, YEAR_MSG]
        range_list = [MONTH_RANGE, YEAR_RANGE]

        MONTH = 0
        YEAR = 1
        MONTHS_PER_YEAR = 12

        not_correct_range = True
        show_hint = False
        while(not_correct_range):
            min_date = self.interface.read_int_list(READ_MIN_DATE_MSG,
                                                    msg_list,
                                                    range_list,
                                                    show_hint,
                                                    hint=READ_DATE_RANGE_HINT
                                                    )

            max_date = self.interface.read_int_list(READ_MAX_DATE_MSG,
                                                    msg_list,
                                                    range_list)

            min_date_months = min_date[MONTH] + min_date[YEAR] * MONTHS_PER_YEAR
            max_date_months = max_date[MONTH] + max_date[YEAR] * MONTHS_PER_YEAR

            if max_date_months >= min_date_months:
                not_correct_range = False
            else:
                show_hint = True

        return min_date, max_date
