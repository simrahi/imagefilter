#!/usr/bin/python
import sys
import pickle
import cgitb; cgitb.enable()
import cgi
import ctypes
import copy

fastLib=ctypes.cdll.LoadLibrary('./libfast_filter.so')

def firstaddToPickle(BMPcontents):
    to_pickle=open("history.pickle","w")
    pickle.dump(BMPcontents, to_pickle)
    pickle.dump(0, to_pickle)
    to_pickle.close()

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

def load(BMPcontents): #just string x.bmp
    firstaddToPickle(BMPcontents)
    imglist=[]
    imglist=pickleToList()
    Result(imglist,0)

def undo():
    #First, we transfer the pickle data to the list
    imglist=[]
    imglist=copy.deepcopy(pickleToList())
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
    imglist=copy.deepcopy(pickleToList())
    #opens .pickle
    to_pickle=open("history.pickle","wb")
    #We want to access the last element of the list which tells us where our active site is
    counter=imglist[-1]
    if counter>=len(imglist)-2:
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
        #print "counter equals length-2"
        imglist.pop()
        imglist.append(Carg4)
        #print "after appending Carg4, length is %i"%len(imglist)  
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

print "Content-type: text/html\n"  # note HTTP transactions start with this!
form = cgi.FieldStorage()	# parse query

if form.has_key('photo'):
    img_in = form['photo'].value
else:
    img_in = open('result.bmp', 'rb')

#Gathering info from the form for our filter call
blur_weight = [float(form['00'].value), float(form['01'].value), float(form['02'].value), float(form['10'].value), float(form['11'].value), float(form['12'].value), float(form['20'].value), float(form['21'].value), float(form['22'].value)]

if form['p'].value == "Load":
    load(img_in)   
    print "Loaded successfully."

if form['p'].value == "Filter":
    filter(3, blur_weight)
    print "Filter applied."

if form['p'].value == "Undo":
    undo()

if form['p'].value == "Redo":
    redo()
    
print """<html>
<body>
<form name="input" action="./q3_cgi_filter.py" method="post" enctype="multipart/form-data">
  <p>Photo to Upload: <input type="file" name="photo" /></p>
  <p>Next Filter:</p>
  <p><input type="text" name="00" value="%f"> <input type="text" name="01" value="%f"> <input type="text" name="02" value="%f"> </p>
  <p><input type="text" name="10" value="%f"> <input type="text" name="11" value="%f"> <input type="text" name="12" value="%f"> </p>
  <p><input type="text" name="20" value="%f"> <input type="text" name="21" value="%f"> <input type="text" name="22" value="%f"> </p> 
  <input type="submit" value="Load" name="p">
  <input type="submit" value="Filter" name="p">
  <input type="submit" value="Undo" name="p">
  <input type="submit" value="Redo" name="p">

</form>

<hl>

<img src="result.bmp"/>
</body>
</html>""" % (blur_weight[0], blur_weight[1],blur_weight[2],blur_weight[3],blur_weight[4],blur_weight[5],blur_weight[6],blur_weight[7],blur_weight[8])

