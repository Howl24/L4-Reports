from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable
from cassandra import InvalidRequest
from cassandra.query import BoundStatement
from dictionary.constants import *

class Offer:
    session = None
    keyspace = ""
    offers_table = "new_offers"
    select_stmt = None
    select_all_stmt = None

    def __init__(self, year=0, month=0, id="",
                 features={}, careers=set(), skills={},
                 source=""):
        self.year = year
        self.month = month
        self.id = id
        self.features = features
        self.careers = careers
        self.skills = skills
        self.source = source

    @classmethod
    def ConnectToDatabase(cls, cluster=None):
        if not cluster:
            cluster = Cluster()

        try:
            cls.session = cluster.connect(cls.keyspace)
        except NoHostAvailable as e:
            print("Ningun servicio de cassandra esta disponible.")
            print("Inicie un servicio con el comando " +
                  "\"sudo cassandra -R \"")
            print()
            return UNSUCCESSFUL_OPERATION

        return SUCCESSFUL_OPERATION

    @classmethod
    def SetKeyspace(cls, keyspace):
        cls.keyspace = keyspace
        try:
            cls.session.set_keyspace(cls.keyspace)
        except InvalidRequest:
            print("El keyspace no existe")
            print()
            return UNSUCCESSFUL_OPERATION

        cls.PrepareStatements()
        return SUCCESSFUL_OPERATION

    @classmethod
    def PrepareStatements(cls, keyspace=None):
        if keyspace:
            if cls.SetKeyspace(keyspace) == UNSUCCESSFUL_OPERATION:
                return UNSUCCESSFUL_OPERATION

        cmd_select = """
                     SELECT * FROM {0} WHERE
                     year = ? AND
                     month = ? AND
                     id = ?;
                     """.format(cls.offers_table)

        cmd_select_all = """
                         SELECT * FROM {0}
                         """.format(cls.offers_table)

        try:
            cls.select_stmt = cls.session.prepare(cmd_select)
            prepared_stmt = cls.session.prepare(cmd_select_all)
            cls.select_all_stmt = BoundStatement(prepared_stmt, fetch_size=10)
        except InvalidRequest:
            print("Tabla no configurada")
            raise
            return UNSUCCESSFUL_OPERATION

        return SUCCESSFUL_OPERATION

    @classmethod
    def Select(cls, year, month, id, source):
        rows = cls.session.execute(cls.select_stmt,
                                   (year, month, id))

        if not rows:
            return None
        else:
            return Offer.ByCassandraRow(rows[0], source)

    @classmethod
    def ByCassandraRow(cls, row, source):
        return cls(row.year, row.month, row.id, row.careers, row.features,
                   source=source)

    @classmethod
    def SelectAll(cls, source):
        cls.SetKeyspace(source)
        rows = cls.session.execute(cls.select_all_stmt)

        if not rows:
            return None
        else:
            return cls.ByCassandraRows(rows, source)

    @classmethod
    def SelectSince(cls, source, date):
        year = date[0]
        month = date[1]
        cls.SetKeyspace(source)
        rows = cls.session.execute(cls.select_all_stmt)

        if not rows:
            return None
        else:
            selected_rows = []
            for row in rows:
                if (row.year > year) or \
                   ((row.year == year) and (row.month >= month)):
                    selected_rows.append(row)

            return cls.ByCassandraRows(selected_rows, source)

    @classmethod
    def ByDateRange(cls, min_date, max_date, source):
        cls.SetKeyspace(source)
        rows = cls.session.execute(cls.select_all_stmt)

        if not rows:
            return None

        else:
            selected_rows = []
            for row in rows:
                offer_month = row.month
                offer_year = row.year
                offer_date = (offer_month, offer_year)
                if cls._check_date_range(offer_date, min_date, max_date):
                    selected_rows.append(row)

            return cls.ByCassandraRows(selected_rows, source)

    @staticmethod
    def _check_date_range(offer_date, min_date, max_date):
        # TODO
        # Replace date by a class

        MONTH = 0
        YEAR = 1
        MONTHS_PER_YEAR = 12

        offer_months = offer_date[MONTH] + offer_date[YEAR] * MONTHS_PER_YEAR
        min_date_months = min_date[MONTH] + min_date[YEAR] * MONTHS_PER_YEAR
        max_date_months = max_date[MONTH] + max_date[YEAR] * MONTHS_PER_YEAR

        if offer_months >= min_date_months and offer_months <= max_date_months:
            return True
        else:
            return False

    @classmethod
    def ByCassandraRows(cls, rows, source):
        offers = []
        for row in rows:
            offer = cls(row.year, row.month, row.id, row.features, row.careers,
                        source=source)
            offers.append(offer)

        return offers

    def get_text(self, feature_list, delimiter=" "):
        """
        Get offer text from feature list.
        concatenated by delimiter
        """

        text = ""
        for feature in feature_list:
            if feature in self.features:
                text += self.features[feature] + delimiter

        return text

    @classmethod
    def FromConfiguration(cls, configuration):
        # TODO 
        # Include filters in configuration

        # Career and date range filter 
        filter_career = "ECONOMÍA"
        filter_min_date = (3, 2016)
        filter_max_date = (6, 2016)

        # All offers - No filter purpose
        #offers = Offer.SelectAll(configuration.source)

        # Filter offers by date range
        offers = Offer.ByDateRange(filter_min_date,
                                   filter_max_date,
                                   configuration.source)

        filtered_offers = []
        for offer in offers:
            # Filter offers by career
            offer_careers = [career.strip() for career in offer.features['Majors/Concentrations'].split(",")]
            offer_month = offer.month
            offer_year = offer.year

            if filter_career in offer_careers:
                filtered_offers.append(offer)

        offers = filtered_offers
        return offers
