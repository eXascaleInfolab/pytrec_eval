import sys
import pytrec_eval

__author__ = 'alberto'


def evaluate(run, qrels, measures=pytrec_eval.STD_METRICS, detailed=False):
    """Evaluates a TREC-run by using the specified qrels to compute the given measures.
    Measure is a list of functions.
    If detailed is True then the value of each measure is reported for each topic."""
    if type(measures) == list:
        results = []
        for measure in measures:
            results.append(measure(run, qrels, detailed))
    else:
        results = measures(run, qrels, detailed)
    return results


def evaluateAll(runs, qrels, measures=pytrec_eval.STD_METRICS, streamOut=sys.stdout):
    """Evaluates all the runs contained in runs (a list of runs).
    Prints the result of the evaluation in streamOut."""
    mList = [pytrec_eval.METRICS_NAMES[measure] for measure in measures]

    print('run name', end='\t', file=streamOut)
    for m in mList: print(m, end='\t', file=streamOut)
    print('')

    for run in runs:
        results = evaluate(run, qrels, measures)
        print(run.name, end='\t', file=streamOut)
        for m in results: print(m, sep='', end='\t', file=streamOut)
        print('')


def writeAll(runList, outputDir):
    """writes all the runs into TREC-run files placed in outputDir"""
    for run in runList:
        f = open(outputDir + '/' + run.name, 'w', encoding='utf-8')
        run.write(f)
        f.close()


def loadAll(runFilenames):
    """Load all runs in the list runFilenames and returns a list of TrecRun s."""
    return [pytrec_eval.TrecRun(name) for name in runFilenames]


def showRelevanceScores(trecRun, qrels, topicId, top_n=10, file=sys.stdout):
    """
    shows relevance scores for the top_n entries of trecrun for topicId
    """
    for rank, (docId, _, _) in enumerate(trecRun.getEntriesBy(topicId), start=1):
        if rank > top_n: break
        print(topicId, rank, docId,
              qrels.getRelevanceScore(topicId, docId) if docId in qrels.allJudgements[topicId] else '?',
              sep='\t', file=file)
