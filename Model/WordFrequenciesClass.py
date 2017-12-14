import argparse
import re
import os
import operator
import argparse
import matplotlib.pyplot as plt
import datetime
from Helper import Helper
from Preferences import Preferences
from PrintHelper import PrintHelper
import locale
import hashlib
from WordDict import WordDict
from WordsPerDayDict import WordsPerDayDict
from enum import Enum

class PrintOption(Enum):
    HIGHEST = 1
    LOOKUP = 2
    NAMES = 'names'
    RELATED = 4
    GRAPH = 5
    GRAPHENTRIES = 6
    WORDSPERDAY = 7
    NAMESPERDAY = 8
    ADDNAME = 9
    OPTION = 10
    LENGTH = 11
    GRAPHLENGTH = 12
    OVERALL = 13
    EXIT = 14

class InputOption(Enum):
    HIGHEST = 'highest'
    WPD = 'wpd'
    LOOKUP = 'lookup'
    NAMES = 'names'
    RELATED = 'related'
    NPD = 'npd'
    GRAPH = 'graph'
    GRAPH_ENTRIES = 'graphentries'
    GRAPH_LENGTH = 'graphlength'
    ADDNAME = 'addname'
    OPTION = 'option'
    LENGTH = 'length'
    OVERALL = 'overall'
    EXIT = 'exit'

class WordFrequencies:
###############################################################################################
# Members
###############################################################################################
    namesSet = set()
    wordDict = WordDict()
    namesDict = {} #{ name : ( count , last occurence ) }
    # wordsPerDayDict = {} #{ word : { 'count': count , 'lastOccurence': last occurence } } only counts one occurence per day
    wordsPerDayDict = WordsPerDayDict()
    namesPerDayDict = {} #{ word : ( count , last occurence ) }
    namesToGraphDict = {} #{ word : [ [ date , count ] ] }
    namesToGraphDictUniqueOccurences = {} #{ word : [ date ] }
    wordCountOfEntriesDict = {} #{ date : word count }
    relatedNamesDict = {} #{ name : { name : unique day count } }
    lastNamesForFirstNameDict = {} #{ first name : [ last names ] }
    totalNumberOfWords = 0
    dayEntryHashTable = {} #{ date : hash }

    guessedNamesSet = set()
    firstDate = datetime.datetime(datetime.MAXYEAR,12,31)
    mostRecentDate = datetime.datetime(datetime.MINYEAR,1,1)

    namesURL = os.path.dirname(os.path.realpath(__file__)) + '/names.txt'
    markUnderFilePath = os.path.dirname(os.path.realpath(__file__)) + '/markunder.txt'
    prefs = Preferences() #stored the user's preferences for various things
    printer = PrintHelper(prefs)

    MARK_UNDER_START = '[!!'
    MARK_UNDER_END = '!!]'
    MARK_UNDER_DELIMITER = '|'


###############################################################################################
# Loading and Setup
###############################################################################################    

    #only called for names
    #ask which name it is, store it in a markup format, and compute a hash of the day

    #return either the word unchanged, or the qualified name if it's a name
    def getMarkUnderWord(self, word, originalWord, line, date):
        print('\n\n\n')
        print((Helper.prettyPrintDate(date)))
        print(line) #gives context so you can figure out what's going on
        print('Which ' + word + ' is this?') #TODO: want this name to be capitalized
        numPossibleLastNames = 0

        try:
            self.lastNamesForFirstNameDict[word] #trigger exception if there's one to be thrown
            for nameFromDict in self.lastNamesForFirstNameDict[word]:
                print(str(numPossibleLastNames) + ': ' + nameFromDict)
                numPossibleLastNames = numPossibleLastNames + 1
            print('Or type new last name')
        except:
            print('Type last name:')

        #get the last name either from the number of the choice (if it's a number) or the last name that was directly entered
        lastName = ''
        choice = input('>')
        lastName = choice
        for x in range(0, numPossibleLastNames):
            if choice == str(x):
                lastName = self.lastNamesForFirstNameDict[word][x]
                break

        try:
            if lastName not in self.lastNamesForFirstNameDict[word]:
                self.lastNamesForFirstNameDict[word].append(lastName)
        except:
            self.lastNamesForFirstNameDict[word] = [lastName]

        #create the qualified name to insert into the markunder
        qualifiedLastName = self.MARK_UNDER_START + word + self.MARK_UNDER_DELIMITER + Helper.cleanWord(originalWord, True) + ' ' + lastName + self.MARK_UNDER_END

        return qualifiedLastName

        #need to actually do something to associate the info the user entered with the specific instance of the name




