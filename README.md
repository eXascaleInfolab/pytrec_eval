pytrec_eval
===========

A (tiny) library to evaluate TREC-like runs by using TREC-like qrels. 
Implements Kendall's tau similarity of rankings, t-test between runs etc…
In particular, (for the moment) the implemented metrics are: Average Precision (AP), Normalized Discounted Cumulative Gain (NDCG), Precision, Recall, Precision@k.
All the functions implementing metrics are contained in the module pytrec_eval.metrics.

Basic usage:

* use the class TrecRun to load a TREC-run from a file

`run = pytrec_eval.TrecRun(<fileName>)`


* you can also use loadAll to load all TREC-runs contained in a list of file names.

`runs = pytrec_eval.loadAll(['run1', 'run2', 'run3'])`


* use the class QRels to load the qrels from a file

`qrels = pytrec_eval.QRels(<fileName>)`


Evaluation
----------

* Use evaluate (resp., evaluateAll) to evaluate a run (resp., list of runs)

`pytrec_eval.evaluate(run, qrels, metrics)`

where metrics can be either a list of functions computing some metrics, for example, 
`[pytrec_eval.avgPrec, pytrec_eval.ndcg]`
or a dictionary mapping metrics names to the function that computes the metrics, for example,
`{ 'MAP' : pytrec_eval.avgPrec, 'NDCG' : pytrec_eval.ndcg }`.


* It is possible to compute the *ranking* of a list of runs by using pytrec_eval.rankRuns as follows:

`ranking = pytrec_eval(<list of TrecRuns>, qrels, measure)`

where measure is a function that computes some metrics (have a look to pytrec_eval.metrics to get the list of the implemented measures). 
A ranking is a list of pairs (TrecRun, score) ordered by decreasing score.


Statistical Tools
-----------------

* pytrec_eval features a function that computes the *Student's t-test* between a run and a list of other runs, for example, 

`pValues = pytrec_eval.ttest(run0, [run1, run2], qrels, pytrec_eval.ndcg)`

returns a dictionary mapping the name of run1 to the p-value obtained by comparing the NDCG score of run1 to the NDCG score of run0, and the name of run2 to the p-value obtained by comparing the NDCG score of run2 to the NDCG score of run0. 


* Given two rankings it is possible to compute the *Kendall's tau correlation* between them as follows:

`tau = pytrec_eval.rankSimilarity(ranking0, ranking1)`

where ranking0 and ranking1 are lists of pairs (TrecRun, score) ordered by decreasing score.


For more functions/details, please check the documentation strings in the Python source code. 
