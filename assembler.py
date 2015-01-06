# Assembler program main function
#  including two main procedure: one pass, two pass assembly




# -*- coding: cp936 -*-
import re
import analyzeSrc
from orgsegclass import orgclass
import writehex
import sys


# Global variables to be used in two pass assembly
symtable={}




# determine whether it is pesudo
# 1 pesudo
# 0 real instruction
def isPesudo(line):
    pesudo_ins = [ 'ORG', 'EQU' ,'DB' , 'DS' ,'CSEG' , 'RSEG','SEGMENT' ,'PUBLIC' , 'EXTERN', 'END' ]
    for i in pesudo_ins:
      if i in line.upper():
        return 1
    return 0


# get Pesudo Type 
# return a String of pesudo instruction 
def getPesudoType(line):
    pesudo_ins = [ 'ORG', 'EQU' ,'DB' , 'DS' ,'CSEG' , 'RSEG','SEGMENT' ,'PUBLIC' , 'EXTERN', 'END' ]
    for i in pesudo_ins:
      if i in line.upper():
        return i
    return None


# Check whether Label used by user is already in the'Reserved list' or symbol table
# In order to prevent user from using 'Reserved words' to name his label to cause ambiguity
def isReserved(alabel):
  try:
    rlist=open('rlist','r')
  except:
    raise Exception('can\'t open file rlist')
  word=rlist.readline()
  while word:
    if alabel.upper() == word.strip():
      return True   
    word=rlist.readline()
  
  if alabel in symtable.keys():
    print symtable.keys()
    return True

  rlist.close()
  return False






####################                   #####################################
####################     ONE-PASS      #####################################
####################                   #####################################

#pass one: analyse the document and fill up the symtable
def pass_one(filepath):
    lc = 0              #location counter, used to get the current byte number
    lineNum = 0         #used to get the current line number
    try:
        infile=open(filepath,'r')
        
    except:
        print 'can not open',filepath
        return 0
    line=infile.readline()
    try:
        while line:    #always read a line and use lineNum to count it
          lineNum += 1
          
          #Exclude the blank line or only COMMENT line
          #Strip the COMMENT in a line
          commentBot = line.find('#')
          if commentBot!=-1:
            stripLine = line[0:commentBot]
          else:
            stripLine = line
          
          #Determine whether it is blank line
          if stripLine.strip() == "":
            line=infile.readline()
            continue

          #Cope with pesudo instructions(DB, ORG, END, EQU)
          if isPesudo(line):
            # process DB pesudo instruction: caculate the number of data behind "DB" 
            if getPesudoType(line)=="DB":
              dataInDB = line.split(',')
              dataInDB[0] = dataInDB[0][3:]
              for data in dataInDB:
                  data = ''.join(data.split())
                  dataLen = analyzeSrc.analyseData(data,symtable)[1]
                  lc += dataLen       
              line=infile.readline()
              continue

            #process ORG pesudo instruction: let location counter = address behind org
            elif getPesudoType(line)=="ORG":
          
              org_orgin = line.find("ORG")
              lc = analyzeSrc.analyseData(line[org_orgin+3:-1],{})[0]
              line=infile.readline()
              continue

            #process EQU pesudo instruction: store the label in symob table
            elif getPesudoType(line)=="EQU":
              dataEQU = line.upper().split('EQU')
              dataEQU[1] = ''.join(dataEQU[1].split())
              symtable[dataEQU[0].lower().strip()] = analyzeSrc.analyseData(dataEQU[1].strip(),{})[0] 
              line=infile.readline()
              continue

            #process END pesudo instruction, jump out the while loop
            elif getPesudoType(line)=="END":
              break

          # Process of Real  instruction
          else:
            # Get a list contain 3-SEGMENTs:[ LABEL, STATEMENT, COMMENTs]
            ins = analyzeSrc.getInsFromLine(line)

            #If there is a label, add the label to the symtable
            if ins[0]:
              if isReserved(ins[0]):    #chech whether the label is reserved word
                print '\nYou can\'t use a reserved words as a label'
                print 'LINE:\n', line
                exit()
              else:                     # label correct then put the address of the label in symtable
                symtable[ins[0]] = lc

            #Cope with the instructions no matter this line have label or not
            resolvedLine = analyzeSrc.resolveIns(line)
            lc += analyzeSrc.getInsLength(resolvedLine['INS'])
            line=infile.readline()
              
    except analyzeSrc.DataNullException:    #happened when data in set to null or other wrong form
        print 'data in',linNum+'th', 'line can not be analysed'
    print "Finish one pass" 
    pass_two(symtable, filepath)            
      





