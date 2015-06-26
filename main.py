import argparse
import re
import operator
import argparse
import matplotlib.pyplot as plt
from datetime import datetime

namesSet = set()
wordsDict = {} #{ word : ( count , last occurence ) }
namesDict = {} #{ name : ( count , last occurence ) }
wordsPerDayDict = {} #{ word : ( count , last occurence ) } only counts one occurence per day
namesPerDayDict = {} #{ word : ( count , last occurence ) }
namesToGraphDict = {} #{ word : [ [ date , count ] ] }
guessedNamesSet = set()
namesURL = 'names.txt'
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
            wordsDict[word] = (wordsDict[word][0] + 1, currentDate)
        except:
            wordsDict[word] = (1, currentDate)
        
        #words per day
        try:
            if wordsPerDayDict[word][1] != currentDate:
                wordsPerDayDict[word] = (wordsPerDayDict[word][0] + 1, currentDate)
        except:
                wordsPerDayDict[word] = (1, currentDate)

#Used to output to a format that excel can import
def graphAnalytics():
    for key in namesPerDayDict:
        namesList = namesPerDayDict[key]
    '''
    plt.figure();

    #create some data
    x_series = [0,1,2,3,4,5]
    y_series_1 = [x**2 for x in x_series]
    y_series_2 = [x**3 for x in x_series]
     
    #plot the two lines
    plt.plot(x_series, y_series_1)
    plt.plot(x_series, y_series_2)

    plt.savefig("example.png")
    '''

    '''
    x = [datetime.datetime(2010, 12, 1, 10, 0),
        datetime.datetime(2011, 1, 4, 9, 0),
        datetime.datetime(2011, 5, 5, 9, 0)]
    y = [4, 9, 2]
    '''

    #{ word : [ [ date , count ] ] }
    x = [datetime.strptime(date[0] ,'%m-%d-%y') for date in namesToGraphDict['becca']]
    y = [count[1] for count in namesToGraphDict['becca']]

    
    ax = plt.subplot(111)
    ax.bar(x, y, width=10)
    ax.xaxis_date()

    plt.show()
    

def lookupWordPrompt():
    while True:
        inp = raw_input('Enter word for lookup: ')
        try:
            print inp + ': ' + str(wordsDict[inp])
        except:
            print 'Word not found'

def lookupWord(word):
    print word + ': ' + str(wordsDict[word])

def printAll(names):
    printHighest(float('inf'), names)

def makeOutputPretty(inp): #( word : ( count , last occurence ) )
    word = inp[0]
    count = inp[1][0]
    date = inp[1][1]

    if len(word) <= WORD_COL_WIDTH:
        print word,
        chars_left = WORD_COL_WIDTH - len(word)
        print ' ' * chars_left,
    else:
        print word[:WORD_COL_WIDTH],

    #TODO: deal with overshoot on numbers and date
    print count,
    print ' ' * (NUM_COL_WIDTH - len(str(count))),

    print date,
    print ' ' * (DATE_COL_WIDTH - len(date))
    
#print the x most occuring words
#num: number to print. if 'all', prints all
def printHighest(num, option):
    if num == 'all':
        num = float('inf')
    if option == 'names':
        sortedNamesDict = sorted(namesDict.items(), key=operator.itemgetter(1))
        sortedNamesDict.reverse()
        if num > len(sortedNamesDict):
            num = len(sortedNamesDict)
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
        date = date[:2] + '0' + date[2:]

    return date

def readFile(url):
    f = open(url, 'r')
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
    print 'inp: ',
    print inp,
    print type(inp)
    print 'arg: ',
    print arg,
    print type(arg)
    if inp == 'highest':
        printHighest(int(arg), None)
    elif inp == 'lookup':
        lookupWord(arg)
    elif inp == 'names':
        printHighest(int(arg), 'names')
    else:
        pass

def main(args):
    makeNamesSet()
    readFile(args.file)

    legalWordParts = '[^{}]'
    regexDict = {
        re.compile('\s*highest ([[0-9]+|all])\s*'): 'highest',
        re.compile('\s*[l|L]ookup ([^{}]+)\s*'): 'lookup',
        re.compile('\s*names ([[0-9]+|all])\s*'): 'names'
    }

    graphAnalytics();

    '''
    print('Options:\n   Highest x words (highest [num | all])\n   Lookup (lookup [word])\n   Highest x names(names [num | all])')
    while True:
        inp = raw_input('>')

        for regex in regexDict.keys():
            matches = regex.match(inp)

            if matches != None:
                callInputFunction(regexDict[regex], matches.groups(0)[0])
    '''


def enableVerbosity():
    verbose = True;

#populate namesList from file
def makeNamesSet():
    f = open(namesURL, 'r') #TODO: error handling
    namesSet.clear()
    line = f.readline()
    while line != '':
        namesSet.add(line.strip().lower())
        line = f.readline()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to file to examine")
    #parser.add_argument('-v', '--verbose', help="Enable verbose output", action="enableVerbosity")
    args = parser.parse_args()

    main(args)




'''
TODO: 
something weird going on with apostrophes (specifically "didn't")
make names sensitive to capitals (ex. "will" is very high, because of the everyday word)

analytics:
store dates of names, export to excel, graph
'''