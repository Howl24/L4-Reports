# YES_RESPONSES = ['Y', 'S', 'y', 's', 'Si', 'si', 'No', 'NO', 'SI']

# -----------------------------------------------------------------------------
# General

YES_RESPONSES = ['S', 's', 'Si', 'si', 'SI']
NO_RESPONSES = ['N', 'n', 'No', 'no', 'NO']
SUCCESSFUL_OPERATION = True
UNSUCCESSFUL_OPERATION = False
SYMPLICITY_SOURCE = "symplicity"
YES = "Si"
NO = "No"
SIMILARITY_PERCENTAGE = 0.9

ACCEPT_REPRESENTATIVE_RESPONSES = ['SI', 'Si', 'S', 'si']
REJECT_REPRESENTATIVE_RESPONSES = ['No', 'NO', 'N', 'no']
DICTIONARY_KEYSPACE = "general"


# -----------------------------------------------------------------------------
# Dictionary Interaction

# Ask dictionary creation
READ_DICT_OPTIONS_MSG = "Desea crear un diccionario nuevo?"
YES_RESP = "Si"
NO_RESP = "No"
READ_DICT_OPTIONS = [YES_RESP, NO_RESP]

# Read new dictionary
READ_DICT_NAME_MSG = "Ingrese el nombre del nuevo diccionario:"
READ_DICT_NAME_HINT = "(El nombre ya esta siendo utilizado)"
DICT_NAME_FIELD = "Nombre: "

# Select an old dictionary
DICTIONARY_SELECTION_MSG = "Seleccione el diccionario a utilizar:"

# Create bow wait messages
WAIT_MSG_UPDATE_PHRASE_FREC = "Actualizando frases ..."
WAIT_MSG_BUILD_SIMILARS = "Agrupando frases similares ..."
WAIT_MSG_EXPORT_SIMILARS = "Exportando similares ..."


# -----------------------------------------------------------------------------
# Dictionary configuration

# Read N-grams

NGRAM_RANGE = (1, None)  # N-gram >= 1

READ_NGRAMS_MSG = "Ingrese el número mínimo y máximo de ngramas"
READ_NGRAMS_HINT = "(El valor mínimo debe ser menor o igual al máximo)"

READ_MIN_NGRAM_MSG = "Mínimo: "
READ_MAX_NGRAM_MSG = "Máximo: "
READ_NGRAM_FIELDS = [READ_MIN_NGRAM_MSG,
                     READ_MAX_NGRAM_MSG]

READ_NGRAM_FIELD_RANGES = [NGRAM_RANGE,
                           NGRAM_RANGE]

MIN_NGRAM_INDEX = 0
MAX_NGRAM_INDEX = 1


# Read Document Frecuencies

DFS_RANGE = (0, 1)  # 0 <= x <= 1

READ_DFS_MSG = "Ingrese el rango de frecuencias a obtener"
READ_DFS_HINT = "(El valor mínimo debe ser menor o igual al máximo)"

READ_MIN_DFS_MSG = "Mínimo: "
READ_MAX_DFS_MSG = "Máximo: "
READ_DF_FIELDS = [READ_MIN_DFS_MSG,
                  READ_MAX_DFS_MSG]

READ_DF_FIELD_RANGES = [DFS_RANGE,
                        DFS_RANGE]

MIN_DF_INDEX = 0
MAX_DF_INDEX = 1


# -----------------------------------------------------------------------------

# Save representatives
READ_REPRESENTATIVES_FILENAME_MSG = "Seleccione el archivo con las frases " + \
                                    "que desea ingresar."


# Save Review
READ_REVIEW_FILENAME_MSG = "Seleccione el archivo con la revisión: "
