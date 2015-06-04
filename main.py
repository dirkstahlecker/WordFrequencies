import argparse
import re

namesList = [];
wordsDict = {}
namesDict = {}

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

    print wordsDict

def main(url, forNames=False):
    f = open(url, 'r')
    line = f.readline()

    #check a line to see if it's a date, therefore a new day
    newdate = re.compile('\s*[0-9]{1,2}-[0-9]{1,2}-[0-9]{1,2}\s*')
    res = newdate.match(line)
    if res != None: #date found
        addLine(line, forNames) #remove this
    else:
        addLine(line, forNames)


if __name__ == '__main__':
    #parser = argparse.ArgumentParser()
    #parser.parse_args()
    main('/users/dirk/desktop/journal_test.txt')