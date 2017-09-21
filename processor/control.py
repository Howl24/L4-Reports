import sys
from processor import Const
from cassandra.cluster import Cluster
import re
from nltk.stem.snowball import SpanishStemmer
from nltk.corpus import stopwords

from processor import Offer
from processor import Dictionary

import multiprocessing

from processor import textProcessor as tp

feature_list_1 = [
        'NombreAviso',
        'FuncionesResponsabilidades',
        'Requerimientos',
        'estudios',
        'cargos',
        'carreras',
        'Empresa',
        'salario',
        ]

feature_list_2 = [
        'título',
        'descripción',
        'requisitos',
        'estudios',
        'cargos',
        'carreras',
        'Empresa',
        'salario',
        ]

feature_list_symplicity = [
        'Job Title',
        'Description',
        'Qualifications',
        'Majors/Concentrations',
        'Degree Level',
        'Position Level',
        'Position Type',
        'Employer',
        'Organization Name',
        'Software',
        'Salario (S/.)',
        'estudios',
        'cargos',
        'carreras',
        ]

class Processor:

    STOP_WORDS = stopwords.words('english') + stopwords.words('spanish')
    STEMMER = SpanishStemmer()
    CAREERS = 'careers'

    FILE = 'File'
    DATE = 'Date'
    NOT_FOUND = 'otros/no-menciona'

    COPY_VALUE_PROCESSING_CODE = 1
    FIND_WORDS_PROCESSING_CODE = 2
    FIND_PRIORITY_PHRASE_PROCESSING_CODE = 3
    CAREERS_PROCESSING_CODE = 4

    CNT_CAREERS = 0

    PUNCTUATIONS = '!"#$%&\'()*+,-./:;<=>?[\\]^_`{|}~'  # @ not included (@risk)

    N_PROCESS = 2

    def __init__(self, config_filename='config.hwl', reprocess=True):
        self.reprocess = reprocess
        self.config_filename = config_filename
        self.config_features = {}
        self.keyspace = ""
        self.num_offers = 0
        self.chunks = []
        self.dictionaries = {}
        self.session = None
        self.fields = []

    @staticmethod
    def getNumber(file):
        try:
            number = int(file.readline())
        except:
            return Const.FAIL
        return number

    def read_configuration(self):
        with open(self.config_filename, 'r') as file:
            self.keyspace = file.readline().strip()
            careers = file.readline().strip()
            if careers != Processor.CAREERS:
                return Const.FAIL

            career_features = self.read_configuration_features(file)
            if career_features is Const.FAIL:
                print("No se encontraron caracteristicas para obtener las carreras")
                return Const.FAIL
            self.config_features[Processor.CAREERS] = career_features

            for field in file:
                field = field.strip()
                self.fields.append(field)
                features = self.read_configuration_features(file)
                if features is Const.FAIL:
                    return Const.FAIL
                self.config_features[field] = features

        return Const.DONE

    def get_dictionaries(self):
        self.dictionaries = {}

        #self.dictionaries[Processor.CAREERS] = Dictionary.fromFile('Dictionaries/careers_roy')
        self.dictionaries[Processor.CAREERS] = Dictionary.fromCassandra('careers')
        if self.dictionaries[Processor.CAREERS].is_empty():
            print("El Diccionario de carreras no ha sido encontrado.")
            return Const.FAIL

        for field in self.fields:
            if self.config_features[field][0] != 1:
                self.dictionaries[field] = Dictionary.fromCassandra(field.lower())
                if self.dictionaries[field].is_empty():
                    print("Diccionario no encontrado. Revise el nombre del campo ", field,
                          " y que el diccionario exista en la base de datos")
                else:
                    self.dictionaries[field].process_similars()

        # careers
        self.dictionaries['find_careers'] = ['universitario', 'bachiller', 'titulado']
        self.dictionaries['ends'] = ['.']

        return Const.DONE


    def connect_to_database(self):
        cluster = Cluster()
        self.session = cluster.connect('general')  # Review try catch

        Dictionary.connectToDatabase()
        #Offer.connectToDatabase(self.keyspace)
        #Offer.createTables()

        return Const.DONE


    def read_configuration_features(self, file):

        processing_code = Processor.getNumber(file)
        num_columns = Processor.getNumber(file)
        columns = []

        for num_column in range(num_columns):
            columns.append(file.readline().strip())

        if num_columns is Const.FAIL or processing_code is Const.FAIL or columns is []:
            print("Archivo de configuracion incorrecto.")
            return Const.FAIL

        return (processing_code, columns)

    #def read_data(self, offers):
    def read_data(self):

        if self.reprocess is False:
            data = Offer.select_news()
        else:
            data = Offer.select_all()

        data = list(data)
        #data = offers

        #Roy - only 2016
        #new_data = []
        #for offer in data:
        #    if offer.year == 2016:
        #        new_data.append(offer)

        #data = new_data

        # split data
        n_chunks = Processor.N_PROCESS
        chunk_size = len(data)//n_chunks + 1
        self.chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

        return Const.DONE

    def find_phrase(self, phrase, text):
        if len(re.findall('\\b' + phrase + '\\b', text, flags=re.IGNORECASE)) > 0:
            return True
        else:
            return False

    def find_words(self, dataList, dictionary):
        if dictionary == Const.FAIL:
            return []
        else:
            phrases = dictionary.phrases
            found = set()
            for data in dataList:
                data = data.lower()
                dataStemmed = self.stem_text(data)
                for phrase in phrases:
                    for search in dictionary.similars_stem[phrase]:
                        searchStemmed = self.stem_text(search)
                        if self.find_phrase(searchStemmed, dataStemmed):
                            found.add(phrase)

                    for search in dictionary.similars_no_stem[phrase]:
                        if self.find_phrase(search, data):
                            found.add(phrase)

            return found

    def find_priority_phrase(self, dataList, dictionary):
        if dictionary == Const.FAIL:
            return None
        else:
            found = set()
            phrases = dictionary.phrases
            all_data = ""
            for data in dataList:
                all_data += data.lower() + ' '

            all_data_stemmed = self.stem_text(all_data)
            for phrase in phrases:
                for search in dictionary.similars_stem[phrase]:
                    searchStemmed = self.stem_text(search)
                    if self.find_phrase(searchStemmed, all_data_stemmed):
                        found.add(phrase)
                        return found

                for search in dictionary.similars_no_stem[phrase]:
                    if self.find_phrase(search, all_data):
                        found.add(phrase)
                        return found

            return found

    def procSentence(self, dataList, slug, cnt):
        text = ""
        for i, data in enumerate(dataList):
            text += data.lower() + ' '

        finders = self.dictionaries['find_'+slug]

        dictionary = self.dictionaries[slug]

        delimiters = self.dictionaries['ends']

        origin = text
        text = tp.remove_stopwords(text)
        text = tp.remove_whitespaces(text)

        proc = text
        foundWords = set()
        p1 = p2 = p3 = -1
        maxP3 = 0

        while (1):
            flag = True
            for w3 in delimiters:
                try:
                    p3 = text.index(w3)
                    flag = False
                except:
                    continue

            for w1 in finders:
                try:
                    p1 = text.index(w1)
                except:
                    continue

                for phrase in dictionary.phrases:
                    words = dictionary.similars_stem[phrase] + dictionary.similars_no_stem[phrase]
                    for w2 in words:
                        try:
                            p2 = text.index(w2)
                            if (p1<p2) and (p2<p3):
                                foundWords.add(phrase)
                        except:
                            continue

            if flag:
                if foundWords != set():
                    cnt += 1

                return foundWords, cnt

            text = text[p3+1:]

    # No generic. Changed by different data source
    def process(self, dataList, code, dictionary=None):
        if code is Processor.COPY_VALUE_PROCESSING_CODE:
            value = str(dataList[0])
            for data in dataList[1:]:
                value += str(data)
            return value

        if code is Processor.CAREERS_PROCESSING_CODE:
            careers, Processor.CNT_CAREERS = self.procSentence(dataList, 'careers', Processor.CNT_CAREERS) 
            return careers

        regex = re.compile('[%s]' % re.escape(Processor.PUNCTUATIONS))
        for i, data in enumerate(dataList):
            dataList[i] = regex.sub(' ', data)

        for i, data in enumerate(dataList):
            dataList[i] = ""  # Change to " " when you change your finder (regex)
            for word in data.split():
                if word not in Processor.STOP_WORDS:
                    dataList[i] += word + ' '

        if code is Processor.FIND_WORDS_PROCESSING_CODE:
            return self.find_words(dataList, dictionary)

        if code is Processor.FIND_PRIORITY_PHRASE_PROCESSING_CODE:
            return self.find_priority_phrase(dataList, dictionary)

    def stem_text(self, text):
        newText = ""
        for word in text.split():
            wordStemmed = Processor.STEMMER.stem(word)
            newText += wordStemmed + ' '

        return newText.strip()

    def process_offer(self, unproc_offer):
        month = unproc_offer.month
        year = unproc_offer.year
        id = unproc_offer.id
        features = unproc_offer.features

        offer_skills = {}

        career_proc_code = self.config_features[Processor.CAREERS][0]
        career_features = self.config_features[Processor.CAREERS][1]
        data = []
        for feature_needed in career_features:
            try:
                data.append(unproc_offer.features[feature_needed])
            except:
                data.append("")
        careers = self.process(data, career_proc_code, self.dictionaries[Processor.CAREERS])

        for field in self.fields:
            processing_code = self.config_features[field][0]
            features_needed = self.config_features[field][1]

            data = []
            for feature_needed in features_needed:
                try:
                    data.append(unproc_offer.features[feature_needed])
                except:
                    data.append("")

            if processing_code == Processor.COPY_VALUE_PROCESSING_CODE:
                features[field] = self.process(data, processing_code)
            else:
                offer_skills[field] = self.process(data, processing_code, self.dictionaries[field])
                if offer_skills[field] == set():
                    offer_skills[field] = {Processor.NOT_FOUND}  # Always Otros?


        return Offer(year, month, id, features, careers, offer_skills)

    def process_offers(self, data, outfile):
        #Offer.connectToDatabase(self.keyspace)

        sys.stdout = open(outfile, 'w')

        csv_line = '|'.join("^"+ feature + "^" 
                for feature in feature_list_1)
        print(csv_line)


        proc_offers = []
        for idx, unproc_offer in enumerate(data):
            proc_offer = self.process_offer(unproc_offer)
            if proc_offer.careers:
                #printing...
                #proc_offer.print_l4(False, feature_list_symplicity)

                if 'NombreAviso' in proc_offer.features:
                    proc_offer.print_l4(False, feature_list_1)
                else:
                    proc_offer.print_l4(False, feature_list_2)

                proc_offers.append(proc_offer)

        return proc_offers
        #for proc_offer in proc_offers:
        #    proc_offer.update()

    def run(self):
        n_jobs = len(self.chunks)
        jobs = []
        for i in range(n_jobs):
            p = multiprocessing.Process(target=self.process_offers, args=(self.chunks[i],))
            jobs.append(p)
            p.start()

        return Const.DONE



def main():
    if len(sys.argv) == 1:
        print('Debe ingresar un archivo de configuracion')
        return None

    if len(sys.argv) == 2:
        processor = Processor(sys.argv[1], reprocess=False)

    if len(sys.argv) == 3:
        if (sys.argv[1] == '-r'):
            processor = Processor(sys.argv[2], reprocess=True)
        else:
            print("No se reconoce el comando")

    if not processor.read_configuration():  # Add exceptions
        print("No se pudo leer correctamente el archivo de configuracion")
        return None

    if not processor.connect_to_database():
        print("No se pudo conectar a la base de datos")
        return None

    if not processor.read_data():  # Add FAIL option
        print("Ocurrio un error al momento de leer los datos a procesar")
        return None

    if not processor.get_dictionaries():
        print("Ocurrio un error al leer los diccionarios")
        return None

    if not processor.run():
        print("Ocurrio un error al procesar las ofertas")
        return None


if __name__ == "__main__":
    main()
