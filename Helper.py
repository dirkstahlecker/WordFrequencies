import re

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
    def splitDate(date):
        split1 = date.find('-')
        split2 = date.find('-',split1)
        split2 = split2 + split1 + 1
        return (int(date[:split1]), int(date[split1+1:split2]), int(date[split2+1:]))

    #returns date1 - date2 in date format
    def subtractDates(date1, date2): 
        split1 = Helper.splitDate(date1)
        date1 = datetime(year=split1[2], day=split1[1], month=split1[0])

        split2 = Helper.splitDate(date2)
        date2 = datetime(year=split2[2], day=split2[1], month=split2[0])

        diff = date1 - date2
        return diff