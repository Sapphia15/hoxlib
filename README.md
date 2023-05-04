# Hoxlib Documentation

## Functions:

### flatten(x,y,z,w,width,height,length,trength):
*x* integer
*y* integer
*z* integer
*w* integer
*width* integer
*height* integer
*length* integer
*trength* integer
Returns an integer representing the input coordinates as a position in a context with the specified dimensions. This mapping can be inverted with the unflatten or unflattenQA functions.

### flatten(x,y,z,w,width,height,length,trength):

* `x` integer
* `y` integer
* `z` integer
* `w` integer
* `width` integer
* `height` integer
* `length` integer
* `trength` integer

Flattens a 4D coordinate to a 1D index.

---

### flattenCA(p,width,height,length,trength):

* `p` list of integers
* `width` integer
* `height` integer
* `length` integer
* `trength` integer

Flattens a coordinate array to a 1D index using the `flatten` function.

---

### unflatten(i,width,height,length,trength):

* `i` integer
* `width` integer
* `height` integer
* `length` integer
* `trength` integer

Unflattens a 1D index to a dictionary of 4D coordinates.

---

### unflattenCA(i,width,height,length,trength):

* `i` integer
* `width` integer
* `height` integer
* `length` integer
* `trength` integer

Unflattens a 1D index to a coordinate array using the `unflatten` function.

---

### writeInt(i,barray):

* `i` integer
* `barray` list of bytes

Writes an integer to a byte array.

---

### hash(color):

* `color` list of integers

Hashes a color to a value between 0 and 63.

---

### getMaxFileSize(width,height,length,trength,channels=4):

* `width` integer
* `height` integer
* `length` integer
* `trength` integer
* `channels` integer

Calculates the maximum file size for a hoxel model in bytes.

---

### compColor(c1,c2):

* `c1` list of integers
* `c2` list of integers

Compares two colors for equality.

---

### saveModelQOH(model,path,verbose=False):

* `model` dictionary
* `path` string
* `verbose` boolean (optional)

Saves a hoxel model to a binary file in the QOH format.

---

### loadHoxelModel(path):

* `path` string

Loads a hoxel model from a binary file in the QOH format.

---

### saveModelHOX(model,path):

* `model` dictionary
* `path` string

Saves a hoxel model to a text file in the HOX format.

---

### loadHoxelModelData(path):

* `path` string

Loads a dictionary with data about a hoxel model from a binary file in the QOH format or a text file in the HOX format.