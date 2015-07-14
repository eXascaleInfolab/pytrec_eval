from itertools import groupby
from collections import Counter
import math

__author__ = 'alberto'

from pytrec_eval import TrecRun, QRels


def purity(run, qrels, detailed=False):
    """
    :param run:
    :type run: TrecRun
    :param qrels:
    :type qrels: QRels
    :param detailed:
    :return:
    """
    # [(form_id, cluster_id)]
    tmp = [(topic, entries[0][0]) for topic, entries in run.entries.items() if entries]
    tmp.sort(key=lambda x: x[1])  # sort by cluster_id
    cnt = 0
    N = len(tmp)
    # details[cluster_id] = (most_common_class, count)
    details = {}
    for cluster_id, cluster in groupby(tmp, key=lambda x: x[1]):
        # qrels.getAllRelevants(form_id)[0] gets the correct class of the element
        classes_in_cluster = [qrels.getAllRelevants(form_id).pop() for form_id, cluster_id in cluster]
        class_counts = Counter(classes_in_cluster)
        most_common_class, most_common_count = class_counts.most_common(1)[0]
        cnt += most_common_count
        details[cluster_id] = (most_common_class, most_common_count)
    return cnt / N if not detailed else (cnt / N, details)


def nmi(run, qrels, detailed=False):
    """
    :param run:
    :type run: TrecRun
    :param qrels:
    :type qrels: QRels
    :param detailed: no details provided...
    :return:
    """
    tmp = [(topic, entries[0][0]) for topic, entries in run.entries.items() if entries]
    tmp.sort(key=lambda x: x[1])  # sort by cluster_id
    cnt = 0
    N = len(tmp)
    # details[cluster_id] = (most_common_class, count)
    details = {}
    # p_cluster_label[cluster_id][label_id] = count
    n_cluster_label = {}
    n_cluster = {}
    n_label = {}
    for cluster_id, cluster in groupby(tmp, key=lambda x: x[1]):
        n_cluster_label[cluster_id] = {}
        cluster_lst = list(cluster)
        classes_in_cluster = [qrels.getAllRelevants(form_id).pop() for form_id, cluster_id in cluster_lst]

        class_counts = Counter(classes_in_cluster)
        for clazz, cnt in class_counts.items():
            if clazz not in n_label:
                n_label[clazz] = 0
            n_label[clazz] += cnt
            if clazz not in n_cluster_label[cluster_id]:
                n_cluster_label[cluster_id][clazz] = 0
            n_cluster_label[cluster_id][clazz] += cnt

        if cluster_id not in n_cluster:
            n_cluster[cluster_id] = 0
        n_cluster[cluster_id] += len(cluster_lst)

    I = sum(n_cluster_label[k][j] / N *
            math.log(
                (N * n_cluster_label[k][j]) / (n_cluster[k] * n_label[j])
            )
            if k in n_cluster_label and j in n_cluster_label[k] else 0
            for k in n_cluster
            for j in n_label)

    h_omega = - sum(n_cluster[k] / N * math.log(n_cluster[k] / N)
                    for k in n_cluster)
    h_c = - sum(n_label[j] / N * math.log(n_label[j] / N)
                for j in n_label)
    return I / ((h_c + h_omega) / 2)


def rand_index(run, qrels, detailed=False):
    """
    :param run:
    :type run: TrecRun
    :param qrels:
    :type qrels: QRels
    :param detailed: no details available
    :return:
    """
    items = run.getTopicIds()
    tp, tn, fp, fn = 0, 0, 0, 0
    for i in items:
        i_cluster = run.getEntriesBy(i)[0]
        i_label = qrels.getAllRelevants(i).pop()
        for j in [j for j in items if j > i]:
            j_cluster = run.getEntriesBy(j)[0]
            j_label = qrels.getAllRelevants(j).pop()
            if i_label == j_label and i_cluster == j_cluster:
                tp += 1
            elif i_label != j_label and i_cluster != j_cluster:
                tn += 1
            elif i_label == j_label and i_cluster != j_cluster:
                fn += 1
            else: # i_label != j_label and i_cluster == j_cluster:
                fp += 1
    return (tp + tn) / (tp + tn + fp + fn)


def f_clustering(beta):
    def f_beta(run, qrels, detailed=False):
        """
        :param run:
        :type run: TrecRun
        :param qrels:
        :type qrels: QRels
        :param detailed: no details available
        :return:
        """
        items = run.getTopicIds()
        tp, tn, fp, fn = 0, 0, 0, 0
        for i in items:
            i_cluster = run.getEntriesBy(i)[0]
            i_label = qrels.getAllRelevants(i).pop()
            for j in [j for j in items if j > i]:
                j_cluster = run.getEntriesBy(j)[0]
                j_label = qrels.getAllRelevants(j).pop()
                if i_label == j_label and i_cluster == j_cluster:
                    tp += 1
                elif i_label != j_label and i_cluster != j_cluster:
                    tn += 1
                elif i_label == j_label and i_cluster != j_cluster:
                    fn += 1
                else: # i_label != j_label and i_cluster == j_cluster:
                    fp += 1
        p = tp / (tp + fp)
        r = tp / (tp + fn)
        return ((beta * beta + 1) * p * r) / (beta * beta * p + r)
    return f_beta
