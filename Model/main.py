import argparse
import re
import os
import operator
import argparse
import matplotlib.pyplot as plt
from datetime import datetime

namesSet = set()
wordsDict = {} #{ word : ( count , last occurence , first occurence ) }
namesDict = {} #{ name : ( count , last occurence ) }
wordsPerDayDict = {} #{ word : ( count , last occurence ) } only counts one occurence per day
namesPerDayDict = {} #{ word : ( count , last occurence ) }
namesToGraphDict = {} #{ word : [ [ date , count ] ] }
guessedNamesSet = set()
namesURL = os.path.dirname(os.path.realpath(__file__)) + '/names.txt'
illegalCharacters = ['\\','{','}'] #characters that a word can't start with

WORD_COL_WIDTH = 20
NUM_COL_WIDTH = 6
DATE_COL_WIDTH = 8

debug = False

#try to guess what is a name by looking for capitalized letters in the middle of sentences
def getGuessedNames():
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

def guessNames(line):
    nameRegex = re.compile('[^\.] ([ABCDEFGHIJKLMNOPQRSTUVWXYZ][\w+|\.])')
    names = nameRegex.search(line)

    try: 
        for name in names.groups():
            guessedNamesSet.add(name)
        #print names.groups() #TODO: regex is broken (doesn't capture all matches)
    except:
        return

#Add a name manually to the names set
def addName(name):
    if name in namesDict:
        print "Name already added"
        return
    namesSet.add(name);
    f = open(namesURL, 'a')
    f.write(name + '\n')
    f.close()

def removeName(name):
    namesSet.remove(name);
    f = open(namesURL, 'r+')
    f.clear()
    for name in namesSet:
        f.write(name) + '\n'
    f.close()

def valid(word):
    if len(word) == 0:
        return False;
    if word[0] in illegalCharacters:
        return False
    return True

def cleanWord(word):
    word = word.strip().lstrip().lower();
    regex = re.compile('([\w|-|\']*)')
    match = regex.match(word)
    word = match.group(0)
    return word

#parse a line and add the words to the dictionaries
def addLine(line, currentDate):
    words = line.split(' ')
    for word in words:
        word = cleanWord(word)

        if not valid(word):
            continue

        #names
        if word in namesSet:
            try:
                namesDict[word] = (namesDict[word][0] + 1, currentDate)
            except:
                namesDict[word] = (1, currentDate)

            #names per day
            try:
                if namesPerDayDict[word][1] != currentDate:
                    namesPerDayDict[word] = (namesPerDayDict[word][0] + 1, currentDate)
            except:
                namesPerDayDict[word] = (1, currentDate)

            #names for graphing purposes
            try:
                namesToGraphDict[word] #trigger exception
                if namesToGraphDict[word][-1][0] == currentDate: #increment count
                    namesToGraphDict[word][-1][1] += 1
                else: #start a new tuple with a new date
                    namesToGraphDict[word].append([currentDate, 1])

            except: #this name hasn't been encountered yet
                namesToGraphDict[word] = [[currentDate, 1]]

        #words
        try:
            wordsDict[word] = (wordsDict[word][0] + 1, currentDate, wordsDict[word][2])
        except:
            wordsDict[word] = (1, currentDate, currentDate)
        
        #words per day
        try:
            if wordsPerDayDict[word][1] != currentDate:
                wordsPerDayDict[word] = (wordsPerDayDict[word][0] + 1, currentDate)
        except:
                wordsPerDayDict[word] = (1, currentDate)

#graphs the number of occurences of the name per day
def graphAnalytics(name):
    #{ word : [ [ date , count ] ] }
    try:
        x = [datetime.strptime(date[0] ,'%m-%d-%y') for date in namesToGraphDict[name]]
        y = [count[1] for count in namesToGraphDict[name]]
        
        ax = plt.subplot(111)
        ax.bar(x, y, width=2)
        ax.xaxis_date()

        plt.show()
    except:
        print 'Illegal input - must be a valid name'

