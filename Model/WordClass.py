import re

#Used to represent a single word. This is a full class so markup words can be handled the same way as
#regular words without disrupting the logic. Overriding the toString and comparison methods allow this 
#operation to work
class WordClass:
    rawWord = None
    firstName = None
    lastName = None

    def __init__(self, inp_word):
        self.rawWord = inp_word
        markupName = re.compile('^\[!!([^|]+)\|([^!]+)!!\]$').search(self.rawWord)
        if markupName != None:
            self.firstName = markupName.group(1)
            self.lastName = markupName.group(2)

    def __str__(self):
        if self.firstName != None:
            return self.firstName
        else:
            return self.rawWord

    #TODO: make this case insensitive?
    def __eq__(self, other):
        if self.firstName != None:
            return self.firstName == other #TODO: look at this again
        else:
            return self.rawWord == other

    def toString(self):
        if self.firstName != None:
            return self.firstName
        return self.rawWord

    def strip(self):
        return self.toString().strip()

    def endswith(self, arg):
        return self.toString().endswith(arg)