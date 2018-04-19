class DateValue(object):

    def __init__(self,date,value):
        self.date = date
        self.value = value

    def getDate(self):
        return self.date

    def getValue(self):
        return self.value

    def __str__(self):
        return "Date : %s , Value : %s" % (self.date, self.value)
