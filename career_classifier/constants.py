# --------------------------------------------------------------------------
# Manager modes

UPDATE_CAREERS = "Actualizar Carreras Symplicity"
CLASSIFY_OFFERS = "Clasificar Ofertas"
SAVE_CLASSIFICATION_REVIEW = "Guardar Revisión"
CLOSE = "Salir"

MODES = [UPDATE_CAREERS,
         CLASSIFY_OFFERS,
         SAVE_CLASSIFICATION_REVIEW,
         CLOSE,
         ]

MODE_MSG = "Escoja una acción: "

# -------------------------------------------------------------------------
# Read career

CHOOSE_CAREER_MSG = "Seleccione la carrera a utilizar"

# --------------------------------------------------------------------------
# Save classification review

READ_CAREER_OFFERS_FILENAME_MSG = "Seleccione el archivo" + \
                                  " con las ofertas de la carrera"


# --------------------------------------------------------------------------
# Update careers

CHOOSE_CAREERS_MSG = "Seleccione las carreras q desea ingresar"
SYMPLICITY_SOURCE = "symplicity"
SYMPLICITY_CAREER_FEATURES = ["Majors/Concentrations"]


# --------------------------------------------------------------------------
# Classify offers

TRAINING_SOURCE = "symplicity"
TRAINING_DATE_RANGE = [(1, 2015), (12, 2017)]
MIN_TRAINING_CNT = 15
WAIT_CLASSIFICATION_MSG = "Clasificando ofertas ..."
