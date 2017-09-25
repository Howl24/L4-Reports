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


READ_MIN_DATE_MSG = "Ingrese el mes y año de inicio"
READ_MAX_DATE_MSG = "Ingrese el mes y año de fin"
READ_DATE_RANGE_HINT = "(Fecha de fin debe ser mayor o igual a la de inicio)"
MONTH_MSG = "Mes: "
YEAR_MSG = "Año: "
MONTH_RANGE = (1, 12)
YEAR_RANGE = (2010, 2030)

MONTH_INDEX = 0
YEAR_INDEX = 1
MONTHS_PER_YEAR = 12




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


def read_date_range(interface):
    msg_list = [MONTH_MSG, YEAR_MSG]
    range_list = [MONTH_RANGE, YEAR_RANGE]

    not_correct_range = True
    show_hint = False

    while (not_correct_range):
        min_date = interface.read_int_list(READ_MIN_DATE_MSG,
                                           msg_list,
                                           range_list,
                                           show_hint,
                                           hint=READ_DATE_RANGE_HINT,
                                           )

        max_date = interface.read_int_list(READ_MAX_DATE_MSG,
                                           msg_list,
                                           range_list,
                                           )

        min_date_months = min_date[MONTH_INDEX] + min_date[YEAR_INDEX] * MONTHS_PER_YEAR
        max_date_months = max_date[MONTH_INDEX] + max_date[YEAR_INDEX] * MONTHS_PER_YEAR

        if max_date_months >= min_date_months:
            not_correct_range = False
        else:
            show_hint = True

        return min_date, max_date
