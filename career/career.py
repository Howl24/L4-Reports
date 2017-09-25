from cassandra.cluster import Cluster

GENERAL_KEYSPACE = "general"


class Career:
    session = None
    insert_stmt = None
    select_stmt = None
    table_name = "careers"
    keyspace = GENERAL_KEYSPACE

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Career):
            return False

        if self.name != other.name:
            return False

        return True

    def __hash__(self):
        return hash(self.name)

    def __lt__(self, other):
        return self.name.__lt__(other.name)

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
        cmd_select = """
                     SELECT * FROM {0};
                     """.format(cls.table_name)

        cmd_insert = """
                     INSERT INTO {0}
                     (name)
                     VALUES
                     (?);
                     """.format(cls.table_name)

        cls.select_stmt = cls.session.prepare(cmd_select)
        cls.insert_stmt = cls.session.prepare(cmd_insert)

    @classmethod
    def CreateTables(cls):
        cmd_create_career_table = """
                                  CREATE TABLE IF NOT EXISTS {0} (
                                  name text,
                                  PRIMARY KEY (name));
                                  """.format(cls.table_name)

        cls.session.execute(cmd_create_career_table)

    def insert(self):
        self.session.execute(self.insert_stmt, (self.name, ))

    @classmethod
    def Select(cls):
        result = cls.session.execute(cls.select_stmt, ())

        careers = []
        for row in result:
            career = cls(row.name)
            careers.append(career)

        return careers
