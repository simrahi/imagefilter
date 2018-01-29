#Simran Rahi 260604408
#!/usr/bin/python

#INPUT FORMAT: input_file, output_file, width(W), [floating_point_numbers]
import sys
import ctypes

fastLib=ctypes.cdll.LoadLibrary('libfast_filter.so')

if(len(sys.argv)<5):
    print "Not enough arguments; try again."
    exit()

if(len(sys.argv[4:])!=(int(sys.argv[3])**2)):
    print "Incorrect amount of filter weights."
    exit()

#CARG1: This opens the original bmp file and reads it's contents into a list
oldpicture=open(sys.argv[1],'r')
stringOld=oldpicture.read()
charstar=(ctypes.c_ubyte * (len(stringOld)))
Carg1=charstar.from_buffer_copy(stringOld)

#CARG2: Declared to be the filter weights we get as floating point numbers
for num in range(4, len(sys.argv)):
    sys.argv[num]=float(sys.argv[num])
pyWeights=sys.argv[4:]
CFloatArrayType=ctypes.c_float * len(pyWeights)
Carg2=CFloatArrayType( *pyWeights)

#CARG3: The third argument is the integer width of the filter
w=int(sys.argv[3])
Carg3=w

#CARG4: Declared as an empty list (for the modified img contents to be put into)
stringNew=' ' * len(stringOld)
charstartwo=(ctypes.c_ubyte * (len(stringOld)))
Carg4=charstartwo.from_buffer_copy(stringNew)


#WE CALL THE C FUNCTION
#INPUT FORMAT: in_img_data, filter_weights, filter_width, out_img_data
fastLib.doFiltering(Carg1,Carg2,Carg3,Carg4)

#Here, I put the contents of the Carg4 list back into the bmp file
with open(sys.argv[2],"wb") as f:
    f.write(Carg4)

