import numpy as np
import os
dims=(2,4,5,10)
blockdata = np.zeros( shape=dims, dtype='uint8' )
blockdata[0][0][0][0]=1
blockdata[0][0][1][0]=1
blockdata[0][0][2][0]=1
blockdata[0][0][3][0]=1
blockdata[0][0][4][0]=1

#print(blockdata)
blockdata.resize((np.prod(dims),))
#print(blockdata)
i=10
b=i.to_bytes(2,"big")
print(b)