###############################################################################################
# Data Processing
###############################################################################################
    #parse a line and add the words to the dictionaries
    #print the line to markunder file, with the proper qualification on names
    #all markunder printing should happen here
    def addLine(self, line, currentDate):
        markunderFile = open(self.markUnderFilePath, 'a')

        # words = line.split('\[!!([^!]+)!!\]| ')
        words = line.split(' ')
        wordsToCount = 0 #used to calculate the length of entries - don't want to include invalid words in the word count TODO: rethink this?
        namesFound = set()
        for word in words:
            if word == '':
                continue

            if self.prefs.COMBINE_PLURALS:
                if word.endswith("'s"):
                    word = word[:len(word)-2]
                #stripping plural s is easy for names, as we assume there isn't another word that is the name plus the trailing s
                #but for arbitrary words its hard (e.g. "was" or "is")

            wasUpper = False;
            if word[:1].isupper():
                wasUpper = True;
            originalWord = word
            word = Helper.cleanWord(word) #this strips off all punctuation and other information that we want to pass into markup.

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
            if self.wordDict.exists(word):
                # self.wordsDict[word] = {'count': self.wordsDict[word]['count'] + 1, 
                # 'lastDate': currentDate, 'firstDate': self.wordsDict[word]['firstDate'], 'wasUpper': wasUpper}
                self.wordDict.addOrReplaceWord(word, self.wordDict.getCount(word) + 1, currentDate, self.wordDict.getFirstOccurrence(word), wasUpper)
            else:
                self.wordDict.addWord(word, 1, currentDate, currentDate, wasUpper) #TODO: wasUpper wasn't there originally
            
            #words per day
            # try:
            #     if self.wordsPerDayDict.getLastOccurrence(word) != currentDate:
            #         self.wordsPerDayDict[word] = {'count': self.wordsPerDayDict[word]['count'] + 1, 'lastOccurence': currentDate}
            # except:
            #         self.wordsPerDayDict[word] = {'count': 1, 'lastOccurence': currentDate}

            if self.wordsPerDayDict.exists(word):
                self.wordsPerDayDict.addWord(word, self.wordsPerDayDict.getCount(word), currentDate) #TODO: was addOrReplaceWord, need to think what it should be
            else:
                self.wordsPerDayDict(word, 1, currentDate)

            if self.prefs.DO_MARK_UNDER:
                #if it's a name, qualify it for the markunder
                if word in self.namesSet:# or not (Preferences.REQUIRE_CAPS_FOR_NAMES and wasUpper):
                    markUnderWord = self.getMarkUnderWord(word, originalWord, line, currentDate)
                else:
                    markUnderWord = word

                markunderFile.write(markUnderWord + ' ')

        markunderFile.close()
        return (wordsToCount, namesFound)


