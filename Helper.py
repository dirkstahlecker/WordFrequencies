import re
from datetime import datetime
import locale

class Helper:
    @staticmethod
    def daysAsPrettyLength(numDays):
        years = numDays / 365
        months = (numDays - years *  365) / 12
        days = (numDays - years *  365) % 30
        return str(years) + ' years, ' + str(months) + ' months, ' + str(days) + ' days'

    @staticmethod
    def cleanWord(word):
        word = word.strip().lstrip().lower();
        regex = re.compile('([\w|-|\']*)')
        match = regex.match(word)
        word = match.group(0)
        return word

    @staticmethod
    def makeDateObject(dateStr):
        split1 = dateStr.find('-')
        split2 = dateStr.find('-',split1)
        split2 = split2 + split1 + 1

        month = int(dateStr[:split1])
        day = int(dateStr[split1+1:split2])
        year = int(dateStr[split2+1:])
        #convert year into four digits
        if year < 1000:
            year = year + 2000

        return datetime(year=year, month=month, day=day)

    @staticmethod
    def valid(word):
        illegalCharacters = ['\\','{','}'] #characters that a word can't start with
        if len(word) == 0:
            return False;
        if word[0] in illegalCharacters:
            return False
        return True

    #Put date into a format that can be recognized by datetime
    @staticmethod
    def formatDateStringIntoCleanedString(dateStr):
        date = dateStr.strip().lstrip();

        #currently assume they're fairly correctly formatted
        #won't get in here in the first place if they're not
        if re.search('^[0-9]-', date):
            date = '0' + date
        if re.search('-[0-9]-', date):
            date = date[:3] + '0' + date[3:]
        return date

    @staticmethod
    def prettyPrintDate(date):
        return date.strftime('%m-%d-%Y')

