import re
from datetime import datetime

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
        # print dateStr
        split1 = dateStr.find('-')
        split2 = dateStr.find('-',split1)
        split2 = split2 + split1 + 1

        month = int(dateStr[:split1])
        day = int(dateStr[split1+1:split2])
        year = int(dateStr[split2+1:])
        # print 'year: ',
        # print year
        # print 'month: ',
        # print month
        # print 'day: ',
        # print day

        return datetime(year=year, month=month, day=day)

    #returns date1 - date2 in date format
    @staticmethod
    def subtractDates(date1, date2): 
        # print 'date1: ',
        # print date1
        # print 'date2: ',
        # print date2
        # print type(date1)
        # print type(date2)
        diff = date1 - date2
        return diff

    @staticmethod
    def compareDates(date1, date2):
        #TODO: last can be None
        if date2 == None:
            return 1

        #TODO: this method is unnecessary once all dates are datetime objects
        if date1 > date2:
            return 1
        elif date1 < date2:
            return -1
        return 0

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

