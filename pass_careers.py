from offer import Offer
from career import Career

Offer.ConnectToDatabase()
Offer.SetKeyspace("symplicity")
Offer.PrepareStatements()

Career.ConnectToDatabase()
Career.PrepareStatements()

offers = Offer.SelectAll("symplicity")

all_careers = [career.name for career in Career.Select()]

for offer in offers:
    careers = offer.features['Majors/Concentrations'].split(",")
    for career in careers:
        if career in all_careers:
            offer.careers.add(career)

    offer.insert()
