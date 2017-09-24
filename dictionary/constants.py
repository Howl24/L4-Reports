#YES_RESPONSES = ['Y', 'S', 'y', 's', 'Si', 'si', 'No', 'NO', 'SI']

#-------------------------------------------------------------------------------- 
# General

YES_RESPONSES = ['S', 's', 'Si', 'si', 'SI']
NO_RESPONSES = ['N', 'n', 'No', 'no', 'NO']
SUCCESSFUL_OPERATION = True
UNSUCCESSFUL_OPERATION = False
SYMPLICITY_SOURCE = "new_btpucp"
YES = "Si"
NO = "No"
SIMILARITY_PERCENTAGE = 0.9

ACCEPT_REPRESENTATIVE_RESPONSES = ['SI', 'Si', 'S', 'si']
REJECT_REPRESENTATIVE_RESPONSES = ['No', 'NO', 'N', 'no']
DICTIONARY_KEYSPACE = "general"


#-------------------------------------------------------------------------------- 
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

