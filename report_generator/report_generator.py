from career import Career
from dictionary import DictionaryManager

class ReportGenerator:

    def __init__(self, interface, career=None, sources=None):
        self.interface = interface
        self.career = career
        self.sources = sources


    def run(self):
        Career.ConnectToDatabase()
        Career.PrepareStatements()

        if self.career is None:
            self.career = self.read_career()

        if self.sources is None:
            dict_manager = DictionaryManager(self.interface)
            self.sources = dict_manager.read_keyspaces()

        print(self.sources)

    def read_career(self):
        CHOOSE_CAREER_MSG = "Seleccione la carrera a clasificar:"
        careers = sorted(Career.Select())
                
        career = self.interface.choose_option(careers, CHOOSE_CAREER_MSG)
        return career
