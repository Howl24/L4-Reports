from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable
from cassandra import InvalidRequest
from offer import Offer
from dictionary import Representative
from dictionary import Phrase
from dictionary import Configuration

from dictionary.constants import DICTIONARY_KEYSPACE
from dictionary.constants import SUCCESSFUL_OPERATION
from dictionary.constants import UNSUCCESSFUL_OPERATION

import text_processor as tp
import gensim
import gc

"""
This class contains methods to manipulate dictionary information and
database structure.
"""


class Dictionary:
    # TODO
    # Update configuration:

    session = None
    keyspace = DICTIONARY_KEYSPACE
    conf_table_name = Configuration.table_name
    phrase_table_name = Phrase.table_name
    tmp_phrase_table_name = "dict_temp_phrases"
    delete_stmt = None
    select_representative_stmt = None
    insert_tmp_stmt = None
    select_tmp_stmt = None
    select_all_tmp_stmt = None

    def __init__(self,
                 name,
                 configurations=[],
                 representatives=[],
                 last_bow=(0, 0),
                 sources=[]):

        self.name = name
        self.configurations = configurations
        self.representatives = representatives
        self.last_bow = last_bow
        self.sources = sources

        self.accepted_reps = self.get_representatives(state=True)
        self.rejected_reps = self.get_representatives(state=False)

        self.accepted_phrases = self.get_phrases(state=True)
        self.rejected_phrases = self.get_phrases(state=False)

        self.phrases = self.get_all_phrases()

        self.confs_by_source = self.configurations_by_source()

    def configurations_by_source(self):
        confs_by_source = {}
        for conf in self.configurations:
            confs_by_source[conf.source] = conf

        return confs_by_source

    def get_representatives(self, state):
        """
        Return representatives with the same state and keyed by rep_name
        state values:
            - True
            - False
            - None (not assigned state)
        """
        selected_reps = {}
        for rep in self.representatives:
            if rep.state == state:
                selected_reps[rep.name] = rep

        return selected_reps

    def get_phrases(self, state):
        """
        Return phrases with the same representative state
        and keyed by phrase_name
        state values:
            - True
            - False
            - None (not assigned state)
        """

        selected_phrases = {}
        for rep in self.representatives:
            if rep.state == state:
                for phrase in rep.phrases:
                    selected_phrases[phrase.name] = phrase

        return selected_phrases

    def get_all_phrases(self):
        """
        Similar to get_phrases with state = True, False and None
        but faster.
        """

        phrases = {}
        for rep in self.representatives:
            for phrase in rep.phrases:
                phrases[phrase.name] = phrase

        return phrases

    def __str__(self):
        txt = ""
        txt += "Accepted: " + '\n'
        for rep in self.accepted:
            txt += str(self.accepted[rep]) + "\n"

        txt += "Rejected: " + '\n'
        for rep in self.rejected:
            txt += str(self.rejected[rep]) + "\n"

        return txt

    @classmethod
    def ConnectToDatabase(cls, cluster=None):
        if cluster is None:
            cluster = Cluster()

        try:
            cls.session = cluster.connect(cls.keyspace)
        except NoHostAvailable:
            raise

        Configuration.ConnectToDatabase(cluster)
        Phrase.ConnectToDatabase(cluster)
        return cluster

    @classmethod
    def GetDictionaryNames(cls):
        cmd = """
              SELECT DISTINCT dict_name FROM {0};
              """.format(cls.conf_table_name)

        result = cls.session.execute(cmd)
        dict_names = [x.dict_name for x in result]
        return dict_names

    @classmethod
    def PrepareStatements(cls):
        Configuration.PrepareStatements()
        Phrase.PrepareStatements()

        cmd_insert_tmp = """
                         INSERT INTO {0}
                         (dict_name, phrase, quantity,
                          source, representative, state)
                         VALUES
                         (?, ?, ?, ?, ?, ?);
                         """.format(cls.tmp_phrase_table_name)

        cmd_select_tmp = """
                         SELECT * FROM {0} WHERE
                         dict_name = ? AND
                         phrase = ?;
                         """.format(cls.tmp_phrase_table_name)

        cmd_select_all_tmp = """
                             SELECT * FROM {0} WHERE
                             dict_name = ?;
                             """.format(cls.tmp_phrase_table_name)

        cls.insert_tmp_stmt = cls.session.prepare(cmd_insert_tmp)
        cls.select_tmp_stmt = cls.session.prepare(cmd_select_tmp)
        cls.select_all_tmp_stmt = cls.session.prepare(cmd_select_all_tmp)

        try:
            pass
        except InvalidRequest:
            print("Tabla no configurada.")
            print("Utilice la funcion CreateTable para crear una tabla")
            print()
            return UNSUCCESSFUL_OPERATION

        return SUCCESSFUL_OPERATION

    @classmethod
    def CreateTables(cls):
        Configuration.CreateTable()
        Phrase.CreateTable()

        cmd_create_tmp_phrase_table = """
            CREATE TABLE IF NOT EXISTS {0} (
            dict_name            text,
            phrase          text,
            quantity        int,
            source          text,
            state           boolean,
            representative  text,
            PRIMARY KEY (dict_name, phrase));
            """.format(cls.tmp_phrase_table_name)

        cls.session.execute(cmd_create_tmp_phrase_table)

        print("Las tablas de diccionarios se crearon correctamente")
        return SUCCESSFUL_OPERATION

    @classmethod
    def ByName(cls, dictionary_name):
        """Return a dictionary from database"""

        configurations = Configuration.ByDictName(dictionary_name)
        if not configurations:
            return None
        else:
            representatives = Representative.ByDictName(dictionary_name)
            return Dictionary(dictionary_name,
                              configurations,
                              representatives)

    @classmethod
    def New(cls, dictionary_name):
        name = dictionary_name
        return cls(name)

    @classmethod
    def ByCassandraRows(cls, dictionary_name, configuration_rows, phrase_rows):
        dict = Dictionary(dictionary_name)

        # Add dictionary configuration
        for row in configuration_rows:
            source = row.source
            features = row.features
            ngrams = row.ngrams
            dfs = row.dfs
            last_bow = row.last_bow
            dict.add_configuration(source,
                                   features,
                                   ngrams,
                                   dfs,
                                   last_bow)

        # Add dictionary phrases
        for row in phrase_rows:
            phrase = row.phrase
            quantity = row.quantity
            source = row.source
            representative = row.representative
            state = row.state
            dict.add_phrase(phrase, quantity, source,
                            representative, state)

        return dict

    @classmethod
    def SetInterface(self, interface):
        self.interface = interface

    def add_configuration(self, configuration):
        self.configurations.append(configuration)

    def add_phrase(self, name, quantity, source, rep_name, state):
        # TODO
        # Add unreview representatives (state = None)
        # Validate different representatives states (in different phrases)
        # Modify dictionary class structure to get unique representatives.
        #   reps = {} <- Reps by name
        #   accepted & rejected = [] <- Pointers to reps
        # Explicitly sending an empty phrase list
        #  (Remove after import-bow bug fix).
        #   Representative(representative_name, state, [] <--)

        if state is True:
            if rep_name not in self.accepted:
                self.accepted[rep_name] = Representative(rep_name,
                                                         state, [])

            self.accepted[rep_name].add_phrase(name, quantity,
                                               source, state)

        if state is False:
            if rep_name not in self.rejected:
                self.rejected[rep_name] = Representative(rep_name,
                                                         state, [])

            self.rejected[rep_name].add_phrase(name, quantity,
                                               source, state)

    def save_configuration(self):
        for configuration in self.configurations:
            configuration.save()

    # -------------------------------------------------------------------------

    @staticmethod
    def free(some_list):
        del some_list[:]
        gc.collect()

    def update_phrases_frecuency(self):

        # Put Symplicity configuration at the top of the list
        self.configurations.sort()

        for configuration in self.configurations:

            # Check if configuration source was selected
            if configuration.source not in self.sources:
                continue

            offers = Offer.FromConfiguration(configuration)

            texts = [offer.get_text(configuration.features)
                     for offer in offers]
            self.free(offers)

            read_phrases = Phrase.FromTexts(texts, configuration)
            self.free(texts)

            # Update phrases info
            for phrase in read_phrases:
                if phrase.name in self.phrases:
                    # Phrase already in dictionary.
                    # Update values
                    self.phrases[phrase.name].update(phrase)
                else:
                    # Add phrase to dictionary
                    self.phrases[phrase.name] = phrase

        # Save and update idf phrases
        for phrase in self.phrases.values():
            phrase.save(self.name)

    def build_representatives(self):
        phrases_list = list(self.phrases.values())
        self.representatives = Representative.FromPhrases(phrases_list)

    def export_unreview_phrases(self):
        filename = self.name + "_similares" + ".csv"
        Representative.ExportUnreviewPhrases(self.representatives, filename)

    def export_unreview_representatives(self):
        filename = self.name + "_revisión" + ".csv"
        Representative.ExportUnreview(self.representatives, filename)

    # -------------------------------------------------------------------------

    def get_word2vec(self):
        model = gensim.models.Word2Vec.load('w2v/model')
        return model

    def all_phrases(self):
        phrases = []
        for phrase in self.accepted_phrases:
            phrases.append(phrase.phrase)

        for phrase in self.rejected_phrases:
            phrases.append(phrase.phrase)

        return phrases


    # ------------------------------------------------------------------------
    def transform(self, text, configuration):
        """ Conver a text to a phrase list that contains the dictionary 
        accepted phrases that are found in the text"""

        vocab = [phrase.name for phrase in self.accepted_phrases.values()]
        vectorizer = tp.build_vectorizer(configuration, min_df=0)

        vectorizer.fit([text])
        terms = vectorizer.get_feature_names()

        filter_phrases = [self.accepted_phrases[term]
                          for term in terms if term in vocab]
        return filter_phrases
