from .chart import Chart
from .datevalue import DateValue

class DateTimeChart(Chart):
    values = []
    def __init__(self, name,color, values):
        Chart.__init__(self,name,color)
        for value in values:
            self.values.append(DateValue(value["date"],value["value"]))


    def getAllValue(self):
        return  self.values


    def plot(self):
        import matplotlib.pyplot as plt
        from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
        import datetime as dt

        dates =[dt.datetime.strptime(value.date,'%Y-%m-%d').date() for value in self.values]
        opens=[value.value for value in self.values]
        # dates = [q[0] for q in quotes]
        # opens = [q[1] for q in quotes]

        fig, ax = plt.subplots()
        ax.plot_date(dates, opens, '-')

        years = YearLocator()   # every year
        months = MonthLocator()  # every month
        yearsFmt = DateFormatter('%Y')

        # format the ticks
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.xaxis.set_minor_locator(months)
        ax.autoscale_view()


        # format the coords message box
        def price(x):
            return '$%1.2f' % x
        ax.fmt_xdata = DateFormatter('%Y-%m-%d')
        ax.fmt_ydata = price
        ax.grid(True)

        fig.autofmt_xdate()
        fig.savefig("datetimevalue.png")
        # plt.show()

