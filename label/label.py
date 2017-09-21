GENERAL_KEYSPACE = "general"
from cassandra.cluster import Cluster

class Label:
    session = None
    insert_stmt = None
    select_stmt = None
    table_name = "career_labels"
    keyspace = GENERAL_KEYSPACE

    def __init__(self, career, field, name):
        self.career = career
        self.field = field
        self.name = name

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
    def CreateTables(cls):
        cmd_create_label_table = """
            CREATE TABLE IF NOT EXISTS {0} (
            career          text,
            field           text,
            label           text,
            PRIMARY KEY (career, field, label));
        """.format(cls.table_name)

        cls.session.execute(cmd_create_label_table)

    @classmethod
    def PrepareStatements(cls):
        cmd_select = """
                     SELECT * FROM {0} WHERE
                     career = ?; """.format(cls.table_name)

        cmd_insert = """
                     INSERT INTO {0}
                     (career, field, label)
                     VALUES
                     (?, ?, ?);
                     """.format(cls.table_name)

        cls.insert_stmt = cls.session.prepare(cmd_insert)
        cls.select_stmt = cls.session.prepare(cmd_select)

    @classmethod
    def Insert(cls, career, field, label):
        """ From outside class instance usage
            Example: Insert(career, field, label)
        """
        self.session.execute(cls.insert_stmt, (career,
                                               field,
                                               label,))

    def insert(self):
        """ label.insert() """
        self.session.execute(self.insert_stmt, (self.career,
                                                self.field,
                                                self.name))

    @classmethod
    def Select(cls, career):
        # TODO 
        # Replace by class label return dictionary
        """ Return all career labels keyed by field"""

        labels_by_field = {}
        result = cls.session.execute(cls.select_stmt, (career,))
        for row in result:
            career = row.career
            field = row.field
            label_name = row.label

            if field not in labels_by_field:
                labels_by_field[field] = []
                    
            labels_by_field[field].append(label_name)
            #label = Label(career, field, label_name)
            #labels.append(label)

        return labels_by_field
