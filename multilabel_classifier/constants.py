# -------------------------------------------------------------------------
# Manager modes

SET_CAREER_LABELS = "Crear etiquetas para clasificación"
GET_OFFERS_TO_LABEL = "Obtener muestra a etiquetar"
SAVE_CLASSIFICATION_REVIEW = "Guardar Revisión"
CLASSIFY_OFFERS = "Clasificar ofertas"
CLOSE = "Salir"

MODES = [SET_CAREER_LABELS,
         GET_OFFERS_TO_LABEL,
         CLASSIFY_OFFERS,
         SAVE_CLASSIFICATION_REVIEW,
         CLOSE,
         ]

MODE_MSG = "Seleccione una opción: "

# ------------------------------------------------------------------------
# IO
# Read field
READ_FIELD_MSG = "Ingrese el nombre del campo que agrupe las etiquetas"
FIELD = "Campo: "

# Read labels
READ_LABEL_MSG = "Ingrese el nombre de las etiquetas"
LABEL_FIELD = "Etiqueta: "
READ_LABELS_STOP_STRING = ""
READ_LABELS_HINT = "(Etiqueta vacía para terminar.)"

# Select labels
CHOOSE_FIELD_MSG = "Seleccione un campo: "

# ------------------------------------------------------------------------
# Get offers to label
TRAINING_MIN_OFFER_CNT = 10

# -------------------------------------------------------------------------
# Classify offers

TRAINING_SOURCE = "symplicity"
TRAINING_DATE_RANGE = [(1, 2013), (12, 2017)]

# ------------------------------------------------------------------------
# Save Review
READ_LABELED_OFFERS_FILENAME_MSG = "Seleccione el archivo" + \
                                           " con las ofertas etiquetadas"

# ------------------------------------------------------------------------
# Read career
CHOOSE_CAREER_MSG = "Seleccione la carrera a clasificar:"

