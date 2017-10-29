import datetime

class WordDict():
    #{ word : { 'count': count , 'lastDate': last occurence , 'firstDate': first occurence , 'wasUpper': started with uppercase letter } }

    internalDict = {}

    def checkInvariants(self):
        pass

    COUNT = 'count'
    LAST_DATE = 'lastDate'
    FIRST_DATE = 'firstDate'
    WAS_UPPER = 'wasUpper'


    #Add a new word to the dictionary, or if the word exists already, replace its fields with the supplied new values
    #returns True if added successfully and False if not
    def addOrReplaceWord(self, word, count, lastDate, firstDate, wasUpper):
        if type(count) is not int:
            return False
        if type(lastDate) is not datetime.datetime:
            return False
        if type(firstDate) is not datetime.datetime:
            return False
        if type(wasUpper) is not bool:
            return False

        self.internalDict[word] = {self.COUNT: count, self.LAST_DATE: lastDate, self.FIRST_DATE: firstDate, self.WAS_UPPER: wasUpper}
        return self.checkInvariants()

    #Adds a new word to the dictionary. If it already exists, return False and do nothing
    def addWord(self, word, count, lastDate, firstDate, wasUpper):
        if word in self.internalDict:
            return False
        if type(count) is not int:
            return False
        if type(lastDate) is not datetime.datetime:
            return False
        if type(firstDate) is not datetime.datetime:
            return False
        if type(wasUpper) is not bool:
            return False

        self.internalDict[word] = {self.COUNT: count, self.LAST_DATE: lastDate, self.FIRST_DATE: firstDate, self.WAS_UPPER: wasUpper}
        return self.checkInvariants()

    #check if a word exists in the dictionary
    def exists(self, word):
        try:
            self.internalDict[word]
            return True
        except:
            return False

    def get(self, word):
        if not self.exists(word):
            return False
        return self.internalDict[word]

    #returns None if not added successfully
    def getCount(self, word):
        if self.exists(word):
            return self.internalDict[word][self.COUNT]
        else:
            return None

    def getFirstDate(self, word):
        if self.exists(word):
            return self.internalDict[word][self.FIRST_DATE]
        else:
            return None

    def getLastDate(self, word):
        if self.exists(word):
            return self.internalDict[word][self.LAST_DATE]
        else:
            return None

    def incrementCount(self, word):
        if not self.exists(word):
            return False
        self.internalDict[word][self.COUNT] = self.internalDict[word][self.COUNT] + 1
        return True

    def __str__(self):
        outStr = '';
        for word in self.internalDict:
            outStr += word + ': ' + str(self.internalDict[word]) + '\n'
        return outStr

