__author__ = 'alberto'
import pygal
from pygal.style import BlueStyle, LightGreenStyle
import pytrec_eval

__author__ = 'alberto'

PLOT_STYLE = LightGreenStyle
PLOT_STYLE.background = 'transparent'


def plotDifferenceFromAvg(trecRun, qrels, measure, outputFile, style=PLOT_STYLE):
    """
    Plots an histogram with one bar per topic.
    Each bar represents the difference between measure computed on the topic
    and the average measure among all topics.
    OutputFile is a string specifying the name of the file the plot
    is saved into.
    """

    avg, details = pytrec_eval.evaluate(trecRun, qrels, measure, True)
    # to be sure that qId order is the same of score order (maybe it's not necessary...)
    bar_chart = pygal.Bar()
    bar_chart.style = style
    lstDetails = [(qId, score) for qId, score in details.items()]
    lstDetails.sort(key=lambda x: x[0])
    qIds = [qId for qId, _ in lstDetails]
    scores = [score - avg for _, score in lstDetails]
    bar_chart.add(trecRun.name, scores)

    bar_chart.label_font_size = 8
    bar_chart.legend_at_bottom = True
    bar_chart.legend_font_size = 10
    bar_chart.legend_box_size = 8

    bar_chart.x_label_rotation = 90
    bar_chart.x_labels = qIds
    bar_chart.x_title = 'query ids'
    bar_chart.y_title = 'Difference of ' + pytrec_eval.METRICS_NAMES[measure] + ' from Average'
    bar_chart.render_to_file(outputFile)


def plotEvaluation(trecRun, qrels, measure, outputFile, style=PLOT_STYLE):
    """
    Plots an histogram with one bar per topic.
    Each bar represents the difference between measure computed on the topic
    and the average measure among all topics.
    OutputFile is a string specifying the name of the file the plot
    is saved into.
    """

    avg, details = pytrec_eval.evaluate(trecRun, qrels, measure, True)
    # to be sure that qId order is the same of score order (maybe it's not necessary...)
    bar_chart = pygal.Bar()
    bar_chart.style = style
    lstDetails = [(qId, score) for qId, score in details.items()]
    lstDetails.sort(key=lambda x: x[0])
    qIds = [qId for qId, _ in lstDetails]
    scores = [score for _, score in lstDetails]
    bar_chart.add(trecRun.name, scores)

    bar_chart.label_font_size = 8
    bar_chart.legend_at_bottom = True
    bar_chart.legend_font_size = 10
    bar_chart.legend_box_size = 8

    bar_chart.x_label_rotation = 90
    bar_chart.x_labels = qIds
    bar_chart.x_title = 'query ids'
    bar_chart.y_title = 'Difference of ' + pytrec_eval.METRICS_NAMES[measure] + ' from Average'
    bar_chart.render_to_file(outputFile)


def plotEvaluationAll(trecRuns, qrels, measure, outputFile, style=PLOT_STYLE):
    """
    Plots an histogram with one bar per topic.
    Each bar represents the difference between measure computed on the topic
    and the average measure among all topics.
    OutputFile is a string specifying the name of the file the plot
    is saved into.
    """
    qIds = list(qrels.getTopicIds())
    qIds.sort()

    bar_chart = pygal.Bar()
    # bar_chart.spacing = 50
    bar_chart.label_font_size = 8
    bar_chart.style = style
    bar_chart.x_label_rotation = 90
    bar_chart.x_labels = qIds
    bar_chart.x_title = 'Topic Id'
    bar_chart.legend_at_bottom = True
    bar_chart.legend_font_size = 10
    bar_chart.legend_box_size = 8

    bar_chart.y_title = pytrec_eval.METRICS_NAMES[measure]

    for trecRun in trecRuns:
        avg, details = pytrec_eval.evaluate(trecRun, qrels, measure, True)
        lstDetails = [details[topicId] if topicId in details else 0 for topicId in qIds]
        bar_chart.add(trecRun.name, lstDetails)

    bar_chart.render_to_file(outputFile)