###############################################################################################
# Graphing and Printing
###############################################################################################
    #print the x most occuring words
    #num: number to print. if 'all', prints all
    #TODO: it would be nice to move at least part of this function to the printer class
    def printHighest(self, args, option):
        if self.prefs.VERBOSE:
            print('args: ', end=' ')
            print(args)
            print('option: ', end=' ')
            print(option)

        if option == 'namesRelated':
            nameForRelated = args[0]
            args = args[1:]
            if len(args) < 1:
                print('Too few arguments.')
                return
            if self.prefs.VERBOSE:
                print('nameForRelated: ' + nameForRelated)

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
                print('Invalid arguments')
                return
        elif len(args) >= 2: #start and end
            try:
                start_num = int(args[index1])
                if (args[index2] == 'all'):
                    end_num = float('inf')
                else:
                    end_num = int(args[index2])
            except:
                print('Invalid arguments')
                return

        if self.prefs.VERBOSE:
            print('start_num: ', end=' ')
            print(start_num, end=' ')
            print(' end_num ', end=' ')
            print(end_num)

        #TODO: add headers to all cases
        if option == PrintOption.NAMES:
            sortedNamesDict = sorted(list(self.namesDict.items()), key=operator.itemgetter(1))
            sortedNamesDict.reverse()
            end_num = min(end_num, len(sortedNamesDict))
            self.printer.makePrettyHeader('Word', 'Count', 'Last Occurence')
            for x in range(start_num, end_num):
                self.printer.makeOutputPretty(sortedNamesDict[x])
        elif option == PrintOption.RELATED:
            #TODO: deal with 'all' here, since it won't be caught earlier
            sortedRelatedNamesDict = sorted(list(self.relatedNamesDict[nameForRelated].items()), key=operator.itemgetter(1))
            sortedRelatedNamesDict.reverse()
            print('Related names for ' + nameForRelated + ':\n')
            self.printer.makePrettyHeader('Name', 'Count')
            end_num = min(end_num, len(sortedRelatedNamesDict))
            for x in range(start_num, end_num):
                self.printer.makeOutputPrettyRelated(sortedRelatedNamesDict[x])
        elif option == PrintOption.WORDSPERDAY:
            sortedWordsPerDayDict = self.wordsPerDayDict.getSortedDictByCount()
            sortedWordsPerDayDict.reverse()
            end_num = min(end_num, len(sortedWordsPerDayDict))
            self.printer.makePrettyHeader('Word', 'Count', 'Last Occurence')
            for x in range(start_num, end_num):
                self.printer.makeOutputPrettyWPD(sortedWordsPerDayDict[x])
        elif option == PrintOption.NAMESPERDAY:
            sortedNamesPerDayDict = sorted(list(self.namesPerDayDict.items()), key=operator.itemgetter(1))
            sortedNamesPerDayDict.reverse()
            end_num = min(end_num, len(sortedNamesPerDayDict))
            self.printer.makePrettyHeader('Name', 'Count', 'Last Occurence')
            for x in range(start_num, end_num):
                self.printer.makeOutputPretty(sortedNamesPerDayDict[x])
        elif option == PrintOption.LENGTH:
            sortedLengthOfEntriesDict = sorted(list(self.wordCountOfEntriesDict.items()), key=operator.itemgetter(1))
            sortedLengthOfEntriesDict.reverse()
            end_num = min(end_num, len(sortedLengthOfEntriesDict))
            self.printer.makePrettyHeader('Date', 'Count')
            for x in range(start_num, end_num):
                self.printer.makeOutputPrettyLength(sortedLengthOfEntriesDict[x])
        else: #regular words
            self.printer.makePrettyHeader('Word', 'Count', 'Last Occurence')
            sortedWordsDict = self.wordDict.getSortedDictByCount()
            sortedWordsDict.reverse()
            end_num = min(end_num, len(sortedWordsDict))
            for x in range(start_num, end_num):
                self.printer.makeOutputPrettyWordsDict(sortedWordsDict[x])


    #graphs the number of occurences of the name per day
    def graphAnalytics(self, args):
        #{ word : [ [ date , count ] ] }
        name = args[0]
        try:
            self.namesToGraphDict[name]
        except:
            print('Invalid input - must be a valid name')
            return
        try:
            x = [date[0] for date in self.namesToGraphDict[name]]
            y = [count[1] for count in self.namesToGraphDict[name]]
            
            ax = plt.subplot(111)
            ax.bar(x, y, width=2)
            ax.xaxis_date()

            plt.show()
        except:
            print('Unknown error occured while graphing')

    #graphs a bar for each day that an entry exists
    def graphEntries(self, args):
        #{ date : word count }
        sortedLengthOfEntriesDict = sorted(list(self.wordCountOfEntriesDict.items()), key=operator.itemgetter(1))
        x = [i[0] for i in sortedLengthOfEntriesDict]
        y = [1 for j in sortedLengthOfEntriesDict]
        self.graphHelper(x, y)

    def graphHelper(self, x, y):
        ax = plt.subplot(111)
        ax.bar(x, y, width=2)
        ax.xaxis_date()
        plt.show()

    def graphNameValue(self, in_dict):
        x = list(in_dict.keys())
        y = list(in_dict.values())
        self.graphHelper(x, y)

    def lookupWord(self, args):
        word = args[0]
        if not self.wordDict.exists(word):
            print('Invalid word')
            return
        print(word + ': ')
        print('First usage: ' + str(self.wordDict.getFirstOccurrence(word)))
        print('Last usage: ' + str(self.wordDict.getLastOccurrence(word)))
        total_uses = self.wordDict.getCount(word)
        total_days_used = self.wordsPerDayDict.getCount(word)
        total_number_of_days = len(self.wordCountOfEntriesDict)
        print('Total usages: ' + str(total_uses))
        length = (self.wordDict.getLastOccurrence(word) - self.wordDict.getFirstOccurrence(word)).days
        print('Length from first use to last: ' + Helper.daysAsPrettyLength(length))
        print('Average usages per day: ' + str(float(total_uses) / length))
        print('Percentage of days with a useage: ' + str(round(float(total_days_used) / total_number_of_days * 100, 2)) + '%')

    def overallAnalytics(self):
        print('Total number of entries: ', end=' ')
        print(len(self.wordCountOfEntriesDict))
        print('First entry: ', end=' ')
        print(Helper.prettyPrintDate(self.firstDate))
        print('Last entry: ', end=' ')
        print(Helper.prettyPrintDate(self.mostRecentDate))
        print('Total days from first to last entry: ', end=' ')
        totalDays = self.mostRecentDate - self.firstDate #this is correct
        days = totalDays.days
        print(days)
        print('Percentage of days from first to last with an entry: ', end=' ')
        print(str(round(float(len(self.wordCountOfEntriesDict)) / days * 100, 2)) + '%')
        print('Average length per entry: ', end=' ')
        numberOfEntries = len(self.wordCountOfEntriesDict)
        sumOfLengths = 0
        longestEntryLength = 0
        for date in list(self.wordCountOfEntriesDict.keys()):
            length = self.wordCountOfEntriesDict[date]
            if length > longestEntryLength:
                longestEntryLength = length
                longestEntryDate = date
            sumOfLengths += length 
        print(round(float(sumOfLengths) / numberOfEntries, 2))
        print('Longest entry: ' + str(longestEntryLength) + ' words on ', end=' ')
        print(Helper.prettyPrintDate(longestEntryDate))
        print('Total number of words written: ', end=' ')
        print(locale.format("%d", self.totalNumberOfWords, grouping=True))



