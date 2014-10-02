__author__ = 'alberto'


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
        return len([t for t, relevance in self.allJudgements[topicId].items() if relevance >= 1])

    def isRelevant(self, topicId, docId):
        """Returns True if typeURI is relevant for entityURI in the context proposed in docID.
        If a triple (docId, entityURI, typeURI) is not present in the qrels it returns False."""
        try:
            return self.allJudgements[topicId][docId] >= 1
        except KeyError:
            return False

    def getAllRelevants(self, topicId):
        """ Returns a set containing all relevants docIds for the specified topic"""
        return {docId for docId, score in self.allJudgements[topicId].items()
                if score >= 1}

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
            return [nonJudged if not ( topicId in self.allJudgements and docId in self.allJudgements[topicId])
                    else self.allJudgements[topicId][docId]
                    for docId in docIds]
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
                streamOut.write('{}\t0\t{}\t{}\n'.format(topicId, docId, relevanceScore))

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