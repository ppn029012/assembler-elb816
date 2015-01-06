from orgsegclass import orgclass
'''
Name: toHexFile(orgseg orgseg, file myfile)
Description: write an org segment instanse to hex file
Arguments: orgseg: an instance of org class, contain the data, start address,end
           myfile: the file pointer point to the file you want to write
Output: 1 success
        0 empty input data
        -1 fail
'''

def toHexFile(orgseg,myfile):#orgseg is a instance of org class
    if orgseg.data==[] and orgseg.end != 1: #if input an empty line but is not the end then return 0 and do nothing
	return 0

    n=0                 #the number of data
    m=0                 #once write a line already, increase m
    sum=0               #the sum of the input data
    string=''           #store data in hex mode without 0x

    for data in orgseg.data:           
        string=string+hex2(data)   
        sum=sum+data
        n +=1
        if n == 20:     #make sure a line can have 20 data at most
            m=m+1
            writeALine(sum,m,n,myfile,string,orgseg) #write a line to hex file
            #clear n,sum and string
            n=0
            sum=0
            string=''

    #when the left data is less than 20 also write a line in hex file
    m=m+1
    writeALine(sum,m,n,myfile,string,orgseg)

'''
Name: writeALine(int sum, int n, int m, file myfile,String string, orgseg orgseg)
Description: write a line in hex file according to the input arguments
Arguments: sum: the sum of data need to write in a line
           m: the number of lines that you have write in hex file currently
           n: the number of data in this line 
           myfile: the file you want to write to
           string: the string contains the data need to be write
           orgseg: an org segment instanse 
'''    

def writeALine(sum,m,n,myfile,string,orgseg):     #write a line according to the data import to myfile in intel HEX style
    hexAddr=''
    sum=findSum(sum)                   
    startAddr=20*(m-1)+orgseg.start
    if len(hex2(startAddr))<4:
        for i in range(0,4-len(hex2(startAddr))):
            hexAddr += '0'
    hexAddr += hex2(startAddr)
    string=':'+hex2(n)+hexAddr+'00'+string+sum+'\n'
    myfile.write(string)
    if orgseg.end == 1:             #the data is finished
        string=':00000001FF'
        myfile.write(string)

'''
Name: findSum(int sum)
Description: find the twos complement of sum
Arguments: sum: the sum of data need to write in a line
'''         
def findSum(sum):
    #if the sum is too big, only choose the last two bytes
    if len(hex(sum)) == 3:                  #the sum in hex is something like 0x3
      sum=hex(sum)[-1]
    else:                                   #the sum in hex is bigger and is something like 0x22
      sum=hex(sum)[-2]+hex(sum)[-1]
    sum=int(sum,16)
    sum=255-sum
    sum=hex2(sum)
    return sum
    
'''
Name: hex2(int sum)
Description: change the integer to octal number but do not have 0x before them
Arguments: num: the integer number need to translate
''' 
def hex2(num):                      
    num=hex(num)
    if len(num)==3:
        num=num.replace('0x','0')
    else:
        num=num.replace('0x','')
    return num



if __name__=='__main__': toHexFile(['5','10','4'],'0000')

    
        
