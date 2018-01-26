import sys
import datetime
import pytz
import re

class CSVParser(object):

    #Initalize Function, need storage from CSV and delimiter value
    def __init__(self):
        self.data = []
        self.delimiter = ','

    # ReadFile: Reads in the file and puts it in the data list.
    def ReadFile(self):
        try:
           # Need to detach stdin to decode in utf-8
           sys.stdin = sys.stdin.detach()   
           for line in sys.stdin:
               line = line.decode("utf-8", "surrogateescape")
               # Regex will look at each comma
               # if it's surrounded by ", will not split on that comma
               self.data.append(re.split(',(?=(?:[^"]*\"[^"]*\")*[^"]*$)',line))
        except:
            # Extra validation, stdin/out already verifies this
            sys.stderr.write('Invalid Filename, Please Try Again')

    # Create a CSV from the list provided, in utf-8
    # If there an invalid character, escape/write it in unicode.
    def WriteFile(self):
        for line in self.data:
            line = ",".join(line).encode("utf-8", "surrogateescape")
            sys.stdout.buffer.write(line)

    # Imports the Time as Pacific, then converts to Eastern
    # Also changes the format, always assumes input format is m/d/y. 
    def UpdateTimestamp(self, timestamp):
        if (timestamp == 'Timestamp'):
            return timestamp
        try:
            date = datetime.datetime.strptime(timestamp, "%m/%d/%y %I:%M:%S %p")
            eastern = pytz.timezone('US/Eastern')
            pacific = pytz.timezone('US/Pacific-New')
            datept = pacific.localize(date)
            dateet = datept.astimezone(eastern)
            return dateet.strftime("%Y/%m/%d %H:%M:%S")
        except ValueError as e:
            sys.stderr.write("DateTime could not be parsed correctly")
            return ''

    # Makes sure Zip is 5 characters, if not, just add 0s to beginning. 
    def UpdateZip(self, zipcode):
        if(zipcode == 'ZIP'):
            return zipcode
        return '{:0>5}'.format(zipcode)

    # Uppercase the name
    def UpdateName(self, name):
        if (name == "Name"):
            return name
        return name.upper()

    # Switch the Miliseconds to a floating seconds
    def UpdateDuration(self, durationtime):
        return str.replace(durationtime, '.', '.0')

    # Add the two Durations together to get a total, keeping in mind overflow
    def UpdateTotalDuration(self, total, time1, time2):
        if (total == 'TotalDuration'):
            return total
        firsttime = time1.split(':')
        secondtime = time2.split(':')

        finaltime = [0,0,0.0]
        
        finaltime[2] = float(firsttime[2]) + float(secondtime[2])
        if (finaltime[2] >= 60):
            finaltime[1] + 1
            finaltime[2] - 60

        finaltime[1] += int(firsttime[1]) + int(secondtime[1])
        if (finaltime[1] >= 60):
            finaltime[0] + 1
            finaltime[1] - 60

        finaltime[0] += int(firsttime[0]) + int(secondtime[0])
        return str(finaltime[0]) + ':' + str(finaltime[1]) + ':' + str(finaltime[2])
    
    # TraverseFile: Goes through each line and edits the values that need editing
    def TraverseFile(self):
        for row in self.data:
            if (row[0] is not None):
                row[0] = self.UpdateTimestamp(row[0])
            if (row[2] is not None):
                row[2] = self.UpdateZip(row[2])
            if (row[3] is not None):
                row[3] = self.UpdateName(row[3])
            if (row[4]  is not None):
                row[4] = self.UpdateDuration(row[4])
            if (row[5] is not None):
                row[5] = self.UpdateDuration(row[5])
            if (row[6] is not None and row[5] is not None and row[4] is not None):
                row[6] = self.UpdateTotalDuration(row[6], row[5], row[4])

# Main program, Parse, Read, Traverse, Write.
def main():
    a = CSVParser()
    a.ReadFile()
    a.TraverseFile()
    a.WriteFile()

main()
