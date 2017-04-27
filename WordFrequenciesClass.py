import argparse
import re
import os
import operator
import argparse
import matplotlib.pyplot as plt
from datetime import datetime
from Helper import Helper
from Preferences import Preferences

class WordFrequencies:
    namesSet = set()
    wordsDict = {} #{ word : { 'count': count , 'lastDate': last occurence , 'firstDate': first occurence , 'wasUpper': started with uppercase letter } }
    namesDict = {} #{ name : ( count , last occurence ) }
    wordsPerDayDict = {} #{ word : { 'count': count , 'lastOccurence': last occurence } } only counts one occurence per day
    namesPerDayDict = {} #{ word : ( count , last occurence ) }
    namesToGraphDict = {} #{ word : [ [ date , count ] ] }
    namesToGraphDictUniqueOccurences = {} #{ word : [ date ] }
    wordCountOfEntriesDict = {} #{ date : word count }
    guessedNamesSet = set()
    namesURL = os.path.dirname(os.path.realpath(__file__)) + '/names.txt'
    prefs = Preferences() #stored the user's preferences for various things

    WORD_COL_WIDTH = 20
    NUM_COL_WIDTH = 6
    DATE_COL_WIDTH = 8

    #try to guess what is a name by looking for capitalized letters in the middle of sentences
    def getGuessedNames(self):
        f = open(namesURL, 'r+')
        print 'Are these names? (y/n)'
        for name in guessedNamesSet:
            if name in namesSet:
                break
            inp = raw_input(name + ': ')
            if inp == 'y':
                namesSet.add(name)

        for name in namesSet:
            f.write(name) + '\n'

    def guessNames(self, line):
        nameRegex = re.compile('[^\.] ([ABCDEFGHIJKLMNOPQRSTUVWXYZ][\w+|\.])')
        names = nameRegex.search(line)

        try: 
            for name in names.groups():
                self.guessedNamesSet.add(name)
            #print names.groups() #TODO: regex is broken (doesn't capture all matches)
        except:
            return

    #Add a name manually to the names set
    def addName(self, args):
        name = args[0]
        if name in self.namesDict:
            print "Name already added"
            return
        self.namesSet.add(name);
        f = open(self.namesURL, 'a')
        f.write(name + '\n')
        f.close()

    def removeName(self, name):
        self.namesSet.remove(name);
        f = open(self.namesURL, 'r+')
        f.clear()
        for name in self.namesSet:
            f.write(name) + '\n'
        f.close()

    #parse a line and add the words to the dictionaries
    def addLine(self, line, currentDate):
        words = line.split(' ')
        wordsToCount = 0 #used to calculate the length of entries - don't want to include invalid words in the word count TODO: rethink this?
        for word in words:
            wasUpper = False;
            if word[:1].isupper():
                wasUpper = True;
            word = Helper.cleanWord(word)

            if not Helper.valid(word):
                continue
            wordsToCount += 1

            #names
            if word in self.namesSet and (Preferences.REQUIRE_CAPS_FOR_NAMES and wasUpper):
                try:
                    self.namesDict[word] = (self.namesDict[word][0] + 1, currentDate)
                except:
                    self.namesDict[word] = (1, currentDate)

                #names per day
                try:
                    if self.namesPerDayDict[word][1] != currentDate:
                        self.namesPerDayDict[word] = (self.namesPerDayDict[word][0] + 1, currentDate)
                except:
                    self.namesPerDayDict[word] = (1, currentDate)

                #names for graphing purposes
                try: #{ word : [ [ date , count ] ] }
                    self.namesToGraphDict[word] #trigger exception
                    if self.namesToGraphDict[word][-1][0] == currentDate: #increment count
                        self.namesToGraphDict[word][-1][1] += 1
                    else: #start a new tuple with a new date
                        self.namesToGraphDict[word].append([currentDate, 1])
                except: #this name hasn't been encountered yet
                    self.namesToGraphDict[word] = [[currentDate, 1]]

                #names for graph, counting on unique occurences
                try: #{ word : [ date ] }
                    self.namesToGraphDictUniqueOccurences[word].append(currentDate)
                except:
                    self.namesToGraphDictUniqueOccurences[word] = [currentDate]

            #words
            try:
                self.wordsDict[word] = {'count': self.wordsDict[word]['count'] + 1, 
                'lastDate': currentDate, 'firstDate': self.wordsDict[word]['firstDate'], 'wasUpper': wasUpper}
            except:
                self.wordsDict[word] = {'count': 1, 'lastDate': currentDate, 'firstDate': currentDate}
            
            #words per day
            try:
                if self.wordsPerDayDict[word]['lastOccurence'] != currentDate:
                    self.wordsPerDayDict[word] = {'count': self.wordsPerDayDict[word]['count'] + 1, 'lastOccurence': currentDate}
            except:
                    self.wordsPerDayDict[word] = {'count': 1, 'lastOccurence': currentDate}

        return wordsToCount

    #graphs the number of occurences of the name per day
    def graphAnalytics(self, args):
        #{ word : [ [ date , count ] ] }
        name = args[0]
        try:
            x = [datetime.strptime(date[0] ,'%m-%d-%y') for date in self.namesToGraphDict[name]]
            y = [count[1] for count in self.namesToGraphDict[name]]
            
            ax = plt.subplot(111)
            ax.bar(x, y, width=2)
            ax.xaxis_date()

            plt.show()
        except:
            print 'Invalid input - must be a valid name'

    def lookupWord(self, args):
        word = args[0]
        print word + ': '
        print 'First usage: ' + str(self.wordsDict[word]['firstDate'])
        print 'Last usage: ' + str(self.wordsDict[word]['lastDate'])
        total_uses = self.wordsDict[word]['count']
        total_days_used = self.wordsPerDayDict[word]['count']
        total_number_of_days = len(self.wordCountOfEntriesDict)
        print 'Total usages: ' + str(total_uses)
        length = Helper.subtractDates(self.wordsDict[word]['lastDate'], self.wordsDict[word]['firstDate']).days
        print 'Length from first use to last: ' + Helper.daysAsPrettyLength(length)
        print 'Average usages per day: ' + str(float(total_uses) / length)
        print 'Percentage of days with a useage: ' + str(float(total_days_used) / total_number_of_days)

    def printAll(self, names):
        self.printHighest(float('inf'), names)

    def makeOutputPrettyHelper(self, header, word, count, date):
        if header:
            print 'Word',
            print ' ' * (self.WORD_COL_WIDTH - 4),
        else:
            if len(word) <= self.WORD_COL_WIDTH:
                print word,
                chars_left = self.WORD_COL_WIDTH - len(word)
                print ' ' * chars_left,
            else:
                print word[:self.WORD_COL_WIDTH],

        if header:
            print 'Count',
            print ' ' * (self.NUM_COL_WIDTH - 5),
        else:
            #TODO: deal with overshoot on numbers and date
            print count,
            print ' ' * (self.NUM_COL_WIDTH - len(str(count))),

        if header:
            print 'Last Occurence',
        else:
            print date,
        print ' ' * (self.DATE_COL_WIDTH - len(date))

        if header:
            print '-'*(38) #WORD_COL_WIDTH + NUM_COL_WIDTH + DATE_COL_WIDTH
            #TODO: make this a variable rather than a hardcoded number (and figure out why the variable width is off by 4)

    def makeOutputPretty(self, inp): #( word : ( count , last occurence ) )
        word = inp[0]
        count = inp[1][0]
        date = inp[1][1]
        self.makeOutputPrettyHelper(False, word, count, date)

    #inp comes in as a tuple due to the sorting and the fact that dicts can't be sorted
    def makeOutputPrettyWPD(self, inp): #( word : { 'count': count, 'lastOccurence': last occurence } )
        word = inp[0]
        count = inp[1]['count']
        date = inp[1]['lastOccurence']
        self.makeOutputPrettyHelper(False, word, count, date)

    def makeOutputPrettyWordsDict(self, inp): #( word : { 'count': count, 'lastDate': last occurence, 'firstDate': first occurence } )
        word = inp[0]
        count = inp[1]['count']
        date = inp[1]['lastDate']
        self.makeOutputPrettyHelper(False, word, count, date)

    def makePrettyHeader(self):
        self.makeOutputPrettyHelper(True, '', '', '')
        
    #print the x most occuring words
    #num: number to print. if 'all', prints all
    def printHighest(self, args, option):
        start_num = 0
        end_num = 0
        if len(args) == 1: #only an end num
            try:
                if (args[0] == 'all'):
                    end_num = float('inf')
                else:
                    end_num = int(args[0])
            except:
                print 'Invalid arguments'
        elif len(args) >= 2: #start and end
            try:
                start_num = int(args[0])
                if (args[1] == 'all'):
                    end_num = float('inf')
                else:
                    end_num = int(args[1])
            except:
                print 'Invalid arguments'

        if self.prefs.VERBOSE:
            print 'start_num: ',
            print start_num,
            print ' end_num ',
            print end_num

        if option == 'names':
            self.sortedNamesDict = sorted(self.namesDict.items(), key=operator.itemgetter(1))
            self.sortedNamesDict.reverse()
            if end_num > len(self.sortedNamesDict):
                end_num = len(self.sortedNamesDict)
            self.makePrettyHeader()
            for x in xrange(start_num, min(end_num, len(self.sortedNamesDict))):
                self.makeOutputPretty(self.sortedNamesDict[x])
        elif option == 'wordsPerDay':
            self.sortedWordsPerDayDict = sorted(self.wordsPerDayDict.items(), key=lambda x: x[1]['count'])
            self.sortedWordsPerDayDict.reverse()
            if end_num > len(self.sortedWordsPerDayDict):
                end_num = len(self.sortedWordsPerDayDict)
            for x in xrange(start_num, min(end_num, len(self.sortedWordsPerDayDict))):
                self.makeOutputPrettyWPD(self.sortedWordsPerDayDict[x])
        elif option == 'namesPerDay':
            self.sortedNamesPerDayDict = sorted(self.namesPerDayDict.items(), key=operator.itemgetter(1))
            self.sortedNamesPerDayDict.reverse()
            if end_num > len(self.sortedNamesPerDayDict):
                end_num = len(self.sortedNamesPerDayDict)
            for x in xrange(start_num, min(end_num, self.sortedNamesPerDayDict)):
                self.makeOutputPretty(self.sortedNamesPerDayDict[x])
        else: #regular words
            self.sortedWordsDict = sorted(self.wordsDict.items(), key=lambda x: x[1]['count'])
            self.sortedWordsDict.reverse()
            if end_num > len(self.sortedWordsDict):
                end_num = len(self.sortedWordsDict)
            for x in xrange(start_num, min(end_num, len(self.sortedWordsDict))):
                self.makeOutputPrettyWordsDict(self.sortedWordsDict[x])

    def readFile(self, url):
        try:
            f = open(url, 'r')
        except:
            print('File not found')
            newPath = raw_input('Enter new path > ');
            self.readFile(newPath) #TODO: this doesn't work for entirely unknown reasons
            return

        newdate = re.compile('\s*([0-9]{1,2}-[0-9]{1,2}-[0-9]{2})\s*')
        currentDate = None;
        numWords = 0
        
        line = f.readline()
        while (line != ''):
            #check a line to see if it's a date, therefore a new day
            res = newdate.match(line)
            if res != None: #date found
                if numWords > 0:
                    self.wordCountOfEntriesDict[currentDate] = numWords #should be here, since we want it triggered at the end
                numWords = 0
                currentDate = res.group(0);
                currentDate = Helper.formatDate(currentDate)
                line = line[len(currentDate):] #remove date from line, so it's not a word

            if currentDate != None:
                numWords += self.addLine(line, currentDate)
                self.guessNames(line)
            line = f.readline()

        #need to capture the last date for the entry length
        self.wordCountOfEntriesDict[currentDate] = numWords 
        f.close()

    #args is a list of arguments in order
    def callInputFunction(self, inp, args):
        if inp == 'highest':
            print self.wordCountOfEntriesDict
            self.printHighest(args, None)
        elif inp == 'lookup':
            self.lookupWord(args)
        elif inp == 'names':
            self.printHighest(args, 'names')
        elif inp == 'graph':
            self.graphAnalytics(args)
        elif inp == 'gpd':
            self.graphAnalyticsPerDay(args)
        elif inp == 'wpd':
            self.printHighest(args, 'wordsPerDay')
        elif inp == 'npd':
            self.printHighest(args, 'namesPerDay')
        elif inp == 'addname':
            self.addName(args)
        elif inp == 'option':
            pass
        elif inp == 'exit':
            return False
        else:
            print 'Unknown command.'
        return True

    #populate namesList from file
    def makeNamesSet(self):
        try:
            f = open(self.namesURL, 'r') #TODO: error handling
        except:
            raise Exception("Names file not found")
        self.namesSet.clear()
        line = f.readline()
        while line != '':
            self.namesSet.add(line.strip().lower())
            line = f.readline()

    def parseInput(self, inpStr):
        parts = inpStr.split()
        command = parts[0]
        args = parts[1:]
        if (self.prefs.VERBOSE):
            print 'Parsed arguments: command: ' + str(command) + ' args: ' + str(args)
        return self.callInputFunction(command, args)

    def main(self, fileurl):
        self.makeNamesSet()
        self.readFile(fileurl)
        
        while True:
            print '''
    Options:
    Highest x words             highest [num | all] (num | all)
    Highest x words per day     wpd [num | all]
    Lookup                      lookup [word]
    Highest x names             names [num | all]
    Highest x names per day     npd [num | all]
    Graph names                 graph [name]
    Graph names per day         gpd [name]
    Add name                    add name [name]
    Set Options                 option [option_name] [value]
    Exit                        exit
    '''
            if not self.parseInput(raw_input('>')):
                return

if __name__ == '__main__':
    wf = WordFrequencies()

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to file to examine")
    #parser.add_argument('-v', '--verbose', help="Enable verbose output", action="enableVerbosity()")
    args = parser.parse_args()

    wf.main(args.file)



'''
TODO: 
something weird going on with apostrophes (specifically "didn't")
make names sensitive to capitals (ex. "will" is very high, because of the everyday word)
distinguish between different people with the same spelling of names
    possibly by looking at other people that are frequently mentioned with them in the same day to determine
length of entries / average length of entries per day / look up or graph trends

replace data structures with something more readable and maintainable (some sort of named nested tree maybe)

flag to ignore trailing s and then combine both "word" and "words" into same 

enter new path doesn't work if initial one isn't valid

allow graphing for words and not just names

'''