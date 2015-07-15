import sys

__author__ = 'alberto'


class TrecRun:
    """Represents a TREC-like run."""

    # Collects the entries of the run:
    # runEntries[topicID] = [ (docID, score, annotation) ] sorted by score
    entries = None

    name = None

    def __init__(self, source, name=''):
        """Builds a type-run starting from a file (if source is a string containing a file name)
        or from another dictionary source[topicID] = [ (docID, score, annotation) ] (the list of docID, scores
        may be not sorted)."""
        if type(source) == str:
            self._parseFile(source)
            self.name = name if name != '' else self._extract_runname(source)
        elif type(source) == dict:
            self.entries = source
            self.name = name
        else:
            raise RuntimeError("Wrong parameter for TrecRun's constructor. Accepted str and dict, given", type(source))

        for topicId, entryList in self.entries.items():
            entryList.sort(key=lambda x: x[1], reverse=True)

    def _extract_runname(self, filename):
        if filename.endswith('.trecrun'):
            return filename[filename.rfind('/') + 1: filename.rfind('.')]
        else:
            return filename

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

    def restrictTopicsTo(self, qrels):
        """
        Remove all topics that are not in qrels
        :param qrels:
        :type qrels: pytrec_eval.QRels
        :return:
        """
        good_topics = set(qrels.getTopicIds())
        bad_topics = [run_topic for run_topic in self.getTopicIds() if run_topic not in good_topics]
        for t in bad_topics:
            self.removeEntries(t)

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

    def write(self, outStream=sys.stdout):
        """Writes the run in the specified stream using TREC-format"""
        for topicId, entryList in self.entries.items():
            for (rank, (docId, score, annotation)) in enumerate(entryList, start=1):
                outStream.write('{}\tQ0\t{}\t{}\t{}\t{}\n'.format(topicId, docId, rank, score, annotation))

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'TrecRun ' + self.name
