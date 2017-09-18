from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable
#from dictionary import DICTIONARY_KEYSPACE
#from dictionary import SYMPLICITY_SOURCE
from dictionary.constants import *

class Configuration:

    insert_stmt = None
    select_stmt = None
    table_name = "dict_configuration"
    session = None
    keyspace = DICTIONARY_KEYSPACE

    def __init__(self, dict_name, source, features, ngrams, dfs):
        self.dict_name = dict_name
        self.source = source
        self.features = features
        self.ngrams = ngrams
        self.dfs = dfs

    def __lt__(self, other):
        return self.source != SYMPLICITY_SOURCE and other.source == SYMPLICITY_SOURCE

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
    def PrepareStatements(cls):
        cmd_insert_conf = """
                          INSERT INTO {0}
                          (dict_name, source, features, ngrams, dfs, last_bow)
                          VALUES
                          (?, ?, ?, ?, ?, ?);
                          """.format(cls.table_name)

        cmd_select_conf = """
                          SELECT * FROM {0} WHERE
                          dict_name = ?;
                          """.format(cls.table_name)

        cls.insert_stmt = cls.session.prepare(cmd_insert_conf)
        cls.select_stmt = cls.session.prepare(cmd_select_conf)

    def save(self):
        self.session.execute(self.insert_stmt,
                             (self.dict_name,
                              self.source,
                              self.features,
                              self.ngrams,
                              self.dfs))

    @classmethod
    def CreateTable(cls):
        cmd_create_configuration_table = """
            CREATE TABLE IF NOT EXISTS {0} (
            dict_name    text,
            source       text,
            features     set<text>,
            ngrams       tuple<int, int>,
            dfs          tuple<double, double>,
            last_bow     tuple<int, int>,
            PRIMARY KEY (dict_name, source));
            """.format(cls.table_name)

        cls.session.execute(cmd_create_configuration_table)

    @classmethod
    def ByDictName(cls, dictionary_name):
        configuration_rows = cls.session.execute(cls.select_stmt,
                                                  (dictionary_name,))

        if not configuration_rows:
            return None
        else:
            configurations = []
            for row in configuration_rows:
                source = row.source
                features = row.features
                ngrams = row.ngrams
                dfs= row.dfs

                conf = cls(dictionary_name, source, features, ngrams, dfs)
                configurations.append(conf)

            return configurations
