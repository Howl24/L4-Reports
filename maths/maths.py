
def intersection(lista, listb):
    """ Return the intersection of two list 

    Return the intersection of two list , but this two list dosen´t have to be nested 

    Arguments:
        lista {Object} -- [First list , dosen´t have to be nested]
        listb {Object} -- [Second list , dosen´t have to be nested]

    Returns:
        IntersectedList -> List with the intersect values 
    """
    return list(set(lista) & set(listb))


def calculate_alpha(fileAreas):
    """ Calculate the alpha value 

    Arguments:
        fileAreas {String}  -- [Name of the file ]
    Returns:
        matrix_alpha -- Matrix with the alphas value 
    """
    read = pd.read_csv(fileAreas)
    len_x = len(read.Area.unique())
    matrix_alpha = np.zeros(shape=(len_x, len_x))
    data = read.groupby('Area')[' Conocimiento'].apply(list)
    listAreas = list(read.Area.unique())
    i = j = 0
    for x in listAreas:
        for y in listAreas:
            matrix_alpha[i, j] = float(len(intersect(data[x], data[y]))) / len(data[x])
            j += 1
        i += 1
        j = 0
    return matrix_alpha
    