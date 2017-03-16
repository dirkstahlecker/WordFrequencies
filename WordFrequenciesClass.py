import argparse
import re
import os
import operator
import argparse
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta

def enum(**enums):
    return type('Enum', (), enums)

class WordFrequencies:
    namesSet = set()
    wordsDict = {} #{ word : ( count , last occurence , first occurence ) }
    namesDict = {} #{ name : ( count , last occurence ) }
    wordsPerDayDict = {} #{ word : ( count , last occurence ) } only counts one occurence per day
    namesPerDayDict = {} #{ word : ( count , last occurence ) }
    namesToGraphDict = {} #{ word : [ [ date , count ] ] }
    namesToGraphDictUniqueOccurences = {} #{ word : [ date ] }
    lengthOfEntriesDict = {} #{ datetime : word count }
    guessedNamesSet = set()
    namesURL = os.path.dirname(os.path.realpath(__file__)) + '/names.txt'
    illegalCharacters = ['\\','{','}'] #characters that a word can't start with

    WORD_COL_WIDTH = 20
    NUM_COL_WIDTH = 6
    DATE_COL_WIDTH = 8

    debug = False


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
    def addName(self, name):
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

    def valid(self, word):
        word = self.cleanWord(word)
        if len(word) == 0:
            return False;
        if word[0] in self.illegalCharacters:
            return False
        return True

    def cleanWord(self, word):
        word = word.strip().lstrip().lower();
        regex = re.compile('([\w|-|\']*)')
        match = regex.match(word)
        word = match.group(0)
        return word

    #parse a line and add the words to the dictionaries
    def addLine(self, line, currentDate):
        words = line.split(' ')

        for word in words:
            if not self.valid(word):
                words.remove(word)
                continue

            word = self.cleanWord(word)

            #names
            if word in self.namesSet:
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
                self.wordsDict[word] = (self.wordsDict[word][0] + 1, currentDate, self.wordsDict[word][2])
            except:
                self.wordsDict[word] = (1, currentDate, currentDate)
            
            #words per day
            try:
                if self.wordsPerDayDict[word][1] != currentDate:
                    self.wordsPerDayDict[word] = (self.wordsPerDayDict[word][0] + 1, currentDate)
            except:
                    self.wordsPerDayDict[word] = (1, currentDate)

        return len(words)

    #graphs the number of occurences of the name per day
    def graphAnalytics(self, name):
        #{ word : [ [ date , count ] ] }
        try:
            x = [datetime.strptime(date[0] ,'%m-%d-%y') for date in self.namesToGraphDict[name]]
            y = [count[1] for count in self.namesToGraphDict[name]]
            
            ax = plt.subplot(111)
            ax.bar(x, y, width=2)
            ax.xaxis_date()

            plt.show()
        except:
            print 'Illegal input - must be a valid name'
    '''
    #graphs unique occurences of a name per day
    def graphAnalyticsPerDay(self, name):
        #{ word : [ [ date , count ] ] }
        try:
            x = [datetime.strptime(date[0] ,'%m-%d-%y') for date in self.namesToGraphDictUniqueOccurences[name]]
            y = [count[1] for count in self.namesToGraphDictUniqueOccurences[name]]
            
            ax = plt.subplot(111)
            ax.bar(x, y, width=2)
            ax.set_xlabel('Date')
            ax.set_ylabel('')
            ax.xaxis_date()

            plt.show()
        except:
            print 'Illegal input - must be a valid name'
    '''

    def lookupWordPrompt(self):
        while True:
            inp = raw_input('Enter word for lookup: ')
            try:
                print inp + ': ' + str(self.wordsDict[inp])
            except:
                print 'Word not found'

    def splitDate(self, date):
        split1 = date.find('-')
        split2 = date.find('-',split1)
        split2 = split2 + split1 + 1
        return (int(date[:split1]), int(date[split1+1:split2]), int(date[split2+1:]))

    #TODO: need to append "20" to start of dates, to make them four digits for pretty printing to work
    def makeDate(self, dateStr):
        date = self.splitDate(self.formatDate(dateStr))
        year = date[2]
        #make the year four digits
        if year < 100:
            year += 2000
        month = date[0]
        day = date[1]
        try:
            return datetime(year=year, day=day, month=month) #goes year, month, day
        except:
            print 'ERROR in makeDate: '
            print date,
            print ' is invalid'
            print date[2]
            print date[1]
            print date[0]
            print type(date)
            print type(date[2])

    def numEntriesAndLengthOfEntriedBetweenDates(self, date1, date2):
        if (date1 > date2):
            print 'date1 < date2'
            return 0
        totalSum = 0
        numDays = 0
        workingDate = date1
        while True:
            try:
                totalSum += self.lengthOfEntriesDict[workingDate]
                numDays += 1
            except:
                pass
            workingDate += timedelta(days=1)
            if workingDate >= date2:
                break
        return (numDays, totalSum)

    def lookupWord(self, word):
        print word + ': '
        try:
            print 'First usage: ' + str(self.wordsDict[word][2])
            print 'Last usage: ' + str(self.wordsDict[word][1])
        except:
            print 'No ocurrences found.'
        try:
            total_uses = self.wordsDict[word][0]
            print 'Total usages: ' + str(total_uses)
            #length = (self.wordsDict[word][1] - self.wordsDict[word][2]).days

            startDate = self.wordsDict[word][2] #these are intentially backwards - 1 is last occurence, 2 is first occurence
            endDate = self.wordsDict[word][1]
            length = self.numEntriesAndLengthOfEntriedBetweenDates(startDate, endDate)[0]

            print 'Length from first use to last: ' + str(length) + ' days'
            #TODO: this assumes that every day from first use to last exists. need to divide by how many entries there actually are
            print 'Average usages per day: ' + str(float(total_uses) / length)
            #print 'Percentage of days with a useage: ' + str()
        except:
            print 'No ocurrences found.'

    def lookupLength(self, date, date2):
        if date2 == None: #single word or total average
            if date == 'avg':
                print 'Average over all dates: ',
                totalSum = 0
                for d in self.lengthOfEntriesDict:
                    totalSum += self.lengthOfEntriesDict[d]
                print round(float(totalSum) / len(self.lengthOfEntriesDict), 2),
                print ' words per day'
            else:
                date = self.makeDate(date)
                print date.strftime("%A, %d. %B %Y")
                print 'Word count: ',
                print self.lengthOfEntriesDict[date]
        else: #date average range
            date = self.makeDate(date)
            date2 = self.makeDate(date2)
            totalSum = self.numEntriesAndLengthOfEntriedBetweenDates(date, date2)[1]
            print date.strftime("%A, %d. %B %Y"),
            print ' to ',
            print date2.strftime("%A, %d. %B %Y")
            print round(float(totalSum) / totalSum, 2), #TODO: this line is wrong
            print ' average words per day'

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

    def makePrettyHeader(self):
        self.makeOutputPrettyHelper(True, '', '', '')
        
    #print the x most occuring words
    #num: number to print. if 'all', prints all
    def printHighest(self, num_in, option):
        #TODO: clean up the num all logic
        num = int(num_in)
        if option == 'names':
            if num_in == 'all':
                num = len(self.namesDict)
            self.sortedNamesDict = sorted(self.namesDict.items(), key=operator.itemgetter(1))
            self.sortedNamesDict.reverse()
            if num > len(self.sortedNamesDict):
                num = len(self.sortedNamesDict)
            self.makePrettyHeader()
            for x in xrange(0,num):
                self.makeOutputPretty(self.sortedNamesDict[x])
        elif option == 'wordsPerDay':
            if num_in == 'all':
                num = len(self.wordsPerDayDict)
            self.sortedWordsPerDayDict = sorted(self.wordsPerDayDict.items(), key=operator.itemgetter(1))
            self.sortedWordsPerDayDict.reverse()
            if num > len(self.sortedWordsPerDayDict):
                num = len(self.sortedWordsPerDayDict)
            for x in xrange(0,num):
                self.makeOutputPretty(self.sortedWordsPerDayDict[x])
        elif option == 'namesPerDay':
            if num_in == 'all':
                num = len(self.namesPerDayDict)
            self.sortedNamesPerDayDict = sorted(self.namesPerDayDict.items(), key=operator.itemgetter(1))
            self.sortedNamesPerDayDict.reverse()
            if num > len(self.sortedNamesPerDayDict):
                num = len(self.sortedNamesPerDayDict)
            for x in xrange(0,num):
                self.makeOutputPretty(self.sortedNamesPerDayDict[x])
        else: #regular words
            if num_in == 'all':
                num = len(self.wordsDict)
            self.sortedWordsDict = sorted(self.wordsDict.items(), key=operator.itemgetter(1))
            self.sortedWordsDict.reverse()
            if num > len(self.sortedWordsDict):
                num = len(self.sortedWordsDict)
            for x in xrange(0,num):
                self.makeOutputPretty(self.sortedWordsDict[x])

    #Put date into a format that can be recognized by datetime
    #returns a string of the date in the proper format
    def formatDate(self, date_in):
        date = date_in.strip().lstrip();

        #currently assume they're fairly correctly formatted
        #won't get in here in the first place if they're not
        if re.search('^[0-9]-', date):
            date = '0' + date
        if re.search('-[0-9]-', date):
            date = date[:3] + '0' + date[3:]
        return date

    def readFile(self, url):
        try:
            f = open(url, 'r')
        except:
            print('File not found')
            self.readFile(raw_input('Enter new path > ')) #TODO: not sure if this works

        newdateRegex = re.compile('\s*([0-9]{1,2}-[0-9]{1,2}-[0-9]{2})\s*')
        currentDate = None;
        numWords = 0
        
        line = f.readline()
        while (line != ''):
            line = line.strip().lstrip()
            #check a line to see if it's a date, therefore a new day
            res = newdateRegex.match(line)
            if res != None: #date found
                self.lengthOfEntriesDict[currentDate] = numWords
                numWords = 0
                currentDate = res.group(0)
                line = line[len(currentDate):] #remove date from line, so it's not a word
                currentDate = self.makeDate(currentDate)

            if currentDate != None:
                numWords += self.addLine(line, currentDate)
                self.guessNames(line)
            line = f.readline()

    def callInputFunction(self, inp, matchGrp):
        arg = matchGrp[0]
        if inp == 'highest':
            self.printHighest(arg, None)
        elif inp == 'lookup':
            self.lookupWord(arg)
        elif inp == 'names':
            self.printHighest(arg, 'names')
        elif inp == 'graph':
            self.graphAnalytics(arg)
        elif inp == 'gpd':
            self.graphAnalyticsPerDay(arg)
        elif inp == 'wpd':
            self.printHighest(arg, 'wordsPerDay')
        elif inp == 'npd':
            self.printHighest(arg, 'namesPerDay')
        elif inp == 'addname':
            self.addName(arg)
        elif inp == 'length':
            print 'single date or total average'
            self.lookupLength(arg, None)
        elif inp == 'length_range':
            date2 = matchGrp[1]
            self.lookupLength(arg, date2)
        elif inp == 'guess_names':
            #TODO
        else:
            pass

    def enableVerbosity(self):
        verbose = True;

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

    def main(self, fileurl):
        self.makeNamesSet()
        self.readFile(fileurl)

        #TODO: there's a better way to do this I'm sure
        regexDict = {
            re.compile('\s*highest\s+([\d]+|all)\s*', re.IGNORECASE): 'highest',
            re.compile('\s*wpd\s+([\d]+|all)\s*', re.IGNORECASE): 'wpd',
            re.compile('\s*[l|L]ookup\s+([^{}]+)\s*', re.IGNORECASE): 'lookup',
            re.compile('\s*names\s+([\d]+|all)\s*', re.IGNORECASE): 'names',
            re.compile('\s*npd\s+([\d]+|all)\s*', re.IGNORECASE): 'npd',
            re.compile('\s*length\s+(([0-9]{1,2}-[0-9]{2}-[0-9]{2})|avg)\s*', re.IGNORECASE): 'length',
            re.compile('length\s+range\s+([0-9]{1,2}-[0-9]{2}-[0-9]{2})\s+([0-9]{1,2}-[0-9]{2}-[0-9]{2})', re.IGNORECASE): 'length_range',
            re.compile('\s*graph\s+([^{}]+)\s*', re.IGNORECASE): 'graph',
            #re.compile('\s*gpd\s+([^{}]+)\s*', re.IGNORECASE): 'gpd',
            re.compile('\s*add\s+name\s+([^{}]+)\s*', re.IGNORECASE): 'addname',
            re.compile('\s*guess\s+names\s+([^{}]+)\s*', re.IGNORECASE): 'guess_names',
            re.compile('\s*exit\s*', re.IGNORECASE): 'exit'
        }
        
        while True:
            print '''
    Options:
    Highest x words             highest [num | all]
    Highest x words per day     wpd [num | all]
    Lookup                      lookup [word]
    Highest x names             names [num | all]
    Highest x names per day     npd [num | all]
    Entry length                length [date | avg | range dateFrom dateTo]
    Graph names                 graph [name]
    Graph names per day         gpd [name]
    Add name                    add name [name]
    Exit                        exit
    '''
            inp = raw_input('>')
            for regex in regexDict.keys():
                matches = regex.match(inp)
                if matches != None:
                    if regexDict[regex] == 'exit':
                        return
                    self.callInputFunction(regexDict[regex], matches.groups(0))

if __name__ == '__main__':
    #Numbers = enum(ONE=1, TWO=2, THREE='three')
    #use this as an enum, with Numbers.ONE, etc

    wf = WordFrequencies()

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to file to examine")
    #parser.add_argument('-v', '--verbose', help="Enable verbose output", action="enableVerbosity()")
    args = parser.parse_args()

    wf.main(args.file)




'''
TODO: 
make names sensitive to capitals (ex. "will" is very high, because of the everyday word)

distinguish between different people with the same spelling of names
    possibly by looking at other people that are frequently mentioned with them in the same day to determine

use enums for all the arguments for the keywords for the different options - enum options utilized with the new enum class in the top

error handling for incorrect arguments

analytics:

'''