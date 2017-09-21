import sys
from cassandra.cluster import Cluster
sys.path.append("..")
from processor import Const
#from utils import Const
from processor import utils
#import utils

class Dictionary:
    session = None

    def __init__(self, title = "", phrases = [], similars_stem = {}, similars_no_stem = {}):
        self.title = title
        self.phrases = phrases
        self.similars_stem = similars_stem
        self.similars_no_stem = similars_no_stem

    @classmethod
    def connectToDatabase(cls, keyspace = 'general'):
        cluster = Cluster()
        cls.session = cluster.connect(keyspace)
        
    @classmethod
    def fromFile(cls, filename):
        errFormat = "Error en la lectura del archivo. Formato incorrecto"

        phrases = []
        similars_stem = {}
        similars_no_stem = {}
        with open(filename, 'r') as file:
            title = utils.clear_spaces(file.readline())
            try:
                num_phrases = int(file.readline())
            except:
                print(errFormat)
                return Const.FAIL

            for i in range(num_phrases):
                phrase = utils.clear_spaces(file.readline())
                phrases.append(phrase)
                similars_stem[phrase] = []
                similars_no_stem[phrase] = []

                try:
                    num_similars_stem = int(file.readline())
                except:
                    print(errFormat)
                    return Const.FAIL

                for j in range(num_similars_stem):
                    similar_stem = utils.clear_spaces(file.readline())
                    similars_stem[phrase].append(similar_stem)

                try:
                    num_similars_no_stem = int(file.readline())
                except:
                    print(errFormat)
                    return Const.FAIL

                for j in range(num_similars_no_stem):
                    similar_no_stem = utils.clear_spaces(file.readline())
                    similars_no_stem[phrase].append(similar_no_stem)

        return cls(title, phrases, similars_stem, similars_no_stem)

    
    @classmethod
    def fromCassandra(cls, title):
        errLoad = "Error al cargar el diccionario desde Cassandra"

        cmd = """
              SELECT * FROM dictionaries WHERE title = %s;
              """
        rows = cls.session.execute(cmd, [title])
        try:
            pass
        except:
            print(errLoad)
            return Const.FAIL

        rows = list(rows)
        if (len(rows) == 0):
            print('Empty')
            return Const.FAIL

        phrases = []
        similars_stem = {}
        similars_no_stem = {}
        for row in rows:
            phrases.append(row.phrase) #cambiar por phrase
            if row.similars_stem is None:
                similars_stem[row.phrase] = []
            else:
                similars_stem[row.phrase] = row.similars_stem

            if row.similars_no_stem is None:
                similars_no_stem[row.phrase] = []
            else:
                similars_no_stem[row.phrase] = row.similars_no_stem
            
        return cls(title, phrases, similars_stem, similars_no_stem)

    @classmethod
    def createTable(cls):
        cmd = """
              CREATE TABLE IF NOT EXISTS dictionaries (
              title text,
              phrase text,
              similars_stem list<text>,
              similars_no_stem list<text>,
              PRIMARY KEY (title, phrase));
              """

        try:
            cls.session.execute(cmd)
        except:
            print("Error al crear la tabla de diccionarios")
            return Const.FAIL

        return Const.DONE

    def insert(self):
        cmd = """
              INSERT INTO dictionaries
              (title, phrase, similars_stem, similars_no_stem)
              VALUES
              (%s,%s,%s,%s);
              """

        for phrase in self.phrases:
            self.session.execute(cmd, [self.title, phrase,
                                       self.similars_stem[phrase], self.similars_no_stem[phrase]])

    
    def is_empty(self):
        if self.title == "" or self.phrases == []:
            return True
        else:
            return False

    def process_similars(self):
        for phrase in self.phrases:
            for i, similar in enumerate(self.similars_stem[phrase]):
                self.similars_stem[phrase][i] = ""
                for word in similar.split(): #A similar can be a phrase
                    if not word in Const.STOP_WORDS:
                        self.similars_stem[phrase][i] += word + ' '
                self.similars_stem[phrase][i] = utils.clear_spaces(self.similars_stem[phrase][i])

            for i, similar in enumerate(self.similars_no_stem[phrase]):
                self.similars_no_stem[phrase][i] = ""
                for word in similar.split():
                    if not word in Const.STOP_WORDS:
                        self.similars_no_stem[phrase][i] += word + ' '
                self.similars_no_stem[phrase][i] = utils.clear_spaces(self.similars_no_stem[phrase][i])


def main():
    Dictionary.connectToDatabase()
    Dictionary.createTable()
    path = "../Dictionaries/"
    #filelist = ['positions','competences','degrees','languages','responsibilities','software','l4_careers']

    # Custom careers
    #filelist = ['positions','competences','ordered_degrees','languages','responsibilities','software','careers_fast']
    #filelist = ['careers_roy']

    filelist = [
            'positions',
            'ordered_degrees',
            'languages',
            'l4_careers',
            'software',
            'competences',
            ]

    #filelist = [
    #        'positions',
    #        'ordered_degrees',
    #        'languages',
    #        'software',
    #        'careers_melissa',
    #        ]

    for file in filelist:
        print(file)
        dic = Dictionary.fromFile(path+file)
        dic.insert()
    
    
if __name__ == "__main__":
    main()
