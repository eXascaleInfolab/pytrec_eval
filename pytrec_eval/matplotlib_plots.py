import matplotlib.pyplot as plt

import pytrec_eval


__author__ = 'alberto'


def plotEvaluation(trecRun, qrels, measure, outputFile=None, showPlot=True):
    """
    Plots an histogram with one bar per topic.
    Each bar represents the difference between measure computed on the topic
    and the average measure among all topics.
    If outputFile is a string specifying the name of a file, then the plot
    is saved into that file.
    If showPlot then the plot is shown to the user (but not necessarily stored
     into a file).
    """
    plt.clf()
    avg, details = pytrec_eval.evaluate(trecRun, qrels, measure, True)
    # to be sure that qId order is the same of score order (maybe it's not necessary...)
    lstDetails = [(qId, score) for qId, score in details.items()]
    lstDetails.sort(key=lambda x: x[0])
    qIds = [qId for qId, _ in lstDetails]
    scores = [score - avg for _, score in lstDetails]
    plt.figure(1)
    x = [i for i in range(len(qIds))]  # np.arange(len(qIds))
    plt.bar(x, scores, width=0.6)
    plt.xticks(x, qIds, rotation=90, size=5)
    plt.xlim(xmax=len(qIds))
    plt.xlabel('Topic Id')
    plt.ylabel('Difference of ' + pytrec_eval.METRICS_NAMES[measure] + ' from Average')
    if showPlot: plt.show()
    if outputFile is not None: plt.savefig(outputFile, bbox_inches=0)


def _recallPrecisionPerTopic(trecRun, qrels, topicId):
    """
    Computes interpolate precision for all recall levels in _recallLevels.
    Returns a list containing the interpolated precisions.
    """
    entries = trecRun.getEntriesBy(topicId)
    intPrecisions = [0] * 11  # contains max precision for each level of recall
    retrievedRelevants, allRelevants = 0, qrels.getNRelevant(topicId)
    for rank, (docId, _, _) in enumerate(entries, start=1):
        if qrels.isRelevant(topicId, docId): retrievedRelevants += 1
        currentRecall = retrievedRelevants / allRelevants
        currentPrecision = retrievedRelevants / rank

        recallLevel = int(currentRecall * 10)
        # print('currentRecall:', currentRecall, 'currentPrecision:', currentPrecision, 'recallLevel:', recallLevel)
        if currentPrecision > intPrecisions[recallLevel]: intPrecisions[recallLevel] = currentPrecision
        if currentRecall == (recallLevel / 10) > 0 and intPrecisions[recallLevel - 1] < currentPrecision:
            intPrecisions[recallLevel - 1] = currentPrecision
    return [max(intPrecisions[rank:]) for rank, _ in enumerate(intPrecisions)]


def plotRecallPrecisionAll(trecRuns, qrels, outputFile=None, showPlot=True):
    """
    Plots a recall/precision graphs showing the precision/recall curves of all the runs contained in trecRuns.
    If outputFile contains a file name, then the plot is printed in the specified file.
    If showPlot is True then the plot is shown to the user before the termination of the function.
    """
    plt.clf()
    plt.figure(1)

    for trecRun in trecRuns:
        _plotRecallPrecision(trecRun, qrels, perQuery=False)
    plt.title('Recall/Precision chart')
    plt.legend()

    if outputFile is not None: plt.savefig(outputFile, bbox_inches=0)
    if showPlot: plt.show()


def plotRecallPrecision(trecRun, qrels, perQuery=False, outputFile=None, showPlot=True):
    """
    Plots a recall/precision graphs showing the precision/recall curve of the given TrecRun.
    If perQuery is True then a dashed precision/recall curve is drawn for each topic together
    with the solid precision/recall curve obtained by averaging precision at each recall point
    among all topics.
    If outputFile contains a file name, then the plot is printed in the specified file.
    If showPlot is True then the plot is shown to the user before the termination of the function.
    """
    plt.clf()
    plt.figure(1)
    _plotRecallPrecision(trecRun, qrels, perQuery)
    if outputFile is not None: plt.savefig(outputFile, bbox_inches=0)
    if showPlot: plt.show()


def _plotRecallPrecision(trecRun, qrels, perQuery=False):
    avgs = [0] * 11
    recallLevels = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for tId in qrels.getTopicIds():
        intPrec = _recallPrecisionPerTopic(trecRun, qrels, tId)
        avgs = map(lambda x, y: x + y, avgs, intPrec)
        if perQuery: plt.plot(recallLevels, intPrec, '--', label=tId)

    nquery = qrels.getNTopics()
    avgs = [avg / nquery for avg in avgs]
    if perQuery:
        plt.plot(recallLevels, avgs, 'r-', lw=2, label='Average')
    else:
        plt.plot(recallLevels, avgs, label=trecRun.name)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Recall/Precision chart for ' + trecRun.name)