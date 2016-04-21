__author__ = 'alberto'

from pytrec_eval import TrecRun


def get_clusters(run):
    """
    get all clusters in run
    :param run:
    :type run: TrecRun
    :return:
    """
    clusters = {}
    for item_id, cluster_rnk in run.entries.items():
        cluster_id = cluster_rnk[0][0]
        if cluster_id not in clusters:
            clusters[cluster_id] = set()
        clusters[cluster_id].add(item_id)
    return clusters


def jaccard_index(c0, c1):
    """
    Computes the Jaccard index to quantify the similarity
    of two clusters.
    :param c0:
    :type c0: set
    :param c1:
    :type c1: set
    :return:
    """
    return len(c0 & c1) / len(c0 | c1)


def max_jaccard(cluster, clusters):
    """
    returns the id of the cluster in <clusters>
    that is more similar to <cluster>
    :param cluster:
    :type cluster: set
    :param clusters: a dictionary clusters[cluster_id] = set(items)
    :type clusters: dict
    :return: a pair (jaccard_index, cluster_id) where cluster_id refers
    to a cluster in <clusters>.
    """
    return max([(jaccard_index(cluster, j), cluster_id)
                for cluster_id, j in clusters.items()],
               key=lambda x: x[1])


def jaccard_map(clusters0, clusters1):
    """
    Creates a map between clusters in <clusters0>
    and clusters in <clusters1> based on the Jaccard similarity.
    :param clusters0:
    :type clusters0: dict
    :param clusters1:
    :type clusters1: dict
    :return:
    """
    m = {}
    for c0, items0 in clusters0.items():
        score, best_map = max_jaccard(items0, clusters1)
        m[c0] = (best_map, score)
    return m