def _recallPrecisionPerTopic(trecRun, qrels, topicId):
    """
    Computes interpolate precision for all recall levels in _recallLevels.
    Returns a list containing the interpolated precisions.
    """
    entries = trecRun.getEntriesBy(topicId)
    intPrecisions = [0] * 11  #contains max precision for each level of recall
    retrievedRelevants, allRelevants = 0, qrels.getNRelevant(topicId)
    for rank, (docId, _, _) in enumerate(entries, start=1):
        if qrels.isRelevant(topicId, docId): retrievedRelevants += 1
        currentRecall = retrievedRelevants / allRelevants
        currentPrecision = retrievedRelevants / rank

        recallLevel = int(currentRecall * 10)
        #print('currentRecall:', currentRecall, 'currentPrecision:', currentPrecision, 'recallLevel:', recallLevel)
        if currentPrecision > intPrecisions[recallLevel]: intPrecisions[recallLevel] = currentPrecision
        if currentRecall == (recallLevel / 10) > 0 and intPrecisions[recallLevel - 1] < currentPrecision:
            intPrecisions[recallLevel - 1] = currentPrecision
    return [max(intPrecisions[rank:]) for rank, _ in enumerate(intPrecisions)]


def plotRecallPrecision(trecRun, qrels, outputFile, perQuery=False, style=PLOT_STYLE):
    line_chart = pygal.Line()
    # line_chart.human_readable = True
    line_chart.legend_at_bottom = True
    line_chart.legend_font_size = 10
    line_chart.legend_box_size = 8
    line_chart.style = style
    line_chart.x_title = 'Recall'
    line_chart.y_title = 'Precision'
    line_chart.title = 'Recall/Precision chart for ' + trecRun.name
    line_chart.x_labels = [str(i) for i in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]

    _plotRecallPrecision(trecRun, qrels, outputFile, line_chart, perQuery)


def _plotRecallPrecision(trecRun, qrels, outputFile, line_chart, perQuery=False):
    """
    Plots a recall/precision graphs showing the precision/recall curve of the given TrecRun.
    If perQuery is True then a dashed precision/recall curve is drawn for each topic together
    with the solid precision/recall curve obtained by averaging precision at each recall point
    among all topics.
    If outputFile contains a file name, then the plot is printed in the specified file.
    If showPlot is True then the plot is shown to the user before the termination of the function.
    """
    avgs = [0] * 11
    for tId in qrels.getTopicIds():
        intPrec = _recallPrecisionPerTopic(trecRun, qrels, tId)
        avgs = map(lambda x, y: x + y, avgs, intPrec)
        if perQuery: line_chart.add(tId, intPrec)

    nquery = qrels.getNTopics()
    avgs = [avg / nquery for avg in avgs]
    if perQuery:
        line_chart.add('Average', avgs, )
    else:
        line_chart.add(trecRun.name, avgs)
    line_chart.render_to_file(outputFile)


def plotRecallPrecisionAll(trecRuns, qrels, outputFile, style=PLOT_STYLE):
    """
    Plots a recall/precision graphs showing the precision/recall curves of all the runs contained in trecRuns.
    If outputFile contains a file name, then the plot is printed in the specified file.
    If showPlot is True then the plot is shown to the user before the termination of the function.
    """
    line_chart = pygal.Line()
    # line_chart.human_readable = True
    # line_chart.show_legend = False
    line_chart.legend_at_bottom = True
    line_chart.x_labels = [str(i) for i in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]
    line_chart.style = style
    line_chart.legend_font_size = 10
    line_chart.legend_box_size = 8
    line_chart.x_title = 'Recall'
    line_chart.y_title = 'Precision'
    line_chart.title = 'Recall/Precision chart'

    for trecRun in trecRuns:
        _plotRecallPrecision(trecRun, qrels, outputFile, line_chart, False)
    line_chart.render_to_file(outputFile)


def plotDifferenceWith(targetRun, otherRuns, qrels, measure, outputFile, style=PLOT_STYLE):
    avg_baseline, baseline_scores = pytrec_eval.evaluate(targetRun, qrels, measure, True)

    bar_chart = pygal.Bar()
    bar_chart.style = style
    allTopics = list(qrels.getTopicIds())

    bar_chart.label_font_size = 8
    bar_chart.legend_at_bottom = True
    bar_chart.legend_font_size = 10
    bar_chart.legend_box_size = 8

    bar_chart.x_label_rotation = 90
    bar_chart.x_labels = allTopics
    bar_chart.x_title = 'Topic Id'
    bar_chart.y_title = 'Difference from ' + targetRun.name + ' (' + pytrec_eval.METRICS_NAMES[measure] + ')'

    for otherRun in otherRuns:
        _, other_scores = pytrec_eval.evaluate(otherRun, qrels, measure, True)
        points = [(other_scores[topicId] if topicId in other_scores else 0) - (baseline_scores[topicId] if topicId in baseline_scores else 0)
                  for topicId in allTopics]
        bar_chart.add(otherRun.name, points)
    bar_chart.render_to_file(outputFile)