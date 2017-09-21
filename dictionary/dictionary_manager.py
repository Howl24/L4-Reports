from dictionary import Dictionary
from dictionary import Configuration
from dictionary import Phrase
from dictionary import Representative
from offer import Offer
import os

from dictionary.constants import *

"""
This class contains methods to interact with dictionaries by an interface.
"""


class DictionaryManager:
    def __init__(self, interface, dictionary=None, cluster=None):
        self.interface = interface
        self.dict = dictionary
        Dictionary.ConnectToDatabase(cluster)
        Dictionary.PrepareStatements()
        Offer.ConnectToDatabase(cluster)

    # -------------------------------------------------------------------------


    def create_bow(self):
        # Ask if user wants to create a new dictionary
        response = self.ask_new_dictionary()
        if response == YES:
            # Creates a new dictionary
            self.dict = self.read_new_dictionary()
            self.read_new_configuration()

        else:
            # Select a dictionary from a list
            self.dict = self.select_old_dictionary()

        # Not succesful dictionary (Check Exception option)
        if not self.dict:
            return None

        # Get dictionary phrases
        self.dict.update_phrases_frecuency()

        # Group phrases by representatives
        self.dict.build_representatives()

        self.dict.export_unreview_phrases()

    # -------------------------------------------------------------------------

    def save_representatives(self):
        # Not read dictionary
        if not self.dict:
            self.dict = self.select_old_dictionary()

        if not self.dict:
            return None
            
        self.import_representatives()
        self.dict.export_unreview_representatives()

    def read_import_filename(self, msg):
        # TODO
        # Move to static utils file
        extension = ".csv"
        filenames = [filename for filename in os.listdir() if extension in filename]
        filename = self.interface.choose_option(filenames, msg)

        return filename

    def import_representatives(self):
        READ_REPRESENTATIVES_FILENAME_MSG = "Seleccione el archivo con las frases que desea ingresar."

        filename = self.read_import_filename(READ_REPRESENTATIVES_FILENAME_MSG)

        f = open(filename, 'r')

        wrong_lines = []
        for idx, line in enumerate(f):
            if idx == 0:
                continue

            data = line.split(',')
            try:
                rep_name =data[0].strip().strip("'")
                phrase_name = data[1].strip().strip("'")
            except Exception as e:
                wrong_lines.append(str(e) + " en linea " + str(idx + 1))
                continue

            try:
                phrase = self.dict.phrases[phrase_name]
            except KeyError:
                wrong_lines.append("Frase '" + phrase_name + \
                                   "' de la linea " + str(idx + 1) + \
                                   " no existe en diccionario")
                continue

            phrase.representative = rep_name
            print(rep_name)
            phrase.insert(self.dict.name)

        self.dict.representatives = Representative.ByDictName(self.dict.name)
        
        for line in wrong_lines:
            print(line)

    # ------------------------------------------------------------------------

    def save_review(self):
        # Not read dictionary
        if not self.dict:
            self.dict = self.select_old_dictionary()

        if not self.dict:
            return None
            
        self.import_review()

    def import_review(self):
        READ_REVIEW_FILENAME_MSG = "Seleccione el archivo con la revisión: "
        filename = self.read_import_filename(READ_REVIEW_FILENAME_MSG)

        f = open(filename, 'r')
        representatives = {}
        wrong_lines = []
        for idx, line in enumerate(f):
            if idx == 0:
                continue
                
            data = line.split(',')
            try:
                rep_name = data[0].strip()
                state = data[1].strip()
            except Exception as e:
                wrong_lines.append(str(e) + " en linea " + str(idx + 1))
                continue

            if state in YES_RESPONSES:
                state = True
            elif state in NO_RESPONSES:
                state = False
            else:
                wrong_lines.append("Revisión '" + state + \
                                   "' no reconocida en linea " + str(idx + 1))
                continue

            representatives[rep_name] = state

        for phrase in self.dict.phrases.values():
            if phrase.representative in representatives:
                phrase.state = representatives[phrase.representative]
                phrase.insert(self.dict.name)

        for line in wrong_lines:
            print(line)

    # ---------------------------------------------------------------------- 
    # Read dictionary functions
    def ask_new_dictionary(self):
        response = self.interface.choose_option(READ_DICT_OPTIONS,
                                                READ_DICT_OPTIONS_MSG)

        if response in YES_RESPONSES:
            return YES
        else:
            return NO

    def read_new_dictionary(self):
        # TODO
        # Add Esc button interaction to return None or an Exception
        dictionary_names = Dictionary.GetDictionaryNames()
        show_hint = False
        correct = False
        while not correct:
            dict_name = self.interface.read_string(READ_DICT_NAME_MSG,
                                                   DICT_NAME_FIELD,
                                                   show_hint,
                                                   READ_DICT_NAME_HINT,
                                                   )
            # Add Esc code here

            if dict_name in dictionary_names:
                show_hint = True
            else:
                correct = True

        return Dictionary.New(dict_name)

    def select_old_dictionary(self):
        # TODO
        # Add Esc button interaction or "Return" option to return None or an Exception
        dictionary_names = Dictionary.GetDictionaryNames()
        if not dictionary_names:
            msg = "No se encontraron diccionarios antiguos."
            self.interface.temp_msg(msg, 2)
            return None

        dict_name = self.interface.choose_option(dictionary_names,
                                                 DICTIONARY_SELECTION_MSG)

        # Add Esc code here

        return Dictionary.ByName(dict_name)

    #---------------------------------------------------------------------- 
    # Read dictionary configuration
    
    def read_new_configuration(self):
        sources = self.read_keyspaces()
        features = self.read_features(sources)
        ngrams = self.read_ngrams()
        dfs = self.read_dfs()
        last_bow = (0, 0)

        for source in sources:
            new_conf = Configuration(self.dict.name,
                                     source,
                                     features[source],
                                     ngrams,
                                     dfs)

            self.dict.add_configuration(new_conf)

        self.dict.save_configuration()


    def read_ngrams(self):
        READ_NGRAMS_MSG = "Ingrese el número mínimo y máximo de ngramas"
        READ_MIN_FIELD_MSG = "Mínimo: "
        READ_MAX_FIELD_MSG = "Máximo: "
        READ_NGRAMS_FIELDS = [READ_MIN_FIELD_MSG, READ_MAX_FIELD_MSG]
        READ_NGRAMS_FIELD_RANGE = (1, None)  # >= 1
        READ_NGRAMS_RANGES = [READ_NGRAMS_FIELD_RANGE, READ_NGRAMS_FIELD_RANGE]
        READ_NGRAMS_HINT = "(El valor mínimo debe ser menor o igual al máximo)"

        correct = False
        show_hint = False
        while not correct:
            ngrams = self.interface.read_int_list(READ_NGRAMS_MSG,
                                                  READ_NGRAMS_FIELDS,
                                                  READ_NGRAMS_RANGES,
                                                  show_hint,
                                                  READ_NGRAMS_HINT,
                                                  )

            if self._check_ngrams(ngrams) is True:
                correct = True
            else:
                show_hint = True

        return ngrams

    def read_dfs(self):
        READ_DFS_MSG = "Ingrese el rango de frecuencias a obtener"
        READ_MIN_DFS_MSG = "Mínimo: "
        READ_MAX_DFS_MSG = "Máximo: "
        READ_DFS_FIELDS = [READ_MIN_DFS_MSG, READ_MAX_DFS_MSG]
        READ_DFS_FIELD_RANGE = (0, 1)  # 0 <= x <= 1
        READ_DFS_RANGES = [READ_DFS_FIELD_RANGE, READ_DFS_FIELD_RANGE]
        READ_DFS_HINT = "(El valor mínimo debe ser menor o igual al máximo)"

        correct = False
        show_hint = False
        while not correct:
            dfs = self.interface.read_double_list(READ_DFS_MSG,
                                                  READ_DFS_FIELDS,
                                                  READ_DFS_RANGES,
                                                  show_hint,
                                                  READ_DFS_HINT,
                                                  )

            if self._check_dfs(dfs) is True:
                correct = True
            else:
                show_hint = True

        return dfs

    def _check_dfs(self, dfs):
        MIN_DFS_INDEX = 0
        MAX_DFS_INDEX = 1

        min_dfs = dfs[MIN_DFS_INDEX]
        max_dfs = dfs[MAX_DFS_INDEX]

        return min_dfs <= max_dfs

    def _check_ngrams(self, ngrams):
        MIN_NGRAM_INDEX = 0
        MAX_NGRAM_INDEX = 1

        min_ngram = ngrams[MIN_NGRAM_INDEX]
        max_ngram = ngrams[MAX_NGRAM_INDEX]

        return min_ngram <= max_ngram

    def read_keyspaces(self):
        SELECT_KEYSPACES_MSG = ["Seleccione las fuentes:"]
        KEYSPACES = ["new_btpucp", "new_aptitus", "new_bumeran", "new_cas", "symplicity"]

        selected_keys = self.interface.choose_multiple(KEYSPACES,
                                                       SELECT_KEYSPACES_MSG)
        return selected_keys

    def read_features(self, sources):
        WAIT_FEATURES_MSG_LIST = ["Se estan revisan los campos existentes",
                                  "Espere un momento...",
                                  ]

        all_features = self.interface.wait_function(WAIT_FEATURES_MSG_LIST,
                                                    self.load_features,
                                                    sources,
                                                    )

        selected_features = {}
        for source in all_features:
            features = all_features[source]
            SELECT_FEATURES_MSG = "Seleccione los campos de la fuente: {0}"
            msg = SELECT_FEATURES_MSG.format(source)

            options = sorted(list(features))
            selected = self.interface.choose_multiple(options,
                                                      msg)
            selected_features[source] = selected

        return selected_features

    def load_features(self, sources):
        features = {}
        for source in sources:
            features[source] = set()
            offers = Offer.SelectAll(source)
            for offer in offers:
                for feature in offer.features:
                    features[source].add(feature)

        return features
