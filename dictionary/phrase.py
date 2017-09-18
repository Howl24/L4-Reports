#from dictionary import SYMPLICITY_SOURCE
#from dictionary import DICTIONARY_KEYSPACE
from dictionary.constants import *
import text_processor as tp


class Phrase:
    session = None
    insert_stmt = None
    select_stmt = None
    table_name = "dict_phrases"
    keyspace = DICTIONARY_KEYSPACE

    def __init__(self, name, idf, source, state=None, representative=""):
        self.name = name
        self.idf = idf
        self.source = source
        self.state = state
        self.representative = representative

    def set_idf(self, new_idf):
        self.idf = new_idf

    def __eq__(self, other):
        if not isinstance(other, Phrase):
            return False

        if self.name != other.name:
            return False

        return True

    def __hash__(self):
        return hash(self.name)

    def update(self, other):
        if not isinstance(other, Phrase):
            return None

        if self.name != other.name:
            return None

        if other.source != "" and self.source != SYMPLICITY_SOURCE:
            self.source = other.source

        self.idf = other.idf

        if other.state is not None:
            self.state = other.state

        if other.representative != None:
            self.representative = other.representative

    @classmethod
    def FromTexts(cls, texts, configuration):
        vectorizer = tp.build_vectorizer(configuration)

        vectorizer.fit(texts)

        terms = vectorizer.get_feature_names()
        idfs = vectorizer.idf_
        source = configuration.source
            
        phrases = []
        for idx, term in enumerate(terms):
            idf = idfs[idx]
            phrase = Phrase(name=term,
                            idf=idf,
                            source=source)

            phrases.append(phrase)

        return phrases

    @classmethod
    def ConnectToDatabase(cls, cluster=None):
        if cluster is None:
            cluster = Cluster()

        try:
            cls.session = cluster.connect(cls.keyspace)
        except NoHostAvailable:
            raise

        return cluster

    @classmethod
    def CreateTable(cls):
        cmd_create_phrase_table = """
            CREATE TABLE IF NOT EXISTS {0} (
            dict_name        text,
            phrase           text,
            idf              float,
            source           text,
            state            boolean,
            representative   text,
            PRIMARY KEY (dict_name, phrase));
            """.format(cls.table_name)

        cls.session.execute(cmd_create_phrase_table)


    @classmethod
    def PrepareStatements(cls):
        cmd_select = """
                     SELECT * FROM {0} WHERE
                     dict_name = ?; """.format(cls.table_name)

        cmd_insert = """
                     INSERT INTO {0}
                     (dict_name, phrase, idf,
                      source, representative, state)
                     VALUES
                     (?, ?, ?, ?, ?, ?);
                     """.format(cls.table_name)

        cls.insert_stmt = cls.session.prepare(cmd_insert)
        cls.select_stmt = cls.session.prepare(cmd_select)


    def save(self, dict_name):
        """Rename to insert"""
        self.insert(dict_name)

    def insert(self, dict_name):
        self.session.execute(self.insert_stmt, (dict_name,
                                                self.name,
                                                self.idf,
                                                self.source,
                                                self.representative,
                                                self.state))

    @classmethod
    def ByDictName(cls, dictionary_name):
        phrase_rows = cls.session.execute(cls.select_stmt,
                                          (dictionary_name,))

        phrases = []
        for row in phrase_rows:
            name = row.phrase
            idf = row.idf
            source = row.source
            state = row.state
            representative = row.representative
            phrase = Phrase(name,
                            idf,
                            source,
                            state,
                            representative)

            phrases.append(phrase)

        return phrases

    @staticmethod
    def _cmp(a, b):
        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0

    def __cmp__(self, cmp_phrase):
        if self.source == SYMPLICITY_SOURCE:
            if cmp_phrase.source != SYMPLICITY_SOURCE:
                return 1
            else:
                return self._cmp(self.idf, cmp_phrase.idf)
        else:
            if cmp_phrase.source == SYMPLICITY_SOURCE:
                return -1
            else:
                return self._cmp(self.idf, cmp_phrase.idf)

    def __lt__(self, cmp_phrase):
        return self.__cmp__(cmp_phrase) < 0

    def __str__(self):
        return str(self.name) + " " + str(self.idf)

    def set_state(self, state):
        self.state = state

    def add_idf(self, idf):
        self.idf += idf
