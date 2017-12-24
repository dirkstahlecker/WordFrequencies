import re

#Used to represent a single word. This is a full class so markup words can be handled the same way as
#regular words without disrupting the logic. Overriding the toString and comparison methods allow this 
#operation to work

#display name is purely for display and can be different for the same person. First and last name are internal,
#and are utilized for determining if two people are the same
class WordClass:
    rawWord = None
    displayName = None
    firstName = None
    lastName = None

    MARK_UNDER_START = '[!!'
    MARK_UNDER_END = '!!]'
    MARK_UNDER_DELIMITER = '|'
    MARK_UNDER_FIRSTLAST_DELIMITER = '_'

    @staticmethod
    def addWordOrMarkup(inp_wordOrMarkup):
        return WordClass(inp_wordOrMarkup)

    def addNameWithMarkupPieces(displayName, firstName, lastName):
        return WordClass(WordClass.buildMarkupString(displayName, firstName, lastName))

    @staticmethod
    def buildMarkupString(displayName, firstName, lastName):
        markupStr = WordClass.MARK_UNDER_START + displayName + WordClass.MARK_UNDER_DELIMITER + firstName
        markupStr += WordClass.MARK_UNDER_FIRSTLAST_DELIMITER + lastName + WordClass.MARK_UNDER_END
        return markupStr;

    def __init__(self, inp_markup):
        self.rawWord = inp_markup
        markupName = re.compile('^\[!!([^|]+)\|([^_]+)_([^!]+)!!\]$').search(self.rawWord)
        if markupName != None:
            self.displayName = markupName.group(1)
            self.firstName = markupName.group(2)
            self.lastName = markupName.group(3)

    def __str__(self):
        return self.toString()

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if type(other) is not WordClass:
            return False
        return self.firstName == other.firstName and self.lastName == other.lastName

    def toString(self):
        if self.displayName != None:
            return self.displayName
        return self.rawWord

    def strip(self):
        return self.toString().strip()

    def endswith(self, arg):
        return self.toString().endswith(arg)

    def printMarkup(self):
        if self.displayName == None:
            return self.toString()
        return WordClass.buildMarkupString(self.displayName, self.firstName, self.lastName)


