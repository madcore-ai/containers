class Chart(object):

    def __init__(self,name,color):
        self.name = name
        self.color = color

    def getName(self):
        return self.name

    def getColor(self):
        return self.color

    def __str__(self):
        return "name : %s , color : %s" % (self.name, self.color)


