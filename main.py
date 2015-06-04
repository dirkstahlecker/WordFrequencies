import argparse
import re
import operator

namesList = []
wordsDict = {}
namesDict = {}
guessedNamesSet = set()

#try to guess what is a name by looking for capitalized letters in the middle of sentences
def getGuessedNames():
    pass

def guessNames(line):
    nameRegex = re.compile('[^\.] ([ABCDEFGHIJKLMNOPQRSTUVWXYZ]\w+)')
    names = nameRegex.search(line)

    try: 
        for name in names.groups():
            guessedNamesSet.add(name)
        print names.groups() #TODO: regex is broken (doesn't capture all matches)
    except:
        return

#parse a line and add the words to the dictionaries
def addLine(line, forNames):
    words = line.split(' ')
    for word in words:
        word = word.strip().lower()
        if forNames:
            if word not in namesList:
                break
        try:
            if forNames:
                namesDict[word] += 1
            else:
                wordsDict[word] += 1
        except:
            if forNames:
                namesDict = 1
            else:
                wordsDict[word] = 1


def printHighest(num):
    sortedWordsDict = sorted(wordsDict.items(), key=operator.itemgetter(1))
    sortedWordsDict.reverse()
    for x in xrange(0,num):
        print sortedWordsDict[x];

def main(url, forNames=False):
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
        addLine(line, forNames)
        guessNames(line)
        line = f.readline()


if __name__ == '__main__':
    #parser = argparse.ArgumentParser()
    #parser.parse_args()
    #main('/users/dirk/desktop/journal_test.txt')
    main('/Volumes/Disk Image/journal.rtf')
    printHighest(5)

    print 'guessedNamesSet: ',
    print guessedNamesSet