###############################################################################################
# Names
###############################################################################################
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

    #try to guess what is a name by looking for capitalized letters in the middle of sentences
    def getGuessedNames(self):
        newNames = set()
        print('Are these names? (y/n)')
        print(self.guessedNamesSet)
        for name in self.guessedNamesSet:
            if name in self.namesSet:
                break
            inp = input(name + ': ')
            if inp == 'y':
                newNames.add(name.lower())

        f = open(self.namesURL, 'r+')
        for name in newNames:
            f.write(name + '\n')
        f.close()

    def guessNames(self, line):
        nameRegex = re.compile('[^\.]\s+([ABCDEFGHIJKLMNOPQRSTUVWXYZ][\w]+)\W')
        names = nameRegex.search(line)

        try: 
            for name in names.groups():
                if name.lower() not in self.namesSet:
                    self.guessedNamesSet.add(name)
        except:
            return

    #Add a name manually to the names set
    def addName(self, args):
        name = args[0]
        if name in self.namesDict:
            print("Name already added")
            return
        self.namesSet.add(name);
        f = open(self.namesURL, 'a')
        f.write('\n' + name)
        f.close()

    def removeName(self, name):
        self.namesSet.remove(name);
        f = open(self.namesURL, 'r+')
        f.clear()
        for name in self.namesSet:
            f.write(name) + '\n'
        f.close()


###############################################################################################
# Control Loop
###############################################################################################
    def main(self, args):
        self.mainSetup(args)
        self.runMainLoop()

    #break apart the main function for testing
    def mainSetup(self, args):
        locale.setlocale(locale.LC_ALL, 'en_US')
        fileurl = args.file

        if args.verbosity:
            self.prefs.VERBOSE = True
        if args.combineplurals:
            self.prefs.COMBINE_PLURALS = True
        if args.guessnames:
            self.prefs.GUESS_NAMES = True
        if args.markunder:
            self.prefs.DO_MARK_UNDER = True
            print('Set DO_MARK_UNDER=True')
