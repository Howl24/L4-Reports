from cassandra.cluster import Cluster
from offer import Offer

Offer.ConnectToDatabase()
Offer.SetKeyspace("symplicity")
Offer.PrepareStatements()

field = "Áreas de Conocimiento"
offers = Offer.SelectAll("symplicity")

cnt = 0
for offer in offers:
    if field in offer.features:
        print("Oferta ", cnt+1)
        cnt += 1
        offer_labels = offer.features[field].split(",")
        for label in offer_labels:
            print(label)

        print()
