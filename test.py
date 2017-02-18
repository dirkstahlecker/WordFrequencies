import unittest
from WordFrequenciesClass import WordFrequencies
 
class TestUM(unittest.TestCase):

    wf = None
 
    def setUp(self):
        self.wf = WordFrequencies()
        self.wf.main("")

 
    def test_namesURL(self):
        self.assertEqual(self.wf.namesURL, "/Users/Dirk/Programming/Python/WordFrequencies/WordFrequencies/names.txt")
 
 
if __name__ == '__main__':
    unittest.main()