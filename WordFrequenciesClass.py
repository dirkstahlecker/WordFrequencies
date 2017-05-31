import argparse
import re
import os
import operator
import argparse
import matplotlib.pyplot as plt
import datetime
from Helper import Helper
from Preferences import Preferences
import locale

class WordFrequencies:
    namesSet = set()
    wordsDict = {} #{ word : { 'count': count , 'lastDate': last occurence , 'firstDate': first occurence , 'wasUpper': started with uppercase letter } }
    namesDict = {} #{ name : ( count , last occurence ) }
    wordsPerDayDict = {} #{ word : { 'count': count , 'lastOccurence': last occurence } } only counts one occurence per day
    namesPerDayDict = {} #{ word : ( count , last occurence ) }
    namesToGraphDict = {} #{ word : [ [ date , count ] ] }
    namesToGraphDictUniqueOccurences = {} #{ word : [ date ] }
    wordCountOfEntriesDict = {} #{ date : word count }
    relatedNamesDict = {} #{ name : { name : unique day count } }
    totalNumberOfWords = 0

    guessedNamesSet = set()
    firstDate = datetime.datetime(datetime.MAXYEAR,12,31)
    mostRecentDate = datetime.datetime(datetime.MINYEAR,1,1)

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
        namesFound = set()
        for word in words:

            if self.prefs.COMBINE_PLURALS:
                if word.endswith("'s"):
                    word = word[:len(word)-2]
                #stripping plural s is easy for names, as we assume there isn't another word that is the name plus the trailing s
                #but for arbitrary words its hard (e.g. "was" or "is")

            wasUpper = False;
            if word[:1].isupper():
                wasUpper = True;
            word = Helper.cleanWord(word)

            if not Helper.valid(word):
                continue
            wordsToCount += 1

            #names
            if word in self.namesSet and (Preferences.REQUIRE_CAPS_FOR_NAMES and wasUpper):
                namesFound.add(word)

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

        return (wordsToCount, namesFound)

    #graphs the number of occurences of the name per day
    def graphAnalytics(self, args):
        #{ word : [ [ date , count ] ] }
        name = args[0]
        try:
            self.namesToGraphDict[name]
        except:
            print 'Invalid input - must be a valid name'
            return
        try:
            x = [date[0] for date in self.namesToGraphDict[name]]
            y = [count[1] for count in self.namesToGraphDict[name]]
            
            ax = plt.subplot(111)
            ax.bar(x, y, width=2)
            ax.xaxis_date()

            plt.show()
        except:
            print 'Unknown error occured while graphing'

    #graphs a bar for each day that an entry exists
    def graphEntries(self, args):
        #{ date : word count }
        sortedLengthOfEntriesDict = sorted(self.wordCountOfEntriesDict.items(), key=operator.itemgetter(1))
        x = [i[0] for i in sortedLengthOfEntriesDict]
        y = [1 for j in sortedLengthOfEntriesDict]
        self.graphHelper(x, y)

    def graphHelper(self, x, y):
        ax = plt.subplot(111)
        ax.bar(x, y, width=2)
        ax.xaxis_date()
        plt.show()

    def graphNameValue(self, in_dict):
        x = in_dict.keys()
        y = in_dict.values()
        self.graphHelper(x, y)

    def lookupWord(self, args):
        word = args[0]
        try:
            self.wordsDict[word]
        except:
            print 'Invalid word'
            return
        print word + ': '
        print 'First usage: ' + str(self.wordsDict[word]['firstDate'])
        print 'Last usage: ' + str(self.wordsDict[word]['lastDate'])
        total_uses = self.wordsDict[word]['count']
        total_days_used = self.wordsPerDayDict[word]['count']
        total_number_of_days = len(self.wordCountOfEntriesDict)
        print 'Total usages: ' + str(total_uses)
        length = (self.wordsDict[word]['lastDate'] - self.wordsDict[word]['firstDate']).days
        print 'Length from first use to last: ' + Helper.daysAsPrettyLength(length)
        print 'Average usages per day: ' + str(float(total_uses) / length)
        print 'Percentage of days with a useage: ' + str(round(float(total_days_used) / total_number_of_days * 100, 2)) + '%'

    def overallAnalytics(self):
        print 'Total number of entries: ',
        print len(self.wordCountOfEntriesDict)
        print 'First entry: ',
        print Helper.prettyPrintDate(self.firstDate)
        print 'Last entry: ',
        print Helper.prettyPrintDate(self.mostRecentDate)
        print 'Total days from first to last entry: ',
        totalDays = self.mostRecentDate - self.firstDate #this is correct
        days = totalDays.days
        print days
        print 'Percentage of days from first to last with an entry: ',
        print str(round(float(len(self.wordCountOfEntriesDict)) / days * 100, 2)) + '%'
        print 'Average length per entry: ',
        numberOfEntries = len(self.wordCountOfEntriesDict)
        sumOfLengths = 0
        longestEntryLength = 0
        for date in self.wordCountOfEntriesDict.keys():
            length = self.wordCountOfEntriesDict[date]
            if length > longestEntryLength:
                longestEntryLength = length
                longestEntryDate = date
            sumOfLengths += length 
        print round(float(sumOfLengths) / numberOfEntries, 2)
        print 'Longest entry: ' + str(longestEntryLength) + ' words on ',
        print Helper.prettyPrintDate(longestEntryDate)
        print 'Total number of words written: ',
        print locale.format("%d", self.totalNumberOfWords, grouping=True)


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

        if len(date) <= self.WORD_COL_WIDTH:
            print date,
            chars_left = self.WORD_COL_WIDTH - len(date)
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
        date = inp[1]['lastDate']
        self.makeOutputPrettyHelper(word, count, date)
        
    #print the x most occuring words
    #num: number to print. if 'all', prints all
    def printHighest(self, args, option):
        if self.prefs.VERBOSE:
            print 'args: ',
            print args
            print 'option: ',
            print option

        if option == 'namesRelated':
            nameForRelated = args[0]
            args = args[1:]
            if len(args) < 1:
                print 'Too few arguments.'
                return
            if self.prefs.VERBOSE:
                print 'nameForRelated: ' + nameForRelated

        start_num = 0
        end_num = 0
        index1 = 0
        index2 = 1

        if len(args) == 1: #only an end num
            try:
                if (args[index1] == 'all'):
                    end_num = float('inf')
                else:
                    end_num = int(args[index1])
            except:
                print 'Invalid arguments'
                return
        elif len(args) >= 2: #start and end
            try:
                start_num = int(args[index1])
                if (args[index2] == 'all'):
                    end_num = float('inf')
                else:
                    end_num = int(args[index2])
            except:
                print 'Invalid arguments'
                return

        if self.prefs.VERBOSE:
            print 'start_num: ',
            print start_num,
            print ' end_num ',
            print end_num

        #TODO: add headers to all cases
        if option == 'names':
            sortedNamesDict = sorted(self.namesDict.items(), key=operator.itemgetter(1))
            sortedNamesDict.reverse()
            end_num = min(end_num, len(sortedNamesDict))
            self.makePrettyHeader('Word', 'Count', 'Last Occurence')
            for x in xrange(start_num, end_num):
                self.makeOutputPretty(sortedNamesDict[x])
        elif option == 'namesRelated':
            #TODO: deal with 'all' here, since it won't be caught earlier
            sortedRelatedNamesDict = sorted(self.relatedNamesDict[nameForRelated].items(), key=operator.itemgetter(1))
            sortedRelatedNamesDict.reverse()
            print 'Related names for ' + nameForRelated + ':\n'
            self.makePrettyHeader('Name', 'Count')
            end_num = min(end_num, len(sortedRelatedNamesDict))
            for x in xrange(start_num, end_num):
                self.makeOutputPrettyRelated(sortedRelatedNamesDict[x])
        elif option == 'wordsPerDay':
            sortedWordsPerDayDict = sorted(self.wordsPerDayDict.items(), key=lambda x: x[1]['count'])
            sortedWordsPerDayDict.reverse()
            end_num = min(end_num, len(sortedWordsPerDayDict))
            self.makePrettyHeader('Word', 'Count', 'Last Occurence')
            for x in xrange(start_num, end_num):
                self.makeOutputPrettyWPD(sortedWordsPerDayDict[x])
        elif option == 'namesPerDay':
            sortedNamesPerDayDict = sorted(self.namesPerDayDict.items(), key=operator.itemgetter(1))
            sortedNamesPerDayDict.reverse()
            end_num = min(end_num, len(sortedNamesPerDayDict))
            self.makePrettyHeader('Name', 'Count', 'Last Occurence')
            for x in xrange(start_num, end_num):
                self.makeOutputPretty(sortedNamesPerDayDict[x])
        elif option == 'length':
            sortedLengthOfEntriesDict = sorted(self.wordCountOfEntriesDict.items(), key=operator.itemgetter(1))
            sortedLengthOfEntriesDict.reverse()
            end_num = min(end_num, len(sortedLengthOfEntriesDict))
            self.makePrettyHeader('Date', 'Count')
            for x in xrange(start_num, end_num):
                self.makeOutputPrettyLength(sortedLengthOfEntriesDict[x])
        else: #regular words
            self.makePrettyHeader('Word', 'Count', 'Last Occurence')
            sortedWordsDict = sorted(self.wordsDict.items(), key=lambda x: x[1]['count'])
            sortedWordsDict.reverse()
            end_num = min(end_num, len(sortedWordsDict))
            for x in xrange(start_num, end_num):
                self.makeOutputPrettyWordsDict(sortedWordsDict[x])

    def addRelatedNames(self, namesFound):
        #{ name : { name : unique day count } }
        for keyName in namesFound:
            for otherName in namesFound:
                if keyName == otherName:
                    continue
                try:
                    self.relatedNamesDict[keyName]
                except:
                    self.relatedNamesDict[keyName] = {}
                try: 
                    self.relatedNamesDict[keyName][otherName] += 1
                except:
                    self.relatedNamesDict[keyName][otherName] = 1

    def readFile(self, url):
        try:
            f = open(url, 'r')
        except:
            print('File not found')
            newPath = raw_input('Enter new path > ');
            self.readFile(newPath) #TODO: this doesn't work for entirely unknown reasons
            return

        newdate = re.compile('\s*([0-9]{1,2}-[0-9]{1,2}-[0-9]{2})\s*')
        currentDateStr = None
        currentDateObj = None
        numWords = 0
        namesFound = set()
        totalWordNum = 0
        
        line = f.readline()
        while (line != ''):
            #check a line to see if it's a date, therefore a new day
            res = newdate.match(line)
            if res != None: #date found
                if namesFound != None:
                    self.addRelatedNames(namesFound)
                    namesFound = set()

                if numWords > 0:
                    self.wordCountOfEntriesDict[currentDateObj] = numWords #should be here, since we want it triggered at the end
                totalWordNum += numWords
                numWords = 0
                currentDateStr = res.group(0)
                currentDateStr = Helper.formatDateStringIntoCleanedString(currentDateStr)
                currentDateObj = Helper.makeDateObject(currentDateStr)

                if currentDateObj > self.mostRecentDate: #found a higher date than what we've seen so far
                    self.mostRecentDate = currentDateObj
                if currentDateObj < self.firstDate: #found a lower date than what we have now
                    self.firstDate = currentDateObj
                line = line[len(currentDateStr):] #remove date from line, so it's not a word

            if currentDateStr != None:
                (wordsFound, namesFoundThisLine) = self.addLine(line, currentDateObj)
                for name in namesFoundThisLine:
                    namesFound.add(name)
                numWords += wordsFound
                # self.guessNames(line)
            line = f.readline()

        #need to capture the last date for the entry length
        self.wordCountOfEntriesDict[currentDateObj] = numWords 
        self.totalNumberOfWords = totalWordNum + numWords #need to get words from last line
        f.close()

    #args is a list of arguments in order
    def callInputFunction(self, inp, args):
        if inp == 'highest':
            self.printHighest(args, None)
        elif inp == 'lookup':
            self.lookupWord(args)
        elif inp == 'names':
            self.printHighest(args, 'names')
        elif inp == 'related':
            self.printHighest(args, 'namesRelated')
        elif inp == 'graph':
            self.graphAnalytics(args)
        elif inp == 'graphentries':
            self.graphEntries(args)
        # elif inp == 'gpd':
        #     self.graphAnalyticsPerDay(args)
        elif inp == 'wpd':
            self.printHighest(args, 'wordsPerDay')
        elif inp == 'npd':
            self.printHighest(args, 'namesPerDay')
        elif inp == 'addname':
            self.addName(args)
        elif inp == 'option':
            pass
        elif inp == 'length':
            self.printHighest(args, 'length')
        elif inp == 'graphlength':
            self.graphNameValue(self.wordCountOfEntriesDict)
        elif inp == 'overall':
            self.overallAnalytics()
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
            self.namesSet.add(line.strip().lower()) #TODO: does this do anything? What?
            line = f.readline()

    def parseInput(self, inpStr):
        parts = inpStr.split()
        command = parts[0].lower().strip().lstrip()
        args = parts[1:]
        if (self.prefs.VERBOSE):
            print 'Parsed arguments: command: ' + str(command) + ' args: ' + str(args)
        return self.callInputFunction(command, args)

    #break apart the main function for testing
    def runMainLoop(self):
        while True:
            print '''
    Options:
    Highest x words             highest [num | all] (num | all)
    Highest x words per day     wpd [num | all]
    Lookup                      lookup [word]
    Highest x names             names [num | all]
    Related Names               related [name] [num | all]
    Highest x names per day     npd [num | all]
    Graph names                 graph [name]
    Graph entries               graphentries
    Graph length                graphlength
    Add name                    add name [name]
    Set Options                 option [option_name] [value]
    Length                      length [num | all]
    Overall analytics           overall
    Exit                        exit
    '''
            if not self.parseInput(raw_input('>')):
                return

    #break apart the main function for testing
    def mainSetup(self, args):
        locale.setlocale(locale.LC_ALL, 'en_US')
        fileurl = args.file

        if args.verbosity:
            self.prefs.VERBOSE = True
        if args.combineplurals:
            self.prefs.COMBINE_PLURALS = True

        self.makeNamesSet()
        self.readFile(fileurl)


    def main(self, args):
        self.mainSetup(args)
        self.runMainLoop()



#Options need to be set on startup
if __name__ == '__main__':
    wf = WordFrequencies()

    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Path to file to examine')
    parser.add_argument('-v', '--verbosity', action='store_true', help='Enable verbose output')
    parser.add_argument('-p', '--combineplurals', action='store_true', help='Combine plurals')
    args = parser.parse_args()

    wf.main(args)



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

what names each name is frequently found with 
    refine to only look at names in the same paragraph maybe?

figure out how to deal with "[date] through [date]:"

use constants for strings

figure out what to do with multiple people of the same name

have a reverse order flag of some sort (allow to view in ascending order rather than descending)


Bugs:
fix axes on graphing
firstDate isn't accurate - isn't picking up 8-08-10, possible bug because it's the first date in there

'''
