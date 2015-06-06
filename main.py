import argparse
import re
import operator

namesSet = set()
wordsDict = {} #{ word : ( count , last occurence ) }
namesDict = {} #{ name : ( count , last occurence ) }
wordsPerDayDict = {} #{ word : ( count , last occurence ) } only counts one occurence per day
namesPerDayDict = {} #{ word : ( count , last occurence ) }
guessedNamesSet = set()
namesURL = 'names.txt'
illegalCharacters = ['\\','{','}'] #characters that a word can't start with

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

#parse a line and add the words to the dictionaries
def addLine(line, currentDate):
    words = line.split(' ')
    for word in words:
        word = word.strip().lower()

        if not valid(word):
            continue

        #names
        if word in namesSet:
            try:
                namesDict[word] += 1
            except:
                namesDict[word] = 1

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

def lookupWord():
    inp = raw_input('Enter word for lookup: ')
    print inp + ': ' + str(wordsDict[inp])

def printAll(names):
    printHighest(float('inf'), names)

def printHighest(num, names, perDay):
    if names == True:
        sortedNamesDict = sorted(namesDict.items(), key=operator.itemgetter(1))
        sortedNamesDict.reverse()

        if num > len(sortedNamesDict):
            num = len(sortedNamesDict);
        for x in xrange(0,num):
            print sortedNamesDict[x];
    elif perDay == False:
        sortedWordsDict = sorted(wordsDict.items(), key=operator.itemgetter(1))
        sortedWordsDict.reverse()
        if num > len(sortedWordsDict):
            num = len(sortedWordsDict);
        for x in xrange(0,num):
            print sortedWordsDict[x];
    else:
        sortedWordsPerDayDict = sorted(wordsPerDayDict.items(), key=operator.itemgetter(1))
        sortedWordsPerDayDict.reverse()
        if num > len(sortedWordsPerDayDict):
            num = len(sortedWordsPerDayDict);
        for x in xrange(0,num):
            print sortedWordsPerDayDict[x];


def main(url):
    f = open(url, 'r')
    line = f.readline()

    currentDate = None;
    while (line != ''):
        #check a line to see if it's a date, therefore a new day
        newdate = re.compile('\s*([0-9]{1,2}-[0-9]{1,2}-[0-9]{1,2})\s*')
        res = newdate.match(line)
        if res != None: #date found
            currentDate = res.group(0);

        if currentDate != None:
            addLine(line, currentDate)
            guessNames(line)
        line = f.readline()

#populate namesList from file
def makeNamesSet():
    f = open(namesURL, 'r') #TODO: error handling
    namesSet.clear()
    line = f.readline()
    while line != '':
        namesSet.add(line.strip().lower())
        line = f.readline()

if __name__ == '__main__':
    makeNamesSet()

    #parser = argparse.ArgumentParser()
    #parser.parse_args()
    #main('/users/dirk/desktop/journal_test.txt')
    main('/Volumes/Disk Image/journal.rtf')
    #printAll(True)
    printHighest(50, False, False)




'''
TODO: 
add per day
strip punctuation
make names sensitive to capitals (ex. "will" is very high, because of the everyday word)
'''