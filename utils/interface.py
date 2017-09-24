from offer import Offer

SELECT_SOURCES_MSG = ["Seleccione las fuentes:"]
SOURCES = ["symplicity",
           "new_bumeran",
           "new_aptitus",
           "new_btpucp",
           "new_cas",
           ]


WAIT_FEATURES_MSG_LIST = ["Se estan revisan los campos existentes",
                          "Espere un momento...",
                          ]

SELECT_FEATURES_MSG = "Seleccione los campos de la fuente: {0}"

def read_sources(interface, sources=SOURCES):
    selected_sources = interface.choose_multiple(sources,
                                                 SELECT_SOURCES_MSG)
    return selected_sources


def read_features(interface, sources):
    features_by_source = interface.wait_function(WAIT_FEATURES_MSG_LIST,
                                                 load_features,
                                                 sources,
                                                 )
    selected_features = {}
    for source, features in features_by_source:
        msg = SELECT_FEATURES_MSG.format(source)

        print(features)
        options = sorted(list(features))
        selected = interface.choose_multiple(options,
                                             msg)
        selected_features[source] = selected

    return selected_features

def load_features(sources):
    all_features = []
    for source in sources:
        source_features = set()
        offers = Offer.SelectAll(source)
        for offer in offers:
            for feature in offer.features:
                source_features.add(feature)

        all_features.append((source, source_features))

    return all_features