def lookupWordPrompt():
    while True:
        inp = raw_input('Enter word for lookup: ')
        try:
            print inp + ': ' + str(wordsDict[inp])
        except:
            print 'Word not found'

def splitDate(date):
    split1 = date.find('-')
    split2 = date.find('-',split1)
    split2 = split2 + split1 + 1
    return (int(date[:split1]), int(date[split1+1:split2]), int(date[split2+1:]))

#returns date1 - date2 in date format
def subtractDates(date1, date2): 
    split1 = splitDate(date1)
    date1 = datetime(year=split1[2], day=split1[1], month=split1[0])

    split2 = splitDate(date2)
    date2 = datetime(year=split2[2], day=split2[1], month=split2[0])

    diff = date1 - date2
    return diff

def lookupWord(word):
    print word + ': '
    print 'First usage: ' + str(wordsDict[word][2])
    print 'Last usage: ' + str(wordsDict[word][1])
    total_uses = wordsDict[word][0]
    print 'Total usages: ' + str(total_uses)
    length = subtractDates(wordsDict[word][1], wordsDict[word][2]).days
    print 'Length from first use to last: ' + str(length)
    print 'Average usages per day: ' + str(float(total_uses) / length)
    #print 'Percentage of days with a useage: ' + str()

def printAll(names):
    printHighest(float('inf'), names)

def makeOutputPrettyHelper(header, word, count, date):
    if header:
        print 'Word',
        print ' ' * (WORD_COL_WIDTH - 4),
    else:
        if len(word) <= WORD_COL_WIDTH:
            print word,
            chars_left = WORD_COL_WIDTH - len(word)
            print ' ' * chars_left,
        else:
            print word[:WORD_COL_WIDTH],

    if header:
        print 'Count',
        print ' ' * (NUM_COL_WIDTH - 5),
    else:
        #TODO: deal with overshoot on numbers and date
        print count,
        print ' ' * (NUM_COL_WIDTH - len(str(count))),

    if header:
        print 'Last Occurence',
    else:
        print date,
    print ' ' * (DATE_COL_WIDTH - len(date))

    if header:
        print '-'*(38) #WORD_COL_WIDTH + NUM_COL_WIDTH + DATE_COL_WIDTH
        #TODO: make this a variable rather than a hardcoded number (and figure out why the variable width is off by 4)

def makeOutputPretty(inp): #( word : ( count , last occurence ) )
    word = inp[0]
    count = inp[1][0]
    date = inp[1][1]
    makeOutputPrettyHelper(False, word, count, date)

def makePrettyHeader():
    makeOutputPrettyHelper(True, '', '', '')
    
#print the x most occuring words
#num: number to print. if 'all', prints all
def printHighest(num, option):
    if num == 'all':
        print "setting to all"
        num = len(namesDict) #TODO: all doesn't work
        print num
    num = int(num)
    print "num: ",
    print num
    if option == 'names':
        sortedNamesDict = sorted(namesDict.items(), key=operator.itemgetter(1))
        sortedNamesDict.reverse()
        if num > len(sortedNamesDict):
            num = len(sortedNamesDict)
        makePrettyHeader()
        for x in xrange(0,num):
            makeOutputPretty(sortedNamesDict[x])
    elif option == 'wordsPerDay':
        sortedWordsPerDayDict = sorted(wordsPerDayDict.items(), key=operator.itemgetter(1))
        sortedWordsPerDayDict.reverse()
        if num > len(sortedWordsPerDayDict):
            num = len(sortedWordsPerDayDict)
        for x in xrange(0,num):
            makeOutputPretty(sortedWordsPerDayDict[x])
    elif option == 'namesPerDay':
        sortedNamesPerDayDict = sorted(namesPerDayDict.items(), key=operator.itemgetter(1))
        sortedNamesPerDayDict.reverse()
        if num > len(sortedNamesPerDayDict):
            num = len(sortedNamesPerDayDict)
        for x in xrange(0,num):
            makeOutputPretty(sortedNamesPerDayDict[x])
    else: #regular words
        sortedWordsDict = sorted(wordsDict.items(), key=operator.itemgetter(1))
        sortedWordsDict.reverse()
        if num > len(sortedWordsDict):
            num = len(sortedWordsDict)
        for x in xrange(0,num):
            makeOutputPretty(sortedWordsDict[x])

