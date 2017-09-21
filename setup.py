from dictionary import Dictionary
from label import Label

def main():
    Dictionary.ConnectToDatabase()
    Dictionary.CreateTables()
    Label.ConnectToDatabase()
    Label.CreateTables()

    Offer.ConnectToDatabase()
    Offer.SetKeyspace("symplicity")
    Offer.CreateTables()

if __name__ == "__main__":
    main()

