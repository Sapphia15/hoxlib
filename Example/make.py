import hoxlib
width=10
height=10
length=10
trength=1000
bulk=width*height*length*trength
model={"col": [[0,0,0,0]]*bulk,"width":width,"height": height,"length": length,"trength": trength}
hoxlib.saveModelHOX(model,"overrideSize.hox")
