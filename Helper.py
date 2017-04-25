class Helper:
    @staticmethod
    def daysAsPrettyLength(numDays):
        years = numDays / 365
        months = (numDays - years *  365) / 12
        days = (numDays - years *  365) % 30
        return str(years) + ' years, ' + str(months) + ' months, ' + str(days) + ' days'

    