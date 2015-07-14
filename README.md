pytrec_eval
===========

A (tiny) library to evaluate TREC-like runs by using TREC-like qrels. 
Implements Kendall's tau similarity of rankings, t-test between runs etcetera.
Moreover, it is capable to output metrics for evaluating classification and clustering algorithms.
For the moment the implemented metrics are the following (partitioned by task):
- *Document Retrival*: Average Precision (AP), Normalized Discounted Cumulative Gain (NDCG), Precision, Recall, Precision@k.
- *Classification*: precision, recall, precision (multi-topic), recall (multi-topic), accuracy (multi-topic), exact match ratio, retrieval f-score.
- *Clustering*: purity, nmi, randin index, f-score.
All the functions implementing metrics are contained in the module pytrec_eval.metrics.

Loading Data
------------

* Use the class TrecRun to load a TREC-run from a file

`run = pytrec_eval.TrecRun(<fileName>)`


* you can also use loadAll to load all TREC-runs contained in a list of file names.

`runs = pytrec_eval.loadAll(['run1', 'run2', 'run3'])`


* use the class QRels to load the qrels from a file

`qrels = pytrec_eval.QRels(<fileName>)`


Evaluation
----------

* Use evaluate (resp., evaluateAll) to evaluate a run (resp., list of runs)

`pytrec_eval.evaluate(run, qrels, metrics)`

where `metrics` is a list of functions computing some metrics, for example, 
`[pytrec_eval.avgPrec, pytrec_eval.ndcg]`.


* It is possible to compute the **ranking** of a list of runs by using pytrec_eval.rankRuns as follows:

`ranking = pytrec_eval(<list of TrecRuns>, qrels, measure)`

where `measure` is a function that computes some metrics. 
A ranking is a list of pairs `(TrecRun, score)` ordered by decreasing score.


pytrec_eval can also creates plots:

* The function `plotDifferenceFromAvg` plots an histogram highlighting the performance of a run for each topic. It is possible to save the plot into a file by using the optional parameter `outputFile`.

`pytrec_eval.plotDifferenceFromAvg(trecRun, qrels, pytrec_eval.ndcg, outputFile='./ndcg.pdf', showPlot=True)`


* The function `plotRecallPrecision` plots the recall/precision curve of a given run.
It is also possible to have multiple recall/precision curves, one for each topic, by setting `perQuery = True`.

`pytrec_eval.plotRecallPrecision(trecRun, qrels, perQuery=True, outputFile='./recall-precision.pdf', showPlot=False)`


* The function `plotRecallPrecisionAll` plots the recall/precision curves of all runs contained in the input list of runs. 

`pytrec_eval.plotRecallPrecisionAll([run0, run1, run2], qrels, outputFile='./recall-precision-all.pdf', showPlot=False)`



Statistical Tools
-----------------

* pytrec_eval features a function that computes the **Student's t-test** between a run and a list of other runs, for example, 

`pValues = pytrec_eval.ttest(run0, [run1, run2], qrels, pytrec_eval.ndcg)`

returns a dictionary mapping the name of `run1` to the p-value obtained by comparing the NDCG score of `run1` to the NDCG score of `run0`, and the name of `run2` to the p-value obtained by comparing the NDCG score of `run2` to the NDCG score of `run0`. 


* Given two rankings it is possible to compute the **Kendall's tau correlation** between them as follows:

`tau = pytrec_eval.rankSimilarity(ranking0, ranking1)`

where `ranking0` and `ranking1` are lists of pairs `(TrecRun, score)` ordered by decreasing score.


For more functions/details, please check the documentation strings in the Python source code. 


Requirements
------------

* Python 3.3
* scipy (http://www.scipy.org/)
* numpy (http://www.numpy.org/)
* pygal (http://pygal.org/)

