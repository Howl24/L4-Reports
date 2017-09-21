from interface import Interface
from report_generator import ReportGenerator

REPORT_GENERATOR = "Generador de Reportes"
CLOSE = "Salir"
MODES = [REPORT_GENERATOR,
         CLOSE,
         ]
MODE_MSG = "Escoja una opción: "


def replace_out():
    import sys
    file = open('out.txt', 'w')
    sys.stdout = file
    sys.stderr = file


def run_report_generator(view):
    report_generator = ReportGenerator(view)
    report_generator.run()


def main():
    # Only for develop
    replace_out()

    view = Interface()

    mode = None
    while (mode != CLOSE):
        mode = view.choose_option(MODES, MODE_MSG)
        if mode == REPORT_GENERATOR:
            run_report_generator(view)


if __name__ == "__main__":
    main()
