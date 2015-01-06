import re

"""
includes 
1. getInsLength(string), it will caculate the digit length of instruction
   arguments: standard INSTRUCTION in mnenomic list

2. resolveIns(string), it will resovle the statements into standard instructions in OPCODE list
   Return:[INS, OPCODE, OPERANDS, DATA]
            'INS': standard instruction 
            'OPCODE': 8 bytes ASCII code of binary OPCODE like '00001000'
            'OPERANDS' (list):  1,2 or 3 operands in statement, it includes register, DATA, LABEL, or unsolved SYNTAX
            'DATA'(list): it includes all OPERANDS except the RESERVED register and words

3. getInsFromLine(test)  Resolve a line into [LABEL, STATEMENT, COMMENT]

"""
def getInsLength(line):
  opLength = 0 #initialise

  #find the lowercase words in opcodelist to determine the length of words
  #write a regular expression to find lowercase

  dataExpress = re.search(r""" #?[a-z_0-9]+""", line)
  if dataExpress:
    dataEnd = re.search(r""" #?[a-z_0-9]+""", line).end()
    if '16' in dataExpress.group():
      opLength = 3
    elif re.search(r""" #?[a-z_0-9]+""", line[dataEnd:]):
      opLength = 3
    else:
      opLength = 2
  else:
    opLength = 1

  return opLength



#get Operands(determine whether it is a (data or label))
#transform the instructions to the standard instruction in  'OPCODE' list
#it may provide the exactly code 
def resolveIns(string):
  try:
    # rlist is the file storing 'Register name'
    # The name will be DATA or LABEL except the name of register 
    infile = open("rlist", "r")   
  except:
    print "I/O exception"

  rlist = []
  for line in infile:

    rlist.append(line.strip())

  ins = getInsFromLine(string)

  # ins[0] is label  
  # ins[1] is instruction  
  # ins[2] is comment


  # find mnemonic, operands, datas
  if re.search(r"""\b\w*\b""",ins[1]):
    mnemonic = re.search(r"""\b\w*\b""",ins[1]).group()
    mnemonic_end = re.search(r"""\b\w*\b""",ins[1]).end()
  else:
    raise Exception('Not found mnemonic')
    
  operand_end = 0
  operands =[]

  operands = ins[1][mnemonic_end:].split(',')

  datas = []
  i = 0
  newIns = mnemonic
  for operand in operands:
    operand = operand.strip()
    if operand not in rlist:

      # find the label or data in operands

      #@addr16 mode
      if '@' in operand:
        data = operand[1:]
        datas.append(data)
        operands[i] = '@addr16'
      elif '#' in operand:
        data = operand[1:]

        #determine the digit of data
        decimal = analyseData(data,[])
        datas.append(data)
        if decimal[1] ==2:
          operands[i] = '#data16'
        else:
          operands[i] = '#data8'
      #some address 
      else:
        datas.append(operands[i][:])
        if 'P' == mnemonic[0]:
          operands[i] = 'addr11'
        elif 'J' in mnemonic:
          operands[i] = 'rel8'
        else:
          operands[i] = 'port_addr'
        
    newIns += ' '+operands[i].strip()+','
    i+=1

  newIns = newIns[:-1]
  
  #print 'OPERANDS: ',operands, '   DATA:', datas, '   newIns:', newIns.strip()
  
  infile.close()
  infile = open('opcode.txt','r')

  line = infile.readline()
  while line:
    myInsre=re.search(r'^.*(?=\d{8})',line)
    if myInsre:
      if myInsre.group().strip() in newIns.strip():
        return {'OPERANDS': operands, 'DATA': datas, 'INS': newIns.strip(),'OPCODE':line[myInsre.end():]}
    line = infile.readline()
    
  return {'OPERANDS': operands, 'DATA': datas, 'INS': newIns.strip(),'OPCODE':'0'}




