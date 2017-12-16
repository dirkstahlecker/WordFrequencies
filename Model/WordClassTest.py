from WordDict import WordDict
from Helper import Helper
import unittest
from WordFrequenciesClass import WordFrequencies
from datetime import datetime
import argparse
from io import StringIO
from WordClass import WordClass
import re

class TestUM(unittest.TestCase):
    basicWord = "test"
    markupName = "[!!Dirk|Dirk Stahlecker!!]"
    wcBasic = WordClass(basicWord)
    wcMarkup = WordClass(markupName)

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def test_basicWord(self):
        self.assertEqual(self.basicWord, self.wcBasic.rawWord)
        self.assertTrue(self.wcBasic == self.basicWord)
        self.assertFalse(self.wcBasic == self.wcMarkup)

    def test_markupWord(self):
        self.assertEqual(self.markupName, self.wcMarkup.rawWord)
        self.assertTrue("Dirk" == self.wcMarkup)
        self.assertFalse(self.wcMarkup == self.basicWord)


if __name__ == '__main__':
    unittest.main()