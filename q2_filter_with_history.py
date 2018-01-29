#Simran Rahi 260604408
#!/usr/bin/python

#INPUT FORMAT: undo #moves active image backwards by one step in history
#INPUT FORMAT: redo #moves active image forwards by one step in history
#INPUT FORMAT: load image_name  #discards any history #new active image
#INPUT FORMAT: filter_width(W), filter_weights  #applies filter to previously active image, makes the result the new active image 

#DONT FORGET TO CHECK EDGES

import sys
import ctypes
import pickle

fastLib=ctypes.cdll.LoadLibrary('libfast_filter.so')

#This distincation is important for when we load a new image and want to completely rewrite the history.pickle
def firstaddToPickle(BMPfile):
    to_pickle=open("history.pickle","w")
    pic=open(BMPfile,"r")
    stringpic=pic.read()
    pickle.dump(stringpic, to_pickle)
    pickle.dump(0, to_pickle)
    to_pickle.close()

def addToPickle(BMPstring):
    to_pickle=open("history.pickle","ab")
    pickle.dump(BMPstring, to_pickle)
    to_pickle.close()

#check if it works for 2 images
def pickleToList():
    picklelist=[]
    from_pickle=open("history.pickle","r")
    while(1):
        try:
            picklelist.append(pickle.load(from_pickle))
        except (EOFError):
            break
    from_pickle.close()
    return picklelist

def Result(inputlist, counter):
    #We receive a python list with our pickle data
    #The last element is the active site counter (int) that we use to index the correct active site
    resultString=inputlist[counter]
    with open("result.bmp","wb") as f:
        f.write(resultString)

def load(BMPfile):
    firstaddToPickle(BMPfile)
    imglist=[]
    imglist=pickleToList()
    Result(imglist,0)

def undo():
    #First, we transfer the pickle data to the list
    imglist=[]
    imglist=pickleToList()
    #opens .pickle
    to_pickle=open("history.pickle","wb")
    #We want to access the last element of the list which tells us where our active site is
    counter=imglist[-1]
    if counter==0:
	print "Not possible: at the beginning of history."
	return
    imglist.pop()
    #When we undo, we need to decrease the active site by 1
    counter=counter-1
    #Now the result.bmp will be made using the new active site
    Result(imglist, counter)
    #We must put the imglist data back into the file data; dump elements of imglist and then the counter
    for ind in range(0, len(imglist)):
        pickle.dump(imglist[ind], to_pickle)
    pickle.dump(counter, to_pickle)
    
    #closes .pickle file
    to_pickle.close()
    
def redo():
    #First, we transfer the pickle data to the list
    imglist=[]
    imglist=pickleToList()
    #opens .pickle
    to_pickle=open("history.pickle","wb")
    #We want to access the last element of the list which tells us where our active site is
    counter=imglist[-1]
    if counter >= len(imglist)-2:
	print "Not possible: at the end of history."
	return
    imglist.pop()
    #When we undo, we need to increase the active site by 1
    counter=counter+1
    #Now the result.bmp will be made using the new active site
    Result(imglist, counter)
    #We must put the imglist data back into the file data; dump elements of imglist and then the counter
    for ind in range(0, len(imglist)):
        pickle.dump(imglist[ind], to_pickle)
    pickle.dump(counter, to_pickle)
    
    #closes .pickle file
    to_pickle.close()

def filter(width, weights):
    #Puts pickle info into a list of strings
    imglist=[]
    imglist=pickleToList()
    #opens .pickle
    to_pickle=open("history.pickle","wb")
    #Gets result.bmp info into a string
    result=open("result.bmp",'r')
    resultString=result.read()
    length=len(imglist)
    counter=int(imglist[-1])
    
    #Now I pass the string from this element to our filtering protocol...
    #CARG1: This opens the original bmp file and reads it's contents into a list
    Carg1=resultString

    #CARG2: Declared to be the filter weights we get as floating point numbers
    CFloatArrayType=ctypes.c_float * len(weights)
    Carg2=CFloatArrayType( *weights)

    #CARG3: The third argument is the integer width of the filter
    Carg3=width

    #CARG4: Declared as an empty list (for the modified img contents to be put into)
    Carg4=' ' * len(resultString)

    #WE CALL THE C FUNCTION
    #INPUT FORMAT: in_img_data, filter_weights, filter_width, out_img_data
    fastLib.doFiltering(Carg1,Carg2,Carg3,Carg4)
    
    if(counter==length-2):
        imglist.pop()
        imglist.append(Carg4) 
        for ind in range(0, length):
            pickle.dump(imglist[ind], to_pickle)
        pickle.dump(counter+1, to_pickle)
        Result(imglist, counter+1)
    
    if(counter<length-2):
        updatedList=[]
        for ind in range(0, counter+1):
            updatedList.append(imglist[ind])
        updatedList.append(Carg4)
        for ind in range(0, len(updatedList)):
            pickle.dump(updatedList[ind], to_pickle)
        pickle.dump(counter+1, to_pickle)
        Result(updatedList, counter+1)
    
    #closes.pickle
    to_pickle.close()

if(sys.argv[1]=="load"):
    load(sys.argv[2])
    
if(sys.argv[1]=="undo"):
    undo()

if(sys.argv[1]=="redo"):
    redo()

if(sys.argv[1]=="filter"):
    width=int(sys.argv[2])
    for num in range(3, len(sys.argv)):
        sys.argv[num]=float(sys.argv[num])
    weights=sys.argv[3:]
    filter(width, weights)






