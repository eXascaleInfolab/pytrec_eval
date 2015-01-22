__author__ = 'alberto'


def confusion_matrix(run, qrels):
    """
    Compute the confusion matrix.
    The case in which there is more than a class associated both in the
    predictions and in the ground truth is handled by filling all
    the positions correspondings to all the pairs (predicted, real).
    For example if for an instance the predictions are a, b and
    the real values are a, c, then all the cells
    (a, a), (a, c), (b, a), (b, c) are updated.
    :returns a 2d-dictionary cm[predicted][real] = count
    """
    classes_sorted = qrels.getDocIds()
    # cm[predicted][actual] = count
    cm = {c_pred: {c_real: 0 for c_real in classes_sorted} for c_pred in classes_sorted}
    for test_instance, entries in run.entries.items():
        predicted_classes = [docId for docId, _, _ in entries]
        if predicted_classes == []: continue
        real_classes = qrels.allJudgements[test_instance].keys()
        for pc in predicted_classes:
            for rc in real_classes:
                cm[pc][rc] += 1
    return cm


def precision_classification(run, qrels, conf_matrix=None):
    """
    Computes the precision of the result of a classification task.
    """
    cf = conf_matrix if conf_matrix != None else confusion_matrix(run, qrels)
    precisions = {cl: 0 for cl in cf.keys()}
    for predicted_class, d in cf.items():
        precisions[predicted_class] = cf[predicted_class][predicted_class] / sum(tp_fp for tp_fp in d.values())
    return precisions


def recall_classification(run, qrels, conf_matrix=None):
    """
    Computes the recall of the result of a classification task.
    """
    cf = conf_matrix if conf_matrix != None else confusion_matrix(run, qrels)
    classes = cf.keys()
    recalls = {cl: 0 for cl in classes}
    for real_class in classes:
        recalls[real_class] = cf[real_class][real_class] / sum(cf[predicted_class][real_class] for predicted_class in classes)
    return recalls