####################                   #####################################
####################     TWO-PASS      #####################################
####################                   #####################################

 
#pass two , use the symtable to get definite OPCODE and data, and write them to .hex file
def pass_two(symtable, filepath):
    try:
      infile=open(filepath,'r')
      newfilepath = filepath.split('.')[0]  
      outfile=open(newfilepath+'.hex','w')   
    except:
        print 'can not open',filepath
        return 0

    #initialize Location Counter
    lc=0
    
    #initialize ORG-class instanse
    orgseg = orgclass(0,0)


    line=infile.readline()
    while line:    #always read a line
        
      #Exclude the blank line or only COMMENT line
      #strip the COMMENT in a line
      commentBot = line.find('#')
      if commentBot!=-1:
        stripLine = line[0:commentBot]
      else:
        stripLine = line
      
      #determine whether it is blank line
      if stripLine.strip() == "":
        line=infile.readline()
        continue

      #Cope with pesudo
      if isPesudo(line):
        # process END pesudo instruction, set orgseg.end to 1 and write last line in hex file
	if getPesudoType(line)=="END":
	  orgseg.end = 1
  	  writehex.toHexFile(orgseg,outfile)
          print "Assembly success, output:", newfilepath+".hex"
          symtable.clear()
          return 1

        # process DB pesudo instruction, add the data after DB instruction to orseg.data
        if getPesudoType(line)=="DB":
          dataInDB = line.split(',')
          dataInDB[0] = dataInDB[0][3:]
          for onedata in dataInDB:
            onedata = ''.join(onedata.split())
            orgseg.addData(analyzeSrc.analyseData(onedata,symtable)[0])
          line=infile.readline()
          continue

        # process ORG pesudo instruction, write the data in orgseg to the destination.hex, clear the orgseg, set the new instanse start address
        if getPesudoType(line)=="ORG":
          writehex.toHexFile(orgseg, outfile)         
          orgseg.clear()
          org_orgin = line.find("ORG")
          start_lc = analyzeSrc.analyseData(line[org_orgin+3:-1],{})[0]
          orgseg.setStart(start_lc)
          line=infile.readline()
          continue

        # process other pesudo instruction if needed to implement in the future
        else:
          line=infile.readline()
          continue

       
          
      # Cope with real instruction
      else:
        # get OPCODE, LABEL, standard INSTRUCTION from non-standard instruction
        ins = analyzeSrc.getInsFromLine(line)
        lineInfo = analyzeSrc.resolveIns(ins[1])
        orgseg.addData(int( lineInfo['OPCODE']  , 2  ))
        orgseg.setEnd(0)
        lc += 1
        
        # change the data into standard style
        for element in lineInfo['DATA']:
          decimal = analyzeSrc.analyseData( element.strip()  ,symtable )

          # cope with the conflict between the byte number needed by the instruction and the offered instruction              
          needlength =  analyzeSrc.getInsLength(analyzeSrc.resolveIns(line)['INS'])-1
          
          if needlength ==2 and len(hex(decimal[0]))>4:
            hexstr = hex(decimal)[2:-2]
            orgseg.addData(str(int(hexstr,2)))
            orgseg.addData(    str(int(hex(decimal[0])[-2:])))
          
          #not Done yet
          orgseg.addData(decimal[0])
          lc += 1
          
        #Read next line and loop  
        line=infile.readline()
        
    #write the standard instruction and data to hex file 
    writehex.toHexFile(orgseg,outfile)
    orgseg.clear()
    #write the last line 00000001ff to hex file
    orgseg.setEnd(1)
    writehex.toHexFile(orgseg,outfile)

    
        
    
    
def main():
    print 'Useage:  python', sys.argv[0]+" example1 example2 ...\n OR input your files name in 'example1, example2, ..' "
    if len(sys.argv) != 1:       #if the user input argument to this script
        for i in range(1, len(sys.argv)):
	    
            pass_one(sys.argv[i])
    else:    
        files=raw_input('Please input the files your want to translat:').strip()
        source=files.split(',')
        for i in source:
            pass_one(i.strip())
    

if __name__=='__main__':main()
