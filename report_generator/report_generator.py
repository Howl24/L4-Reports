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

from utils import read_date_range
from utils import read_sources


CHOOSE_REPORT_MSG = "Seleccione los reportes a generar para : "
ALL_REPORTS = "Todos"
POSITIONS = "Cargos"
DEGREES = "Estudios"
PROFILES = "Perfiles"
CLUSTERS = "Clusters"
PxC = "PerfilesxClusters"

POSITIONS_REP_TITLE = "cargo"
POSITIONS_L4_SLUG = "positions"
POSITIONS_REP_TYPE = "pie"

DEGREES_REP_TITLE = "nivelEstudio"
DEGREES_L4_SLUG = "degrees"
DEGREES_REP_TYPE = "bar"

PROFILES_FIELD = "Áreas de Conocimiento"
PROFILES_L4_SLUG = "software"
PROFILES_REP_TITLE = "Foo"
PROFILES_REP_TYPE = "foo"


REPORTS = [ALL_REPORTS,
           POSITIONS,
           DEGREES,
           PROFILES,
           CLUSTERS,
           PxC,
           ]


class ReportGenerator:

    def __init__(self, interface, career=None, sources=None, date_range=None):
        self.interface = interface
        self.career = career
        self.sources = sources
        self.reports = {}
        self.offers = {}
        self.date_range = date_range

    def run(self):
        Career.ConnectToDatabase()
        Career.PrepareStatements()

        Offer.ConnectToDatabase()

        if self.career is None:
            self.career = self.read_career().name

        if self.sources is None:
            self.sources = read_sources(self.interface)

        self.date_range = read_date_range(self.interface)

        self.reports = {}
        self.offers = {}
        sample_generator = SampleGenerator(self.interface)
        for source in self.sources:
            self.reports[source] = self.read_reports(source)

        for source in self.sources:
            self.offers[source] = sample_generator.read_offers([source],
                                                               self.date_range,
                                                               self.career)

        self.run_reports()

    def read_career(self):
        CHOOSE_CAREER_MSG = "Seleccione la carrera a utilizar:"
        careers = sorted(Career.Select())
                
        career = self.interface.choose_option(careers, CHOOSE_CAREER_MSG)
        return career

    def read_reports(self, source):
        # TODO
        # Replace [1:] in All reports selection


        reports = self.interface.choose_multiple(REPORTS,
                                                 CHOOSE_REPORT_MSG + source)

        if ALL_REPORTS in reports:
            reports = REPORTS[1:]

        return reports

    def run_reports(self):
        # TODO
        # Check reports to know what to process

        N_CHUNKS = 2

        report_types = []
        report_filenames = []
        for source in self.sources:
            offers = self.offers[source]

            # Offer chunks to process
            chunks = self.divide_list(N_CHUNKS, offers)
            l4_count, l4_words = self.processing_offers(chunks, source)

            if POSITIONS in self.reports[source]:
                filename = source + "-" + POSITIONS_REP_TITLE
                self.print_l4_count(l4_count,
                         POSITIONS_L4_SLUG,
                         POSITIONS_REP_TYPE,
                         filename,
                         )

                report_types.append(POSITIONS_REP_TYPE)
                report_filenames.append(filename)

            if DEGREES in self.reports[source]:
                filename = source + "-" + DEGREES_REP_TITLE
                self.print_l4_count(l4_count,
                         DEGREES_L4_SLUG,
                         DEGREES_REP_TYPE,
                         filename,
                         )

                report_types.append(DEGREES_REP_TYPE)
                report_filenames.append(filename)

            if PROFILES in self.reports[source]:
                # divide offer by profile
                offers_by_label = {}
                for offer in offers:
                    if PROFILES_FIELD in offer.features:
                        labels = offer.features[PROFILES_FIELD].split(",")
                        for label in labels:
                            if label not in offers_by_label:
                                offers_by_label[label] = []

                            offers_by_label[label].append(offer)
                    else:
                        print("Algunas ofertas no tienen áreas de conocimiento")
                        return
                                
                filename = source + "-" + PROFILES_REP_TITLE
                words_by_label = {}
                for label, offers in offers_by_label.items():
                    print(label, len(offers), sep=",")
                    label_cnt, label_words = self.processing_offers([offers],
                                                                    source)
                    words_by_label[label] = label_words
                    print(label_words)

                self.print_l4_words(words_by_label, PROFILES_L4_SLUG, filename)

                #report_types.append(PROFILES_REP_TYPE)
                #report_filenames.append(filename)

            if CLUSTERS in self.reports[source]:
                # add cluster reports

                # get offers by id to find them in cluster return
                offers_by_id = {}
                for offer in offers:
                    offers_by_id[offer.id] = offer

                # get offers from cluster
                cluster_ids = self.run_cluster(offers)
                cluster_offers = {}
                for cluster in cluster_ids:
                    cluster_name = "Cluster " + str(cluster + 1)
                    cluster_offers[cluster_name] = []
                    for id in cluster_ids[cluster]:
                        cluster_offers[cluster_name].append(offers_by_id[id])

                for cluster, offers in cluster_offers.items():
                    print(cluster, len(offers))
                    clr_cnt, clr_words = self.processing_offers([offers],
                                                                source)
                    filename = source + "-" + CLUSTER_REP_TITLE
                    self.print_l4(label_cnt, label_words,
                                  CLUSTER_L4_SLUG,
                                  CLUSTER_REP_TYPE,
                                  filename,
                                  )

            if PxC in self.reports[source]:
                pass
                # add profiles x clusters

        print(report_types)
        print(report_filenames)
        export_ppt(report_types, report_filenames)
            
    def run_cluster(self, offers):
        features = []
        ids = []
        for offer in offers:
            features.append(offer.features)
            ids.append(offer.id)

        cluster_offers = get_ids_by_features(features, ids, self.career)
        return cluster_offers

    def processing_offers(self, chunks, source):
        # TODO
        # Move logic to processor package
        q_l4_count = multiprocessing.Queue()
        q_l4_words = multiprocessing.Queue()
        q_offers = multiprocessing.Queue()

        n_jobs = len(chunks)
        jobs = []
        for i in range(n_jobs):
            offers = list(chunks[i])
            outfile = "Outs/ofertas_" + source + "_" + str(i+1) + ".csv"

            p = multiprocessing.Process(target=self.process,
                                        args=(offers,
                                        q_l4_count,
                                        q_l4_words,
                                        source,
                                        outfile
                                        ))

            jobs.append(p)
            p.start()

        #Rendezvous
        for idx, proc in enumerate(jobs):
            proc.join()

        #L4 counter merge & print
        l4_count_1 = q_l4_count.get()
        l4_words_1 = q_l4_words.get()
        for i in range(n_jobs-1):
            l4_count_2 = q_l4_count.get()
            l4_words_2 = q_l4_words.get()

            l4_count_1 = self.pass_count(l4_count_1, l4_count_2)
            l4_words_1 = self.pass_words(l4_words_1, l4_words_2)

        return l4_count_1, l4_words_1

    def print_l4_count(self, l4_count,
                       rep_slug, rep_type, filename):

        f = open(filename, 'w')
        if rep_type in ["pie", "bar"]:
            print(rep_slug, "nro cov", sep=", ", file=f)
            for skill in l4_count[rep_slug]:
                print(skill, l4_count[rep_slug][skill], file=f, sep=", ")

        f.close()

    def print_l4_words(self, l4_words_by_label, rep_slug, filename):
        f = open(filename, "w")

        print("Area", rep_slug, sep=", ", file=f)
        for label, l4_words in l4_words_by_label.items():
            skills = l4_words[rep_slug]
            for skill in skills:
                print(label,skill, sep=", ", file=f)

        f.close()

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
        for field in l4_words_2:
            if field not in l4_words_1:
                l4_words_1[field] = l4_words_2[field]
            else:
                for skill in l4_words_2[field]:
                    # Set can override a repeated skill
                    l4_words_1[field].add(skill)

        return l4_words_1

    def process(self, offers, q_l4_cnt, q_l4_words, source, outfile):
        proc_filename = "proc_" + source
        processor = Processor(proc_filename)
        processor.connect_to_database()
        processor.read_configuration()
        processor.get_dictionaries()
        proc_offers = processor.process_offers(offers, outfile)

        q_l4_cnt.put(self.l4_count(proc_offers))
        q_l4_words.put(self.l4_words(proc_offers))

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
