from career import Career
from dictionary import DictionaryManager
from sample_generator import SampleGenerator
from offer import Offer
from dictionary import Dictionary

import multiprocessing
from processor.control import Processor

from powerpointBTPUCP import export_ppt

# Cluster
from Clustering.Clustering import get_ids_by_features


class ReportGenerator:

    def __init__(self, interface, career=None, sources=None):
        self.interface = interface
        self.career = career
        self.sources = sources
        self.reports = {}
        self.offers = {}


    def run(self):
        Career.ConnectToDatabase()
        Career.PrepareStatements()

        Offer.ConnectToDatabase()

        # Test
        self.career = "ECONOMÍA"
        self.date_range = ((1,2016), (1, 2017))
        self.sources = ["new_btpucp"]

        #if self.career is None:
        #    self.career = self.read_career()

        sample_generator = SampleGenerator(self.interface)
        #date_range = sample_generator.read_date_range()

        #if self.sources is None:
        #    dict_manager = DictionaryManager(self.interface)
        #    self.sources = dict_manager.read_keyspaces()

        self.reports = {}
        self.offers = {}
        for source in self.sources:
            self.reports[source] = self.read_reports(source)
            self.offers[source] = sample_generator.read_offers([source],
                                                               self.date_range,
                                                               self.career)

        self.run_reports()

    def read_career(self):
        CHOOSE_CAREER_MSG = "Seleccione la carrera a clasificar:"
        careers = sorted(Career.Select())
                
        career = self.interface.choose_option(careers, CHOOSE_CAREER_MSG)
        return career.name

    def read_reports(self, source):
        CHOOSE_REPORT_MSG = "Seleccione el reporte a generar para la fuente: "
        ALL_REPORTS = "Todos"
        REPORTS = [ALL_REPORTS,
                   'Cargos',
                   'Estudios',
                   'Idiomas']

        chosen_reports = self.interface.choose_multiple(REPORTS,
                                                        CHOOSE_REPORT_MSG + source)

        if ALL_REPORTS in chosen_reports:
            chosen_reports = REPORTS[1:]

        return chosen_reports

    def run_reports(self):
        # TODO
        # Check reports to know what to process


        N_CHUNKS = 2

        for source in self.sources:
            offers = self.offers[source]
            
            offers_by_id = {}
            for offer in offers:
                offers_by_id[offer.id] = offer

            cluster_ids = self.run_cluster(offers)
            cluster_offers = {}
            for cluster in cluster_ids:
                cluster_name = "Cluster " + str(cluster + 1)
                cluster_offers[cluster_name] = []
                for id in cluster_ids[cluster]:
                    cluster_offers[cluster_name].append(offers_by_id[id])

            chunks = self.divide_list(N_CHUNKS, offers)
            Dictionary.free(offers)

            self.multi_processing(chunks, source)

    def run_cluster(self, offers):
        features = []
        ids = []
        for offer in offers:
            features.append(offer.features)
            ids.append(offer.id)

        cluster_offers = get_ids_by_features(features, ids, self.career)
        return cluster_offers

    def multi_processing(self, chunks, source):
        # TODO
        # Move logic to processor package
        q_l4 = multiprocessing.Queue()
        q_offers = multiprocessing.Queue()

        n_jobs = len(chunks)
        jobs = []
        for i in range(n_jobs):
            offers = list(chunks[i])
            outfile = "Outs/ofertas_" + source + "_" + str(i+1) + ".csv"

            p = multiprocessing.Process(target=self.process,
                                        args=(offers,
                                        q_l4,
                                        source,
                                        outfile
                                        ))

            jobs.append(p)
            p.start()

        #Rendezvous
        for idx, proc in enumerate(jobs):
            proc.join()

        #L4 counter merge & print
        l4_count_1 = q_l4.get()
        l4_word_1 = q_l4.get()
        for i in range(n_jobs-1):
            l4_count_2 = q_l4.get()
            l4_word_2 = q_l4.get()

            l4_count_1 = self.pass_count(l4_count_1, l4_count_2)
            l4_word_1 = self.pass_words(l4_word_1, l4_word_2)

        self.print_l4(l4_count_1, l4_word_1, source)

    def print_l4(self, l4_count, l4_word, source):
        reports = []
        for report in self.reports[source]:
            if report == "Cargos":
                field = "positions"
                filename = source + "-" + "cargo.csv"
                rep_type = "pie"

            if report == "Estudios":
                field = "degrees"
                filename = source + "-" + "nivelEstudio.csv"
                rep_type = "pie"

            if report == "Idiomas":
                field = "languages"
                filename = source + "-" + "idiomas.csv"
                rep_type = "pie"

            reports.append((field, filename, rep_type))

        rep_types = []
        filenames = []
        for (field, filename, rep_type) in reports:
            rep_types.append(rep_type)
            filenames.append(filename)

            f = open(filename, "w")
            if rep_type in ["pie", "bar"]:
                print(field, ", nro conv", file=f)

                for skill in l4_count[field]:
                    print(skill, l4_count[field][skill], file=f, sep=", ")

            f.close()

        print(rep_types)
        print(filenames)
        export_ppt(rep_types, filenames)

    def pass_count(self, l4_count_1, l4_count_2):
        for field in l4_count_2:
            if field not in l4_count_1:
                l4_count_1[field] = l4_count_2[field]
            else:
                for skill in l4_count_2[field]:
                    if skill not in l4_count_1[field]:
                        l4_count_1[field][skill] = l4_count_2[field][skill]
                    else:
                        l4_count_1[field][skill] += l4_count_2[field][skill]

        return l4_count_1

    def pass_words(self, l4_words_1, l4_words_2):
        return l4_words_1
        pass

    def process(self, offers, q_l4, source, outfile):
        proc_filename = "proc_" + source
        processor = Processor(proc_filename)
        processor.connect_to_database()
        processor.read_configuration()
        processor.get_dictionaries()
        proc_offers = processor.process_offers(offers, outfile)

        q_l4.put(self.l4_count(proc_offers))
        q_l4.put(self.l4_words(proc_offers))

    def l4_count(self, proc_offers):
        l4_count = {}
        for offer in proc_offers:
            for field in offer.skills:
                if field not in l4_count:
                    l4_count[field] = {}

                for skill in offer.skills[field]:
                    if skill not in l4_count[field]:
                        l4_count[field][skill] = 0

                    l4_count[field][skill] += 1

        return l4_count

    def l4_words(self, proc_offers):
        l4_words = {}
        for offer in proc_offers:
            for field in offer.skills:
                if field not in l4_words:
                    l4_words[field] = set()

                for skill in offer.skills[field]:
                    l4_words[field].add(skill)

        return l4_words
	
    def divide_list(self, n_chunks, list_to_divide):
        # TODO
        # Move to utils file
        chunk_size = len(list_to_divide)//n_chunks + 1
        chunks = [list_to_divide[i:i+chunk_size] for i in range(0, len(list_to_divide), chunk_size)]

        return chunks