#Put date into a format that can be recognized by datetime
def formatDate(date_in):
    date = date_in.strip().lstrip();

    #currently assume they're fairly correctly formatted
    #won't get in here in the first place if they're not
    if re.search('^[0-9]-', date):
        date = '0' + date
    if re.search('-[0-9]-', date):
        date = date[:3] + '0' + date[3:]
    return date

def readFile(url):
    try:
        f = open(url, 'r')
    except:
        print('File not found')
        readFile(raw_input('Enter new path > ')) #TODO: not sure if this work
    
    line = f.readline()

    currentDate = None;
    while (line != ''):
        #check a line to see if it's a date, therefore a new day
        newdate = re.compile('\s*([0-9]{1,2}-[0-9]{1,2}-[0-9]{2})\s*')
        res = newdate.match(line)
        if res != None: #date found
            currentDate = res.group(0);
            currentDate = formatDate(currentDate)
            line = line[len(currentDate):] #remove date from line, so it's not a word

        if currentDate != None:
            addLine(line, currentDate)
            guessNames(line)
        line = f.readline()

def callInputFunction(inp, arg):
    '''print 'inp: ',
    print inp,
    print type(inp)
    print 'arg: ',
    print arg,
    print type(arg)'''
    if inp == 'highest':
        printHighest(arg, None)
    elif inp == 'lookup':
        lookupWord(arg)
    elif inp == 'names':
        print "names called: "
        print "arg: ",
        print arg
        printHighest(arg, 'names')
    elif inp == 'graph':
        graphAnalytics(arg)
    elif inp == 'wpd':
        printHighest(arg, 'wordsPerDay')
    elif inp == 'npd':
        printHighest(arg, 'namesPerDay')
    elif inp == 'addname':
        addName(arg)
    else:
        pass

def enableVerbosity():
    verbose = True;

#populate namesList from file
def makeNamesSet():
    try:
        f = open(namesURL, 'r') #TODO: error handling
    except:
        raise Exception("Names file not found")
    namesSet.clear()
    line = f.readline()
    while line != '':
        namesSet.add(line.strip().lower())
        line = f.readline()

def main(args):
    makeNamesSet()
    readFile(args.file)
    
    legalWordParts = '[^{}]'
    #TODO: there's a better way to do this I'm sure
    regexDict = {
        re.compile('\s*highest\s+([[0-9]+|all])\s*', re.IGNORECASE): 'highest',
        re.compile('\s*wpd\s+([[0-9]+|all])\s*', re.IGNORECASE): 'wpd',
        re.compile('\s*[l|L]ookup\s+([^{}]+)\s*', re.IGNORECASE): 'lookup',
        re.compile('\s*names\s+([0-9]+|all)\s*', re.IGNORECASE): 'names',
        re.compile('\s*npd\s+([[0-9]+|all])\s*', re.IGNORECASE): 'npd',
        re.compile('\s*graph\s+([^{}]+)\s*', re.IGNORECASE): 'graph',
        re.compile('\s*add name\s+([^{}]+)\s*', re.IGNORECASE): 'addname',
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
Graph                       graph [name]
Add name                    add name [name]
Exit                        exit
'''
        inp = raw_input('>')
        for regex in regexDict.keys():
            matches = regex.match(inp)
            if matches != None:
                if regexDict[regex] == 'exit':
                    return
                callInputFunction(regexDict[regex], matches.groups(0)[0])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to file to examine")
    #parser.add_argument('-v', '--verbose', help="Enable verbose output", action="enableVerbosity()")
    args = parser.parse_args()

    main(args)




'''
TODO: 
something weird going on with apostrophes (specifically "didn't")
make names sensitive to capitals (ex. "will" is very high, because of the everyday word)

distinguish between different people with the same spelling of names
    possibly by looking at other people that are frequently mentioned with them in the same day to determine

length of entries / average length of entries per day / look up or graph trends

analytics:

'''