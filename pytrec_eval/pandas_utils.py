__author__ = 'alberto'

import pandas as pd
from pytrec_eval.utils import *


def df_evaluate(run, qrels, measures):
    if type(measures) == list:
        details = evaluate(run, qrels, measures, True)
        return pd.DataFrame({m.__name__: pd.Series(details[i][1]) for i, m in enumerate(measures)})
    else:
        _, details = evaluate(run, qrels, measures, True)
        return pd.DataFrame({run.name: pd.Series(details)})


def df_evaluateAll(runs, qrels, measures):
    if type(measures) == list:
        data = {metrics.__name__: [evaluate(run, qrels, metrics, False) for run in runs] for metrics in measures}
        return pd.DataFrame(data, index=[run.name for run in runs])
    else:
        series = {run.name: pd.Series(evaluate(run, qrels, measures, True)[1]) for run in runs}
        return pd.DataFrame(series)


def df_relevanceScores(trecRun, qrels, top_n=10):
    return pd.DataFrame([[topicId, rank, docId, ann,
                          qrels.getRelevanceScore(topicId, docId) if docId in qrels.allJudgements[topicId] else -1]
                         for topicId in trecRun.entries
                         for rank, (docId, _, ann) in enumerate(trecRun.getEntriesBy(topicId), start=1) if
                         rank <= top_n],
                        columns=['topicId', 'rank', 'docId', 'annotation', 'relevance_score'])
