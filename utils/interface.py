from offer import Offer

SELECT_SOURCES_MSG = ["Seleccione las fuentes:"]
SOURCES = ["symplicity",
           "new_btpucp",
           "new_aptitus",
           "new_bumeran",
           "new_cas",
           ]


WAIT_FEATURES_MSG_LIST = ["Se estan revisan los campos existentes",
                          "Espere un momento...",
                          ]

SELECT_FEATURES_MSG = "Seleccione los campos de la fuente: {0}"

def read_sources(interface):
    selected_sources = interface.choose_multiple(SOURCES,
                                                 SELECT_SOURCES_MSG)
    return selected_sources


def read_features(interface, sources):
    features_by_source = interface.wait_function(WAIT_FEATURES_MSG_LIST,
                                                 load_features,
                                                 sources,
                                                 )
    selected_features = {}
    for source, features in features_by_source.items():
        msg = SELECT_FEATURES_MSG.format(source)

        options = sorted(list(features))
        selected = interface.choose_multiple(options,
                                             msg)
        selected_features[source] = selected

    return selected_features

def load_features(sources):
    features = {}
    for source in sources:
        features[source] = set()
        offers = Offer.SelectAll(source)
        for offer in offers:
            for feature in offer.features:
                features[source].add(feature)

    return features
