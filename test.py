import unittest
from WordFrequenciesClass import WordFrequencies
from datetime import datetime
import argparse
from cStringIO import StringIO
import sys

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout
 
class TestUM(unittest.TestCase):
    wf = None
 
    @classmethod
    def setUpClass(self):
        self.wf = WordFrequencies()
        self.wf.mainSetup(argparse.Namespace(file='/Users/Dirk/Programming/Python/WordFrequencies/WordFrequencies/testjournal1.txt', 
            verbosity=False, combineplurals=False))

    @classmethod
    def tearDownClass(self):
        pass

    def test_classVariables(self):
        self.assertEqual(self.wf.firstDate, datetime(2014,12,1))
        self.assertEqual(self.wf.mostRecentDate, datetime(2017,12,31))
        self.assertEqual(self.wf.namesURL, "/Users/Dirk/Programming/Python/WordFrequencies/WordFrequencies/names.txt")
        self.assertEqual(self.wf.totalNumberOfWords, 51)


    def test_journalParsing(self):
        self.assertEqual(len(self.wf.wordCountOfEntriesDict), 7)
        self.assertEqual(self.wf.wordCountOfEntriesDict[datetime(2017,1,5)], 14)
        self.assertEqual(len(self.wf.namesDict), 3)

    def test_wordsDict(self):
        self.assertEqual(len(self.wf.wordsDict), 17) #total number of words
        self.assertEqual(self.wf.wordsDict['day']['count'], 9) #word count
        #dates
        self.assertEqual(self.wf.wordsDict['day']['firstDate'], datetime(2017,1,1))
        self.assertEqual(self.wf.wordsDict['day']['lastDate'], datetime(2017,2,5))
        #was upper
        #TODO

    def test_namesDict(self):
        self.assertEqual(len(self.wf.namesDict), 3) #number of names
        self.assertEqual(self.wf.namesDict['cheryl'][0], 4) #count
        self.assertEqual(self.wf.namesDict['cheryl'][1], datetime(2017,1,5))

    def test_wordCountOfEntriesDict(self):
        self.assertEqual(len(self.wf.wordCountOfEntriesDict), 7) #number of entries
        self.assertEqual(self.wf.wordCountOfEntriesDict[datetime(2017,1,5)], 14) #count

    def test_printHighest(self):
        with Capturing() as output:
            self.wf.printHighest(['all'], None)
        expected = str(['Word                  Count   Last Occurence', '----------------------------------', 
            'day                   9       02-05-2017 ', 'sentence              8       02-05-2017 ', 'one                   6       02-05-2017 ', 
            'two                   5       02-05-2017 ', 'cheryl                4       01-05-2017 ', 'dirk                  3       01-05-2017 ', 
            'five                  2       02-05-2017 ', 'skipping              2       02-05-2017 ', 'laura                 2       01-05-2017 ', 
            'four                  2       01-05-2017 ', 'a                     2       02-05-2017 ', 'month                 1       02-05-2017 ', 
            'another               1       12-01-2014 ', 'three                 1       01-03-2017 ', 'testing               1       12-31-2017 ', 
            'date                  1       12-01-2014 ', 'dates                 1       12-31-2017 '])
        self.assertEqual(str(output), expected)

        with Capturing() as output2:
            self.wf.printHighest(['2', '7'], None)
        expected = str(['Word                  Count   Last Occurence', '----------------------------------', 'one                   6       02-05-2017 ', 
            'two                   5       02-05-2017 ', 'cheryl                4       01-05-2017 ', 'dirk                  3       01-05-2017 ', 
            'five                  2       02-05-2017 '])
        self.assertEqual(str(output2), expected)

        with Capturing() as output3:
            self.wf.printHighest(['3'], None)
        expected = str(['Word                  Count   Last Occurence', '----------------------------------', 
            'day                   9       02-05-2017 ', 'sentence              8       02-05-2017 ', 'one                   6       02-05-2017 '])
        self.assertEqual(str(output3), expected)

    def test_relatedNamesDict(self):
        self.assertEqual(len(self.wf.relatedNamesDict), 3) #total number of names
        self.assertEqual(self.wf.relatedNamesDict['cheryl']['laura'], 2)
        self.assertEqual(self.wf.relatedNamesDict['cheryl']['dirk'], 3)
        self.assertEqual(self.wf.relatedNamesDict['laura']['cheryl'], 2)
        self.assertEqual(self.wf.relatedNamesDict['laura']['dirk'], 1)

    def test_printRelatedNames(self):
        with Capturing() as output:
            self.wf.printHighest(['cheryl', 'all'], 'namesRelated')
        expected = str(['Related names for cheryl:', '', 'Name                  Count   ', '----------------------------------', 
            'dirk                  3       ', 'laura                 2       '])
        self.assertEqual(str(output), expected)


    #TODO: re-enable
    # def test_overall(self):
    #     with Capturing() as output:
    #         self.wf.overallAnalytics()
    #     expected = str(['Total number of entries:  7', 'First entry:  12-01-2014', 'Last entry:  12-31-2017', 'Total days from first to last entry:  1126', 
    #         'Percentage of days from first to last with an entry:  0.62%', 'Average length per entry:  7.29', 'Longest entry: 14 words on  01-05-2017', 
    #         'Total number of words written:  51'])
    #     self.assertEqual(str(output), expected)


if __name__ == '__main__':
    unittest.main()


#look into pexpect library for automation
