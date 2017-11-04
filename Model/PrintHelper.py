from Preferences import Preferences
from Helper import Helper

class PrintHelper:
    prefs = None

    WORD_COL_WIDTH = 20
    NUM_COL_WIDTH = 6
    DATE_COL_WIDTH = 8

    def __init__(self, prefs):
        self.prefs = prefs
        assert isinstance(prefs, Preferences)

###############################################################################################
# Printing and Output
###############################################################################################
    #date is a datetime object
    def makeOutputPrettyHelper(self, word, count, date):
        if len(word) <= self.WORD_COL_WIDTH:
            print word,
            chars_left = self.WORD_COL_WIDTH - len(word)
            print ' ' * chars_left,
        else:
            print word[:self.WORD_COL_WIDTH],

        #TODO: deal with overshoot on numbers and date
        print count,
        print ' ' * (self.NUM_COL_WIDTH - len(str(count))),

        if date != None:
            date = Helper.prettyPrintDate(date)
            print date,
            print ' ' * (self.DATE_COL_WIDTH - len(str(date)))
        else:
            print ''

    def makePrettyHeader(self, col1name, col2name = '', col3name = ''):
        print col1name,
        print ' ' * (self.WORD_COL_WIDTH - 4),
        print col2name,
        print ' ' * (self.NUM_COL_WIDTH - 5),
        print col3name
        print '-'*(self.WORD_COL_WIDTH + self.NUM_COL_WIDTH + self.DATE_COL_WIDTH) #38

    def makeOutputPretty(self, inp): #( word : ( count , last occurence ) )
        word = inp[0]
        count = inp[1][0]
        date = inp[1][1]
        self.makeOutputPrettyHelper(word, count, date)

    def makeOutputPrettyRelated(self, inp): #( name , count )
        name = inp[0]
        count = inp[1]
        self.makeOutputPrettyHelper(name, count, None)

    def makeOutputPrettyLength(self, inp): #{ date : word count }
        # self.makeOutputPrettyHelper(None, inp[1], inp[0])
        date = inp[0]
        count = inp[1]

        if len(str(date)) <= self.WORD_COL_WIDTH:
            print date,
            chars_left = self.WORD_COL_WIDTH - len(str(date))
            print ' ' * chars_left,
        else:
            print date[:self.WORD_COL_WIDTH],

        #TODO: deal with overshoot on numbers and date
        print count,
        print ' ' * (self.NUM_COL_WIDTH - len(str(count)))

    #inp comes in as a tuple due to the sorting and the fact that dicts can't be sorted
    def makeOutputPrettyWPD(self, inp): #( word : { 'count': count, 'lastOccurence': last occurence } )
        word = inp[0]
        count = inp[1]['count']
        date = inp[1]['lastOccurence']
        self.makeOutputPrettyHelper(word, count, date)

    def makeOutputPrettyWordsDict(self, inp): #( word : { 'count': count, 'lastDate': last occurence, 'firstDate': first occurence } )
        word = inp[0]
        count = inp[1]['count']
        date = inp[1]['lastOccurrence']
        self.makeOutputPrettyHelper(word, count, date)

    