#        if args.noMarkunder:
#            self.prefs.DO_MARK_UNDER = False
#            print 'Set DO_MARK_UNDER=False'

        self.makeNamesSet()
        self.readFile(fileurl)

    def runMainLoop(self):
        if self.prefs.GUESS_NAMES:
            self.getGuessedNames()
        while True:
            print('''
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
    ''')
            if not self.parseInput(input('>')):
                return

    def parseInput(self, inpStr):
        parts = inpStr.split()
        command = parts[0].lower().strip().lstrip()
        args = parts[1:]
        if (self.prefs.VERBOSE):
            print('Parsed arguments: command: ' + str(command) + ' args: ' + str(args))
        return self.callInputFunction(command, args)

    def readFile(self, url):
        try:
            f = open(url, 'r')
        except:
            print('File not found')
            newPath = input('Enter new path > ');
            self.readFile(newPath) #TODO: this doesn't work for entirely unknown reasons
            return

        newdate = re.compile('\s*([0-9]{1,2}-[0-9]{1,2}-[0-9]{2})\s*')
        currentDateStr = None
        currentDateObj = None
        numWords = 0
        namesFound = set()
        totalWordNum = 0

        currentDayEntry = '' #holds all the lines for the current day, so we can compute a hash of the day later on
        
        line = f.readline()
        while (line != ''):
            if self.prefs.GUESS_NAMES:
                self.guessNames(line)
            #check a line to see if it's a date, therefore a new day
            dateFound = newdate.match(line)
            if dateFound != None: #it's a new date, so wrapup the previous date and set up to move onto the next one
                if namesFound != None:
                    self.addRelatedNames(namesFound)
                    namesFound = set()
                    self.dayEntryHashTable[currentDateObj] = hashlib.md5(currentDayEntry.encode()) #TODO: deal with first date

                if numWords > 0:
                    self.wordCountOfEntriesDict[currentDateObj] = numWords #should be here, since we want it triggered at the end
                totalWordNum += numWords
                numWords = 0
                currentDateStr = dateFound.group(0)
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
            line = f.readline()
            currentDayEntry += line #add line to the day's entry

        #need to capture the last date for the entry length
        self.wordCountOfEntriesDict[currentDateObj] = numWords 
        self.totalNumberOfWords = totalWordNum + numWords #need to get words from last line
        f.close()

    #args is a list of arguments in order
    def callInputFunction(self, inp, args):
        if inp == InputOption.HIGHEST.value:
            self.printHighest(args, None)
        elif inp == InputOption.LOOKUP.value:
            self.lookupWord(args)
        elif inp == InputOption.NAMES.value:
            self.printHighest(args, PrintOption.NAMES)
        elif inp == InputOption.RELATED.value:
            self.printHighest(args, PrintOption.RELATED)
        elif inp == InputOption.GRAPH.value:
            self.graphAnalytics(args)
        elif inp == InputOption.GRAPH_ENTRIES.value:
            self.graphEntries(args)
        # elif inp == 'gpd':
        #     self.graphAnalyticsPerDay(args)
        elif inp == InputOption.WPD.value:
            self.printHighest(args, PrintOption.WORDSPERDAY)
        elif inp == InputOption.NPD.value:
            self.printHighest(args, PrintOption.NAMESPERDAY)
        elif inp == InputOption.ADDNAME.value:
            self.addName(args)
        elif inp == InputOption.OPTION.value:
            print("Setting options isn't supported yet")
            pass
        elif inp == InputOption.LENGTH.value:
            self.printHighest(args, PrintOption.LENGTH)
        elif inp == InputOption.GRAPH_LENGTH.value:
            self.graphNameValue(self.wordCountOfEntriesDict)
        elif inp == InputOption.OVERALL.value:
            self.overallAnalytics()
        elif inp == InputOption.EXIT.value:
            return False
        else:
            print('Unknown command.')
        return True

###############################################################################################
# Main 
###############################################################################################
#Options need to be set on startup
if __name__ == '__main__':
    wf = WordFrequencies()

    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Path to file to examine')
    parser.add_argument('-v', '--verbosity', action='store_true', help='Enable verbose output')
    parser.add_argument('-p', '--combineplurals', action='store_true', help='Combine plurals')
    parser.add_argument('-g', '--guessnames', action='store_true', help='Guess names')
    parser.add_argument('-m', '--markunder', action='store_true', help='Enable markunder')
    parser.add_argument('-nm', '--noMarkunder', action='store_false', help='Disable markunder')
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
    maybe generate a mark under text file that shadows the journal with markup on the names for disambiguation
        this could also work toward caching
        maybe calculate a hash of the day after going through and generating the markdown then using that to see what has been updated
        

have a reverse order flag of some sort (allow to view in ascending order rather than descending)

allow option to filter by dates


connect this to other things
    step counter 
    google location
    texts sent/received
    pictures


make a gui navigable interface

noMarkUnder isn't utilized


Bugs:
fix axes on graphing
firstDate isn't accurate - isn't picking up 8-08-10, possible bug because it's the first date in there (but test case works)
days are off by one
related is broken

'''