#get LABEL , STATEMENT,  COMMENT from a line
def getInsFromLine(test):
  label=re.compile('^.*(?=:)')
  comment=re.compile(r'(?<!, #)(?<=#).*')
  content0=re.compile('(?<=:).* (?=#)')# have label in line
  content1=re.compile('^.* (?=#)')# do not have label in line
  content2=re.compile('(?<=:).*')# do not have comment in line

  test=test.strip()

  a=re.search(label,test)
  b=re.search(comment,test)
  c0=re.search(content0,test)
  c1=re.search(content1,test)
  c2=re.search(content2,test)
  #initialise 
  label = ""
  comment = ""
  content = ""
  #use if else to cope with different cases
  if a==None:       #do not have label in line
      label = ""
      if b == None: #do not have comment in line
          comment = ""
          content = test
      else:         #have comment in line
          comment = b.group()
          content = c1.group()
  else:             #have label
      label= a.group()
      if b==None:   #do not have comment
        comment = ""
        content= c2.group()
      else:         #have comment 
        comment= b.group()
        content= c0.group()

  return [label.strip(), content.strip(), comment.strip()]






"""
Name: analyseData
Description: Change all kind of data, such as 23h,01010101b,123h+0x3*2 or label to standard hexdecimal data without 0x in front

"""

def analyseData(data,symtable):
    try:
        length = 0
        realdata=symtable[data]
        return [realdata,2]
    except:                         #if symtable do not contain data, it will rasie an exception
        b = re.compile('.*(?=[\+\-\*\/])')
        """
        the following code is used to divide data to symbol and number
        for example 0x+2-3h would be '0x' '+' '2' '-' '3h'
        """
        number={}   #the diary used to store numbers
        sym={}      #the symbol used to store symbols
        i=0
        finalLen = 0
        frontData = re.search(b,data)
        while frontData != None:         #front data contain +-*/
            sym[i] = data[len(frontData.group())]
            number[i] = data[len(frontData.group())+1:]
            i += 1
            data=frontData.group()
            frontData = re.search(b,data)
        number[i] = data.lower()                               #the first number
        """
        the following code is used to change the different type number in number diary
        to standard decimal number, for example 0x10 to 16
        """
        for j in number:
            if number[j].strip() in symtable:
                length = 2
                number[j] = symtable[number[j]]
            if number[j].strip() == '':
                raise DataNullException #this data is null, raise DataNullException
            a = re.compile('(?<=0x).*')
            temp = re.search(a,number[j])
            if temp != None:        #this number is something like 0x23
                number[j] = int(temp.group(),16)
                length=len(temp.group())/2
            else:
                a = re.compile('^.*(?=h)')
                temp = re.search(a,number[j])
                if temp != None:        #this number is something like 44h
                    number[j] = int(temp.group(),16)
                    length=len(temp.group())/2
                else:
                    a = re.compile('^.*(?=b)')
                    temp = re.search(a,number[j])
                    if temp != None:        #this number is something like 00000001b
                        number[j] = int(temp.group(),2)
                        if len(temp.group()) > 16:
                            length = 2
                    else:
                        a = re.compile('(?<=^o).*')
                        temp = re.search(a,number[j])
                        if temp != None:        #this number is something like o23
                            number[j] = int(temp.group(),8)
                            if int(number[j]) > 255:
                                length=2
                            else:
                                length=1
                        else:                   #this number is decimal number
                            if int(number[j]) > 255:
                                length=2
                            else:
                                length=1
            if length == 2:                     #once a data is 2 byte, the whole equation need 2 byte
                finalLen = 2
        """
        Combine number diary and symbol diary to caculate the final data
        """
        equation = ''
        for i in xrange(len(sym)-1,-1,-1):
            equation += str(number[i+1])+sym[i]         #combine the number and symbol except the last number

        a=re.compile('^0*')
        b=re.search(a,str(number[0]))
        equation += str(number[0])[len(b.group()):]                     #add last number to the equation

        if finalLen != 2:
            finalLen = length
        return [eval(equation),finalLen]
        
                        
class DataNullException(Exception):pass
        

        
