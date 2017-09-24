from interface import Interface
from dictionary import DictionaryManager

CREATE_DICTIONARY = "Crear un nuevo diccionario"
UPDATE_PHRASES = "Actualizar frases"
SAVE_REPRESENTATIVES = "Guardar palabras representativas"
SAVE_REVIEW = "Guardar una revision de palabras representativas"
CLOSE = "Salir"
MODES = [CREATE_DICTIONARY,
         UPDATE_PHRASES,
         SAVE_REPRESENTATIVES,
         SAVE_REVIEW,
         CLOSE,
         ]
MODE_SELECTION_MSG = "Escoja una opción: "


def replace_out():
    import sys
    file = open('out.txt', 'w')
    sys.stdout = file
    sys.stderr = file


def main():
    # Only for develop
    replace_out()

    view = Interface()
    dict_manager = DictionaryManager(view)

    mode = None
    while (mode != CLOSE):
        mode = view.choose_option(MODES, MODE_SELECTION_MSG)

        if mode == CREATE_DICTIONARY:
            dict_manager.create_dictionary()

        if mode == UPDATE_PHRASES:
            dict_manager.update_phrases()

        if mode == SAVE_REPRESENTATIVES:
            dict_manager.save_representatives()

        if mode == SAVE_REVIEW:
            dict_manager.save_review()

    return


if __name__ == "__main__":
    main()
