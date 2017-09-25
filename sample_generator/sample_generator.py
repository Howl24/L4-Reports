from dictionary import Dictionary
from dictionary import DictionaryManager
from offer import Offer
import random

from utils import read_sources
from utils import read_date_range

from sample_generator.constants import INSERT_MIN_OFFER_CNT_MSG
from sample_generator.constants import MIN_OFFER_CNT_RANGE

from sample_generator.constants import WAIT_MSG_READ_OFFERS
from sample_generator.constants import WAIT_MSG_CREATE_SAMPLE

from sample_generator.constants import MIN_PHRASES_PER_OFFER


class SampleGenerator:

    def __init__(self, interface, dictionary=None,
                 sources=None, offers=[], counter={}):

        self.interface = interface
        self.dictionary = dictionary
        self.min_cnt = None
        self.offers = offers
        self.counter = counter

    def run(self,
            sources=None,
            date_range=None,
            career=None,
            export=False,
            ):

        # Read dictionary
        Dictionary.PrepareStatements()
        if self.dictionary is None:
            dict_manager = DictionaryManager(self.interface)
            self.dictionary = dict_manager.select_old_dictionary()

        if self.min_cnt is None:
            self.min_cnt = self.interface.read_int(INSERT_MIN_OFFER_CNT_MSG,
                                                   MIN_OFFER_CNT_RANGE)

        self.offers = self.interface.wait_function(WAIT_MSG_READ_OFFERS,
                                                   self.read_offers,
                                                   sources,
                                                   date_range,
                                                   career)

        self.sample = self.interface.wait_function(WAIT_MSG_CREATE_SAMPLE,
                                                   self.create_sample)

        if export:
            sample_by_source = {}
            confs_by_source = self.dictionary.configurations_by_source()
            for offer in self.sample:
                if offer.source not in sample_by_source:
                    sample_by_source[offer.source] = []
                sample_by_source[offer.source].append(offer)

            for source, sample in sample_by_source.items():
                filename = self.dictionary.name + "_" + \
                           str(source) + "_sample.csv"

                configuration = confs_by_source[source]

                Offer.PrintAsCsv(sample,
                                 configuration,
                                 filename)

    def read_offers(self, sources=None, date_range=None, career=None):
        if sources is None:
            sources = read_sources(self.interface)

        if date_range is None:
            min_date, max_date = read_date_range(self.interface)
            # min_date = (1, 2016)
            # max_date = (12, 2016)
        else:
            min_date = date_range[0]
            max_date = date_range[1]

        offers = []
        for source in sources:
            offers += Offer.ByDateRange(min_date,
                                        max_date,
                                        source)

        career_filtered = []
        if career is not None:
            for offer in offers:
                if offer.careers is not None:
                    if career in offer.careers:
                        career_filtered.append(offer)

            offers = career_filtered

        print("Read Offers: ", len(offers))

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
                    print("No hay suficientes ofertas para la frase: ",
                          rep.name,
                          self.min_cnt - self.counter[rep.name],
                          " ofertas faltantes.",
                          )
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

        text = offer.get_text(configuration.features)
        phrases = self.dictionary.transform(text, configuration)

        offer_counter = {}

        for phrase in phrases:
            rep_name = phrase.representative
            if rep_name not in self.counter:
                continue

            offer_counter[rep_name] = 1

        if len(offer_counter) >= MIN_PHRASES_PER_OFFER:
            # Useful offer
            for rep_name in offer_counter:
                self.counter[rep_name] += 1

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
