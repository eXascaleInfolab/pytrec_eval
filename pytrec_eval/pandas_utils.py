__author__ = 'alberto'

import pandas as pd
from pytrec_eval.utils import *


def df_evaluate(run, qrels, measures, details=False):
    """
    Evaluates a the given run with the given qrels by computing the
    measures given as input.
    The output is a DataFrame containing the result of the evaluation.
    :param run:
    :param qrels:
    :param measures: either a list of metrics or a single metric.
    In the first case, the resulting dataframe has one row per metric and the result is the average over all topics;
    In the latter case, the resulting dataframe has one row per topic and one column reporting the value
    of the metrics for the topic.
    :return:
    """
    if not details:
        if type(measures) == list:
            details = evaluate(run, qrels, measures)
            d = {m.__name__: pd.Series(details[i]) for i, m in enumerate(measures)}
            return pd.DataFrame(d)
        else:
            avg = evaluate(run, qrels, measures)
            return pd.DataFrame({measures.__name__: [avg]})
    else:
        if type(measures) == list:
            details = evaluate(run, qrels, measures, True)
            return pd.DataFrame({m.__name__: pd.Series(details[i][1]) for i, m in enumerate(measures)})
        else:
            _, details = evaluate(run, qrels, measures, True)
            return pd.DataFrame({run.name: pd.Series(details)})


def df_evaluateAll(runs, qrels, measures):
    """
    Evaluates all the runs given as input with the given qrels by evaluating all the provided measures.
    The output is a DataFrame containing the result of the evaluation.

    :param runs: a list of runs
    :param qrels:
    :param measures: either a list of metrics or a single metric.
    In the first case, the resulting dataframe has one row per run and one column per metric
    In the latter case, the resulting dataframe has one row per topic and one column reporting the value
    of the metrics for the topic.
    :return:
    :rtype:
    """
    if type(measures) == list:
        data = {metrics.__name__: [evaluate(run, qrels, metrics, False) for run in runs] for metrics in measures}
        return pd.DataFrame(data, index=[run.name for run in runs])
    else:
        series = {run.name: pd.Series(evaluate(run, qrels, measures, True)[1]) for run in runs}
        return pd.DataFrame(series)


def df_relevanceScores(trecRun, qrels, top_n=10):
    """
    Outputs a DataFrame with the relevance scores for the top_n entries of trecrun for each topic
    """
    return pd.DataFrame([[topicId, rank, docId, ann,
                          qrels.getRelevanceScore(topicId, docId) if docId in qrels.allJudgements[topicId] else -1]
                         for topicId in trecRun.entries
                         for rank, (docId, _, ann) in enumerate(trecRun.getEntriesBy(topicId), start=1) if
                         rank <= top_n],
                        columns=['topicId', 'rank', 'docId', 'annotation', 'relevance_score'])
