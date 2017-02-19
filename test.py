import unittest
from WordFrequenciesClass import WordFrequencies
from datetime import datetime
 
class TestUM(unittest.TestCase):

    wf = None
 
    def setUp(self):
        self.wf = WordFrequencies()
        self.wf.main("/users/dirk/Programming/Python/WordFrequencies/WordFrequencies/testjournal1.txt")

 
    def test_namesURL(self):
        #self.assertEqual(self.wf.namesURL, "/Users/Dirk/Programming/Python/WordFrequencies/WordFrequencies/names.txt")
        pass

    def test_journalParsing(self):
        self.assertEqual(len(self.wf.wordCountOfEntriesDict), 5)
        self.assertEqual(self.wf.wordCountOfEntriesDict['01-05-17'], 11)
        #self.assertEqual(len(self.wf.wordsDict), 10)
        #self.assertEqual(len(self.wf.namesDict), 0)
        #self.assertEqual(self.wf.wordsDict[1], "one")
 
 
if __name__ == '__main__':
    unittest.main()