import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AffinityPropagation
from sklearn.metrics.pairwise import cosine_distances
from sklearn.utils import check_array


# Class for support
class ProcessedText(object):
    def __init__(self, id_, specialWords):
        self.id_ = id_
        self.specialWords = specialWords

    def __str__(self):
        if isinstance(self.specialWords, str):
            return self.id_ + " " + self.specialWords
        else:
            return self.specialWords


def set_carrerWithFeatures(listObject, clean_list, list_carrers_dic, carrers):
    # Better performance than set_carrerWithFeatures
    dictionaryCarrers = dict((k, None) for k in carrers)
    dictionarySupportID = dict((k, None) for k in carrers)
    for pos, lis_carrers in enumerate(list_carrers_dic):
        for striVersion in lis_carrers:
            if dictionaryCarrers[striVersion] is None:
                dictionaryCarrers[striVersion] = [clean_list[pos][:]]
                dictionarySupportID[striVersion] = [listObject[pos].id_]
            else:
                dictionaryCarrers[striVersion].append(clean_list[pos][:])
                dictionarySupportID[striVersion].append(listObject[pos].id_)
    return dictionaryCarrers, dictionarySupportID


def run_clusteringCaseTwo(data):
    tfidf = TfidfVectorizer(preprocessor=lambda x: x, tokenizer=lambda x: x,
                            min_df=.1, max_df=.8, ngram_range=(1, 2), sublinear_tf=True, smooth_idf=True)
    tfidf_matrix = tfidf.fit_transform(data)
    tfidf_matrix = check_array(tfidf_matrix, accept_sparse='csr')
    input_matrix = cosine_distances(tfidf_matrix)
    pre_media = np.median(input_matrix, axis=1)
    median = np.median(pre_media)
    preference = median
    af = AffinityPropagation(
        damping=.9480, affinity="precomputed", preference=preference).fit(input_matrix)
    cluster_centers_indices = af.cluster_centers_indices_
    n_clusters_ = len(cluster_centers_indices)
    if n_clusters_ >= 20:
        af = AffinityPropagation(
            damping=.9675, affinity="precomputed", preference=preference).fit(input_matrix)
    labels = af.labels_
    cluster_centers_indices = af.cluster_centers_indices_
    n_clusters_ = len(cluster_centers_indices)
    return af


def get_features(tfidf):
    indices = np.argsort(tfidf.idf_)[::-1]
    features = tfidf.get_feature_names()
    top_n = 10
    top_features = [features[i] for i in indices[:top_n]]
    return top_features


def get_label(cluster_indices, tfidf_matrix, tfidf):
    print(tfidf.get_feature_names())
    for x in cluster_indices:
        print("This is the row  ", x, " and have the values: ",
              tfidf_matrix[x].toarray())


def get_list_of_clusters(af, carrer, dictionary):
    num_clusters = len(af.cluster_centers_indices_)
    diction = dict((k, None) for k in range(num_clusters))
    enum = 0
    for pos in af.labels_:
        if diction[pos] is None:
            diction[pos] = [dictionary[carrer][enum][:]]
        else:
            diction[pos].append(dictionary[carrer][enum][:])
        enum += 1
    return diction
