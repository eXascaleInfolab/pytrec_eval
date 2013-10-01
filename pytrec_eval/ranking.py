__author__ = 'alberto'

import pytrec_eval
import scipy.stats as stats

def rankRuns(runs, qrels, measure):
    """Ranks the runs based on measure.
     Returns a list of pairs (run, score) ordered by
     score descending.
    """
    rank = [ (run, pytrec_eval.evaluate(run, qrels, [measure])[0]) for run in runs ]
    rank.sort(key= lambda x : x[1], reverse=True)
    return rank

def rankSimilarity(rank0, rank1):
    """
    Computes the Kendall's tau similarity between two rankings.
    rank0, rank1 are rankings, that is, lists of pairs (run, score)
    ordered by score descending, such that, for example, rank0[0] is the system
    with the best score in rank0.
    """
    rank0Dict = { run.name: position for position, (run, _) in enumerate(rank0) }
    rank0Ids = list(range(0, len(rank0)))
    rank1Ids = [ rank0Dict[run.name] for (run, _) in rank1 ]
    return stats.kendalltau(rank0Ids, rank1Ids)

