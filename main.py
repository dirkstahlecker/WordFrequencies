import argparse
import re
import operator

namesSet = set()
wordsDict = {}
namesDict = {}
guessedNamesSet = set()
namesURL = 'names.txt'

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
    nameRegex = re.compile('[^\.] ([ABCDEFGHIJKLMNOPQRSTUVWXYZ]\w+)')
    names = nameRegex.search(line)

    try: 
        for name in names.groups():
            guessedNamesSet.add(name)
        #print names.groups() #TODO: regex is broken (doesn't capture all matches)
    except:
        return

#parse a line and add the words to the dictionaries
def addLine(line):
    words = line.split(' ')
    for word in words:
        word = word.strip().lower()

        try:
            if word in namesSet:
                namesDict[word] += 1
            wordsDict[word] += 1
        except:
            if word in namesSet:
                namesDict[word] = 1
            wordsDict[word] = 1

def printAll(names):
    printHighest(float('inf'), names)

def printHighest(num, names):
    if names == True:
        sortedNamesDict = sorted(namesDict.items(), key=operator.itemgetter(1))
        sortedNamesDict.reverse()

        if num > len(sortedNamesDict):
            num = len(sortedNamesDict);
        for x in xrange(0,num):
            print sortedNamesDict[x];
    else:
        sortedWordsDict = sorted(wordsDict.items(), key=operator.itemgetter(1))
        sortedWordsDict.reverse()
        if num > len(sortedWordsDict):
            num = len(sortedWordsDict);
        for x in xrange(0,num):
            print sortedWordsDict[x];

def main(url):
    f = open(url, 'r')
    line = f.readline()
    while (line != ''):

        #check a line to see if it's a date, therefore a new day
        newdate = re.compile('\s*[0-9]{1,2}-[0-9]{1,2}-[0-9]{1,2}\s*')
        res = newdate.match(line)
        if res != None: #date found
            pass
        else:
            pass
        addLine(line)
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
    printAll(True)

    #print 'guessedNamesSet: ',
    #print guessedNamesSet


'''
TODO: 
make names sensitive to capitals (ex. "will" is very high, because of the everyday word)
'''