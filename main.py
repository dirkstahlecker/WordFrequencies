import argparse
import re
import operator
import argparse

namesSet = set()
wordsDict = {} #{ word : ( count , last occurence ) }
namesDict = {} #{ name : ( count , last occurence ) }
wordsPerDayDict = {} #{ word : ( count , last occurence ) } only counts one occurence per day
namesPerDayDict = {} #{ word : ( count , last occurence ) }
guessedNamesSet = set()
namesURL = 'names.txt'
illegalCharacters = ['\\','{','}'] #characters that a word can't start with

WORD_COL_WIDTH = 20
NUM_COL_WIDTH = 6
DATE_COL_WIDTH = 8

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


def readFile(url):
    f = open(url, 'r')
    line = f.readline()

    currentDate = None;
    while (line != ''):
        #check a line to see if it's a date, therefore a new day
        newdate = re.compile('\s*([0-9]{1,2}-[0-9]{1,2}-[0-9]{1,2})\s*')
        res = newdate.match(line)
        if res != None: #date found
            currentDate = res.group(0);
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
        printHighest(arg, 'names')
    else:
        pass

def main():
    readFile('/Volumes/Disk Image/journal.rtf')
    makeNamesSet()

    legalWordParts = '[^{}]'
    regexDict = {
        re.compile('\s*highest ([[0-9]+|all])\s*'): 'highest',
        re.compile('\s*[l|L]ookup ([^{}]+)\s*'): 'lookup',
        re.compile('\s*names ([[0-9]+|all])\s*'): 'names'
    }

    print('Options:\n   Highest x words (highest [num | all])\n   Lookup (lookup [word])\n   Highest x names(names [num | all])')
    while True:
        inp = raw_input('>')

        for regex in regexDict.keys():
            matches = regex.match(inp)

            if matches != None:
                callInputFunction(regexDict[regex], matches.groups(0)[0])



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
    args = parser.parse_args()

    main()




'''
TODO: 
something weird going on with apostrophes (specifically "didn't")
make names sensitive to capitals (ex. "will" is very high, because of the everyday word)
'''