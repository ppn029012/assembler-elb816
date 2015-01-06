#!bin/python

class orgclass:
  #initialise
  def __init__(self, start=0, end=1):
    self.start = start
    self.end = end
    self.data = []

  #set start address for ORG Segment
  def setStart(self, start):
    self.start = start

  #get start address for ORG Segment
  def getStart(self):
    return self.start

  #set 1 if end
  def setEnd(self, end):
    self.end = end

  #get whether it ends 1 is end, else 0
  def getEnd(self):
    return end

  def addData(self, data):
    self.data.append(data)

  def getDataLen(self):
    return len(self.data)

  def getData(self, index):
    return self.data[index]
  
  def getData(self):
    return self.data
  
  #clear the orgseg for reuse
  def clear(self):
    self.data = []
    self.start = 0
    self.end = 0

