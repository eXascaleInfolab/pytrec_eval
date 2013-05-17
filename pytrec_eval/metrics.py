import math

__author__ = 'alberto'

#"""Contains all metrics.
#A metric is a function f(TRun, TRels) that returns a double.
#We suppose that each entity has a judgement."""

def precision(run, qrels, detailed = False):
    """Computes average precision among all entities."""
    details = {}
    avg = 0
    for topicId, entryList in run.entries.items():
        numRelevant = len([ docId for docId, score, _ in entryList
                            if qrels.isRelevant(topicId, docId) ])
        numReturned = len(entryList)
        details[topicId] = numRelevant / numReturned
        avg += numRelevant / numReturned
    numTopics = qrels.getNTopics()
    return avg / numTopics if not detailed else (avg / numTopics, details)

def recall(run, qrels, detailed = False):
    """Computes average recall among all entities"""
    details = {}
    avg = 0
    for topicId, entryList in run.entries.items():
        numRelevantFound = len([ docId for docId, score, _ in entryList
                                 if qrels.isRelevant(topicId, docId) ])
        numRelevant = qrels.getNRelevant(topicId)
        details[topicId] = numRelevantFound / numRelevant
        avg += numRelevantFound / numRelevant
    numtopics = qrels.getNTopics()
    return avg / numtopics if not detailed else (avg / numtopics, details)

def avgPrec(run, qrels, detailed = False):
    """Computes average recall among all entities"""
    details = {}
    avg = 0
    for topicId, entryList in run.entries.items():
        sumPrec = numRel = rank = 0
        for (rank, (docId, score, _)) in enumerate(entryList, start=1):
            if qrels.isRelevant(topicId, docId):
                numRel += 1
                sumPrec += numRel / rank
        totRelevant = qrels.getNRelevant(topicId)
        #if totRelevant == 0: print(topicId)
        ap = sumPrec / totRelevant if totRelevant > 0 else 0
        avg += ap
        details[topicId] = ap
    numtopics = qrels.getNTopics()
    return avg / numtopics if not detailed else (avg / numtopics, details)

def precisionAt(rank):
    def precisionAtRank(run, qrels, detailed = False):
        details = {}
        avg = 0
        for topicId, entryList in run.entries.items():
            numRelevant = len([ docId for docId, score, _ in entryList[0 : rank]
                                if qrels.isRelevant(topicId, docId) ])
            details[topicId] = numRelevant / rank
            avg += numRelevant / rank
        numtopics = qrels.getNTopics()
        return avg / numtopics if not detailed else (avg / numtopics, details)
    return precisionAtRank

def ndcg(run, qrels, detailed = False):
    details = {}
    avg = 0
    for topicId, entryList in run.entries.items():
        relevancesByRank = qrels.getRelevanceScores( topicId, [doc for (doc, _, _) in entryList] )
        sumdcg = relevancesByRank[0] + sum( [ relScore / math.log2(rank)
                                              for rank, relScore in enumerate(relevancesByRank[1:], start=2)] )
        #sumdcg = sum( [ (2**relScore - 1) / math.log2(rank+1)
        #                for rank, relScore in enumerate(relevancesByRank, start=1)] )
        relevancesByRank.sort(reverse = True) # sort the relevance list descending order
        sumIdcg = relevancesByRank[0] + sum( [ relScore / math.log2(rank)
                                               for rank, relScore in enumerate(relevancesByRank[1:], start=2)] )
        #sumIdcg = sum( [ (2**relScore - 1) / math.log2(rank+1)
        #                   for rank, relScore in enumerate(relevancesByRank, start=1)] )
        if sumIdcg == 0: print(topicId, relevancesByRank)
        details[topicId] = sumdcg / sumIdcg
        avg += sumdcg / sumIdcg
    numtopics = qrels.getNTopics()
    return avg / numtopics if not detailed else (avg / numtopics, details)

STD_METRICS = { 'MAP' : avgPrec, 'NDCG' : ndcg }