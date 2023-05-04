# Hoxlib Documentation

## Functions:

### flatten(x, y, z, w, width, height, length, trength):

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

### flattenCA(p, width, height, length, trength):

* `p` `point [x, y, z, w]` (list of integers)
* `width` integer
* `height` integer
* `length` integer
* `trength` integer

Flattens a 4D coordinate array to a 1D index using the `flatten` function.

---

### unflatten(i, width, height, length, trength):

* `i` integer
* `width` integer
* `height` integer
* `length` integer
* `trength` integer

Unflattens a 1D index to a point dictionary.

---

### unflattenCA(i, width, height, length, trength):

* `i` integer
* `width` integer
* `height` integer
* `length` integer
* `trength` integer

Unflattens a 1D index to a coordinate array using the `unflatten` function.

---

### writeInt(i, barray):

* `i` integer
* `barray` list of bytes

Writes an integer to a byte array.

---

### hash(color):

* `color` `color [r, g, b, a]` (list of integers)

Hashes a color to a value between 0 and 63.

---

### getMaxFileSize(width, height, length, trength, channels=4):

* `width` integer
* `height` integer
* `length` integer
* `trength` integer
* `channels` integer

Calculates the maximum file size for a hoxel model encoded with QOH in bytes.

---

### compColor(c1, c2):

* `c1` `color [r, g, b, a]` (list of integers)
* `c2` `color [r, g, b, a]` (list of integers)

Compares two colors for equality.

---

### saveModelQOH(model, path, verbose=False):

* `model` model dictionary
* `path` string
* `verbose` boolean (optional)

Saves a hoxel model in the QOH format.

---

### loadHoxelModel(path):

* `path` string

Loads a model dictionary from a QOH or HOX file.

---

### saveModelHOX(model, path):

* `model` model dictionary
* `path` string

Saves a hoxel model in the HOX format.

---

### loadHoxelModelData(path):

* `path` string

Loads a HOX dictionary or a QOH dictionary with data about a hoxel model from a file in the QOH or HOX format.

---

##Dictionary Types

###point
* `x` integer
* `y` integer
* `z` integer
* `w` integer

---

###model:
* `col` list of `color [r, g, b, a]` (list of integers)
* `width` integer
* `height` integer
* `length` integer
* `trength` integer
---

### HOX
*extends model*
* `data` json data dictionary
* `matColor` list of `color [r, g, b, a]` (list of integers)
* `col` list of `color [r, g, b, a]` (list of integers)
* `mat` list of integers
* `width` integer
* `height` integer
* `length` integer
* `trength` integer

---

###QOH
*extends model*
* `channels` integer
* `col` list of `color [r, g, b, a]` (list of integers)
* `width` integer
* `height` integer
* `length` integer
* `trength` integer

---