__author__ = 'alberto'


def confusion_matrix(run, qrels, detailed=False):
    """
    Compute the confusion matrix.
    Doesn't work for a multi-topic classification task.
    Details has no effect here.
    Use the utils.confusion_matrix_toString() to get a visual representation of the matrix.
    :returns a 2d-dictionary cm[predicted][real] = count
    """
    classes_sorted = qrels.getDocIds()
    # cm[predicted][actual] = count
    cm = {c_pred: {c_real: 0 for c_real in classes_sorted} for c_pred in classes_sorted}
    for test_instance, entries in run.entries.items():
        predicted_classes = [docId for docId, _, _ in entries]
        if not predicted_classes: continue
        real_classes = qrels.allJudgements[test_instance].keys()
        assert (len(predicted_classes) == 1 and len(real_classes) == 1)
        for pc in predicted_classes:
            for rc in real_classes:
                cm[pc][rc] += 1
    return cm


def precision_classification(run, qrels, detailed=False, conf_matrix=None):
    """
    Computes the precision of the result of a classification task.
    """
    cf = conf_matrix if conf_matrix is not None else confusion_matrix(run, qrels)
    precisions = {cl: 0 for cl in cf.keys()}
    for predicted_class, d in cf.items():
        precisions[predicted_class] = cf[predicted_class][predicted_class] / sum(tp_fp for tp_fp in d.values())
    return (sum(precisions.values())/len(precisions), precisions) if detailed else sum(precisions.values())/len(precisions)


def recall_classification(run, qrels, detailed=False, conf_matrix=None):
    """
    Computes the recall of the result of a classification task.
    """
    cf = conf_matrix if conf_matrix is not None else confusion_matrix(run, qrels)
    classes = cf.keys()
    recalls = {cl: 0 for cl in classes}
    for real_class in classes:
        recalls[real_class] = cf[real_class][real_class] / sum(
            cf[predicted_class][real_class] for predicted_class in classes)
    return (sum(recalls.values()) / len(recalls), recalls) if detailed else sum(recalls.values()) / len(recalls)


# #### multi topic metrics.

def precision_multitopic(run, qrels, detailed=False):
    """
    Computes the precision of a multitopic classifier.
    :param run:
    :type run:
    :param qrels:
    :type qrels:
    :return:
    :rtype: float
    """
    sum_precisions = 0.0
    count = 0
    if detailed: all_precisions = {}
    for instance, entries in run.entries.items():
        real_classes = set(qrels.allJudgements[instance].keys())
        predicted_classes = set(clazz for clazz, _, _ in entries)
        precision = (len(real_classes & predicted_classes) / len(predicted_classes)) if len(
            predicted_classes) > 0 else 0
        if detailed: all_precisions[instance] = precision
        sum_precisions += precision
        count += 1
    return (sum_precisions / count, all_precisions) if detailed else sum_precisions / count


def recall_multitopic(run, qrels, detailed=False):
    """
    Computes the recall of a multitopic classifier.
    :param run:
    :type run:
    :param qrels:
    :type qrels:
    :return:
    :rtype: float
    """
    sum_recalls = 0.0
    count = 0
    if detailed: all_recalls = {}
    for instance, entries in run.entries.items():
        real_classes = set(qrels.allJudgements[instance].keys())
        predicted_classes = set(clazz for clazz, _, _ in entries)
        recall = (len(real_classes & predicted_classes) / len(real_classes))
        sum_recalls += recall
        if detailed: all_recalls[instance] = recall
        count += 1
    return (sum_recalls / count, all_recalls) if detailed else sum_recalls / count


def accuracy_multitopic(run, qrels, detailed=False):
    """
    Computes the accuracy of a multitopic classifier.
    :param run:
    :type run:
    :param qrels:
    :type qrels:
    :return:
    :rtype: float
    """
    sum_accuracies = 0.0
    count = 0
    if detailed: all_accuracies = {}
    for instance, entries in run.entries.items():
        real_classes = set(qrels.allJudgements[instance].keys())
        predicted_classes = set(clazz for clazz, _, _ in entries)
        accuracy = (len(real_classes & predicted_classes) / len(real_classes | predicted_classes))
        sum_accuracies += accuracy
        if detailed: all_accuracies[instance] = accuracy
        count += 1
    return (sum_accuracies / count, all_accuracies) if detailed else sum_accuracies / count


def exact_match_ratio(run, qrels, detailed=False):
    """
    Computes the exact match ration
    :param run:
    :type run:
    :param qrels:
    :type qrels:
    :return:
    :rtype: float
    """
    count_matches = 0.0
    count = 0
    if detailed: all_emr = {}
    for instance, entries in run.entries.items():
        real_classes = set(qrels.allJudgements[instance].keys())
        predicted_classes = set(clazz for clazz, _, _ in entries)
        if real_classes == predicted_classes:
            count_matches += 1
            if detailed: all_emr[instance] = 1
        count += 1
    return (count_matches / count, all_emr) if detailed else count_matches / count


def retrieval_fscore(run, qrels, detailed=False):
    """
    Computes the retrieval_FScore fore each class.
    :param run:
    :type run:
    :param qrels:
    :type qrels:
    :return: a dictionary mapping class -> FScore if detailed, its avg, otherwise.
    :rtype: dict
    """
    all_classes = qrels.getDocIds()
    num_byclass = {clazz: 0.0 for clazz in all_classes}
    denom_byclass = {clazz: 0.0 for clazz in all_classes}
    for instance, entries in run.entries.items():
        real_classes = set(qrels.allJudgements[instance].keys())
        predicted_classes = set(clazz for clazz, _, _ in entries)
        for clazz in all_classes:
            if clazz in real_classes and clazz in predicted_classes:
                num_byclass[clazz] += 1
            if clazz in real_classes:
                denom_byclass[clazz] += 1
            if clazz in predicted_classes:
                denom_byclass[clazz] += 1
    result = {clazz: 2 * num_byclass[clazz] / denom_byclass[clazz] for clazz in all_classes}
    avg = sum(result.values()) / len(result)
    return (avg, result) if detailed else avg

