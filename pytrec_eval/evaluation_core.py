import sys
import pytrec_eval as evaluation

from scipy import stats
__author__ = 'alberto'

DUMMY_DOCID = 'NO-DOCID'


class TrecRun:
    """Represents a TREC-like run."""

    #Collects the entries of the run:
    #runEntries[topicID] = [ (docID, score, annotation) ] sorted by score
    entries = None

    name = None

    def __init__(self, source, name = ''):
        """Builds a type-run starting from a file (if source is a string containing a file name)
        or from another dictionary source[topicID] = [ (docID, score, annotation) ] (the list of docID, scores
        may be not sorted)."""
        if type(source) == str:
            self._parseFile(source)
            self.name = name if name != '' else source[source.rfind('/')+1:]
        elif type(source) == dict:
            self.entries = source
            self.name = name
        else:
            raise RuntimeError("Wrong parameter for TrecRun's constructor. Accepted str and dict, given", type(source))

        for topicId, entryList in self.entries.items():
            entryList.sort(key = lambda x: x[1], reverse = True)

    def _parseFile(self, source):
        self.entries = {}
        f = open(source, 'r', encoding='utf-8')
        for line in f:
            line = line.strip()
            if line == "": continue
            splitLine = line.split('\t')
            if len(splitLine) == 6:
                topicId, Q0, docId, rank, score, annotation = splitLine
            elif len(splitLine) == 5:
                topicId, Q0, docId, rank, score = splitLine
                annotation = ''
            else:
                raise BaseException('Unparsable run')
            score = float(score)
            if topicId not in self.entries: self.entries[topicId] = []
            self.entries[topicId].append((docId, score, annotation))
        f.close()

    def getEntriesBy(self, topicId):
        """Returns all entry for the specified topicID"""
        return [] if topicId not in self.entries else self.entries[topicId]

    def getScore(self, topicId, docId):
        """Get the score of a specified pair topicId, docId"""
        scores = [score for did, score in self.entries[topicId] if did == docId]
        if scores == []: raise KeyError('Invalid docId for topic "' + topicId + '"')
        return scores[0]

    def getTopicIds(self):
        """Returns all topicIDs"""
        return self.entries.keys()

    def removeEntries(self, topicId):
        """Removes all the entries referring to topicId."""
        self.entries.pop(topicId, '')

    def write(self, outStream = sys.stdout):
        """Writes the run in the specified stream using TREC-format"""
        for topicId, entryList in self.entries.items():
            for (rank, (docId, score, annotation)) in enumerate(entryList, start=1):
                outStream.write('{}\tQ0\t{}\t{}\t{}\t{}\n'.format(topicId, docId, rank, score, annotation) )

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'TrecRun ' + self.name


class QRels:
    """ Contains relevance judgements in TREC format.
    Relevance scores are floating points values.
     A score > 0 means that a document is relevant;
     0 means that it's not relevant;
    -1 means it should be judged (but it's not).
    A score value in [0, 1] has to be intended as the probability of a document to be relevant.
    In this case the method isRelevant returns false.
    This last option is used mainly for computing infAP.
    """

    # a dictionary allJudgements[topicID][docID] = relevanceScore
    allJudgements = None

    def __init__(self, judgements):
        """Initialises the QRels starting from a dictionary
        judgements[topicID][docID] = relevanceScore, if judgements is such a dictionary;
        or from an existing qrels file, if judgements is a string containing the file-name."""
        self.allJudgements = {}
        if type(judgements) == str:
            self.allJudgements = {}
            self._parseFile(judgements)
        elif type(judgements) == dict:
            self.allJudgements = judgements
        else:
            raise RuntimeError("QRels.__init__ accepts exactly one argument (either string or dictionary).")

    def getNRelevant(self, topicId):
        """Returns the number of relevant documents for the specified topicID"""
        if topicId not in self.allJudgements: return 0
        return len( [t for t, relevance in self.allJudgements[topicId].items() if relevance >= 1 ] )

    def isRelevant(self, topicId, docId):
        """Returns True if typeURI is relevant for entityURI in the context proposed in docID.
        If a triple (docId, entityURI, typeURI) is not present in the qrels it returns False."""
        try:
            return self.allJudgements[topicId][docId] >= 1
        except KeyError:
            return False

    def getAllRelevants(self, topicId):
        """ Returns a set containing all relevants docIds for the specified topic"""
        return { docId for docId, score in self.allJudgements[topicId].items()
                 if score >= 1 }

    def getRelevanceScore(self, topicId, docId):
        """Returns the relevance score of docId for topicId.
        If a tuple (topicId, docId) is not contained in the qrels returns None."""
        try:
            return self.allJudgements[topicId][docId]
        except KeyError:
            return None

    def getRelevanceScores(self, topicId, docIds, nonJudged=0):
        """Like getRelevanceScore but now typeURIs is a list of URIs.
        The method returns a LIST of relevance scores referring to each element of typeURIs.
        If there is no relevance judgement for a certain couple (topicId, docIds) a nonJudged is added
        to the list."""
        try:
            return [ nonJudged if not ( topicId in self.allJudgements and docId in self.allJudgements[topicId])
                     else self.allJudgements[topicId][docId]
                     for docId in docIds ]
        except KeyError:
            return []

    def getTopicIds(self):
        return self.allJudgements.keys()

    def getNTopics(self):
        """Returns the number of topics"""
        return len(self.allJudgements)

    def write(self, streamOut):
        """Writes the qrels into a stream using TREC-format for qrels"""
        for topicId, dictDocs in self.allJudgements.items():
            for docId, relevanceScore in dictDocs.items():
                streamOut.write( '{}\t0\t{}\t{}\n'.format(topicId, docId, relevanceScore) )

    def _parseFile(self, otherQRelsPath):
        """Initialises the structure by reading and existing trelsFile"""
        fQRels = open(otherQRelsPath, 'r', encoding='utf-8')
        for line in fQRels:
            line = line.strip()
            if line == '': continue
            split = line.split('\t')
            topicId, docId, relevanceScore = split[0], split[2], float(split[3])

            if topicId not in self.allJudgements:
                self.allJudgements[topicId] = {}
            self.allJudgements[topicId][docId] = relevanceScore
        fQRels.close()
