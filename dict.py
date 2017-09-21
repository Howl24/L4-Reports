from interface import Interface
from dictionary import DictionaryManager

CREATE_BOW = "Crear un nuevo bag of words"
SAVE_REPRESENTATIVES = "Guardar un bag of words"
SAVE_REVIEW = "Guardar una revision de palabras representativas"
CLOSE = "Salir"
MODES = [CREATE_BOW,
         SAVE_REPRESENTATIVES,
         SAVE_REVIEW,
         CLOSE,
         ]
MODE_SELECTION_MSG = "Escoja una opción: "


# def save_review(interface):
#    Dictionary.SaveReview(view)
#
#    dic = interface.read_dictionary(new=False)
#    if not dic:
#        return
#
#    interface.import_review(dic)


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

        if mode == CREATE_BOW:
            dict_manager.create_bow()

        if mode == SAVE_REPRESENTATIVES:
            dict_manager.save_representatives()

        if mode == SAVE_REVIEW:
            dict_manager.save_review()

    return


if __name__ == "__main__":
    main()
