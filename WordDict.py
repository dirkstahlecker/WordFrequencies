import datetime

class WordDict():
    #{ word : { 'count': count , 'lastDate': last occurence , 'firstDate': first occurence , 'wasUpper': started with uppercase letter } }

    internalDict = {}

    def __str__(self):
        outStr = '';
        for word in self.internalDict:
            outStr += word + ': ' + str(self.internalDict[word]) + '\n'
        return outStr

    def checkInvariants(self):
        pass

    COUNT = 'count'
    LAST_DATE = 'lastDate'
    FIRST_DATE = 'firstDate'
    WAS_UPPER = 'wasUpper'


    #############################################
    #Constructors (and updaters)
    #############################################

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

    #For every input that is not None, replace the specified word's value with that value
    def updateWord(self, word, count, lastDate, firstDate, wasUpper):
        if word not in self.internalDict:
            raise Exception(word + ' does not exist.')
        if count != None:
            self.setCount(word, count)
        if lastDate != None:
            self.setLastDate(word, lastDate)
        if firstDate != None:
            self.setFirstDate(word, firstDate)
        if wasUpper != None:
            self.setWasUpper(word, wasUpper)

    #check if a word exists in the dictionary
    def exists(self, word):
        try:
            self.internalDict[word]
            return True
        except:
            return False

    #############################################
    #Public getters
    #############################################

    def get(self, word):
        if not self.exists(word):
            return False
        return self.internalDict[word]

    #returns None if not added successfully
    def getCount(self, word):
        if self.exists(word):
            return self.internalDict[word][self.COUNT]
        else:
            raise Exception(word + ' does not exist.')

    def getFirstDate(self, word):
        if self.exists(word):
            return self.internalDict[word][self.FIRST_DATE]
        else:
            raise Exception(word + ' does not exist.')

    def getLastDate(self, word):
        if self.exists(word):
            return self.internalDict[word][self.LAST_DATE]
        else:
            raise Exception(word + ' does not exist.')

    def incrementCount(self, word):
        if not self.exists(word):
            raise Exception(word + ' does not exist.')
        self.internalDict[word][self.COUNT] = self.internalDict[word][self.COUNT] + 1
        return True

    def getSortedDictByCount(self):
        return sorted(self.internalDict.items(), key=lambda x: x[1][self.COUNT])

    #############################################
    #Private setters
    #############################################

    def setCount(self, word, newCount):
        if newCount is not int:
            raise Exception('Count must be set to an integer')
        if self.exists(word):
            self.internalDict[word][self.COUNT] = newCount
        else:
            raise Exception(word + ' does not exist.')

    def setLastDate(self, word, newDate):
        if newDate is not datetime.datetime:
            raise Exception('Last date must be set to a datetime.datetime')
        if self.exists(word):
            self.internalDict[word][self.LAST_DATE] = newDate
        else:
            raise Exception(word + ' does not exist.')

    def setFirstDate(self, word, newDate):
        if newDate is not datetime.datetime:
            raise Exception('First date must be set to a datetime.datetime')
        if self.exists(word):
            self.internalDict[word][self.FIRST_DATE] = newDate
        else:
            raise Exception(word + ' does not exist.')

    def setWasUpper(self, word, wasUpper):
        if newDate is not bool:
            raise Exception('Was upper must be set to a boolean')
        if self.exists(word):
            self.internalDict[word][self.WAS_UPPER] = wasUpper
        else:
            raise Exception(word + ' does not exist.')    

 

