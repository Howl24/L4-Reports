from dictionary import Dictionary
from dictionary import Configuration
from dictionary import Representative
from offer import Offer
import os
from utils import read_sources
from utils import read_features

from dictionary.constants import WAIT_MSG_UPDATE_PHRASE_FREC
from dictionary.constants import WAIT_MSG_BUILD_SIMILARS
from dictionary.constants import WAIT_MSG_EXPORT_SIMILARS

from dictionary.constants import READ_REPRESENTATIVES_FILENAME_MSG
from dictionary.constants import READ_REVIEW_FILENAME_MSG

from dictionary.constants import READ_DICT_OPTIONS
from dictionary.constants import READ_DICT_OPTIONS_MSG
from dictionary.constants import READ_DICT_NAME_MSG
from dictionary.constants import READ_DICT_NAME_HINT

from dictionary.constants import DICT_NAME_FIELD
from dictionary.constants import DICTIONARY_SELECTION_MSG

from dictionary.constants import READ_NGRAMS_MSG
from dictionary.constants import READ_NGRAMS_HINT
from dictionary.constants import READ_NGRAM_FIELDS
from dictionary.constants import READ_NGRAM_FIELD_RANGES
from dictionary.constants import MIN_NGRAM_INDEX
from dictionary.constants import MAX_NGRAM_INDEX

from dictionary.constants import READ_DFS_MSG
from dictionary.constants import READ_DFS_HINT
from dictionary.constants import READ_DF_FIELDS
from dictionary.constants import READ_DF_FIELD_RANGES
from dictionary.constants import MIN_DF_INDEX
from dictionary.constants import MAX_DF_INDEX

from dictionary.constants import YES_RESPONSES
from dictionary.constants import NO_RESPONSES
from dictionary.constants import YES
from dictionary.constants import NO

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

    def create_dictionary(self):
        self.dict = self.read_new_dictionary()

        if not self.dict:
            return None

        self.read_new_configuration()

    def update_phrases(self):
        self.dict = self.select_old_dictionary()

        # Not succesful dictionary (Check Exception option)
        if not self.dict:
            return None

        dict_sources = [configuration.source
                        for configuration in self.dict.configurations]
        selected_sources = read_sources(self.interface, dict_sources)
        self.dict.sources = selected_sources

        # Get dictionary phrases
        self.interface.wait_function(WAIT_MSG_UPDATE_PHRASE_FREC,
                                     self.dict.update_phrases_frecuency)

        # Group phrases by representatives
        self.interface.wait_function(WAIT_MSG_BUILD_SIMILARS,
                                     self.dict.build_representatives)

        # Export similars
        self.interface.wait_function(WAIT_MSG_EXPORT_SIMILARS,
                                     self.dict.export_unreview_phrases)

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
        filenames = [filename
                     for filename in os.listdir() if extension in filename]
        filename = self.interface.choose_option(filenames, msg)

        return filename

    def import_representatives(self):
        filename = self.read_import_filename(READ_REPRESENTATIVES_FILENAME_MSG)

        f = open(filename, 'r')

        wrong_lines = []
        for idx, line in enumerate(f):
            if idx == 0:
                continue

            data = line.split(',')
            try:
                rep_name = data[0].strip().strip("'")
                phrase_name = data[1].strip().strip("'")
            except Exception as e:
                wrong_lines.append(str(e) + " en linea " + str(idx + 1))
                continue

            try:
                phrase = self.dict.phrases[phrase_name]
            except KeyError:
                wrong_lines.append("Frase '" + phrase_name +
                                   "' de la linea " + str(idx + 1) +
                                   " no existe en diccionario")
                continue

            phrase.representative = rep_name
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
                wrong_lines.append("Revisión '" + state +
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
        # Add Esc button interaction or "Return" option
        # to return None or an Exception
        dictionary_names = Dictionary.GetDictionaryNames()
        if not dictionary_names:
            msg = "No se encontraron diccionarios antiguos."
            self.interface.temp_msg(msg, 2)
            return None

        dict_name = self.interface.choose_option(dictionary_names,
                                                 DICTIONARY_SELECTION_MSG)

        # Add Esc code here

        return Dictionary.ByName(dict_name)

    # ----------------------------------------------------------------------
    # Read dictionary configuration

    def read_new_configuration(self):
        sources = read_sources(self.interface)
        features = read_features(self.interface, sources)
        ngrams = self.read_ngrams()
        dfs = self.read_dfs()

        for source in sources:
            new_conf = Configuration(self.dict.name,
                                     source,
                                     features[source],
                                     ngrams,
                                     dfs)

            self.dict.add_configuration(new_conf)

        self.dict.save_configuration()

    def read_ngrams(self):
        correct = False
        show_hint = False
        while not correct:
            ngrams = self.interface.read_int_list(READ_NGRAMS_MSG,
                                                  READ_NGRAM_FIELDS,
                                                  READ_NGRAM_FIELD_RANGES,
                                                  show_hint,
                                                  READ_NGRAMS_HINT,
                                                  )

            if ngrams[MIN_NGRAM_INDEX] <= ngrams[MAX_NGRAM_INDEX]:
                correct = True
            else:
                show_hint = True

        return ngrams

    def read_dfs(self):
        correct = False
        show_hint = False
        while not correct:
            dfs = self.interface.read_double_list(READ_DFS_MSG,
                                                  READ_DF_FIELDS,
                                                  READ_DF_FIELD_RANGES,
                                                  show_hint,
                                                  READ_DFS_HINT,
                                                  )

            if dfs[MIN_DF_INDEX] <= dfs[MAX_DF_INDEX]:
                correct = True
            else:
                show_hint = True

        return dfs
