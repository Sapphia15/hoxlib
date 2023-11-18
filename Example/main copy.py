import os
import hoxlib
from graphics import *

chunkSize = 8
chunkHeight = 128

gpath="world"

width=750
height=750

win=GraphWin("4D Miner Editor",width,height,autoflush=False)
win.setBackground("black")


AIR=0
GRASS=1
DIRT=2
STONE=3
WOOD=4
LEAVES=5
LAVA=6
IRON=7
DEADLY=8
CHEST=9
MGRASS=10
SOIL=11
MSTONE=12
MWOOD=13
MLEAVES=14

COLOR=[None]*15
COLOR[AIR]=[255,255,255]
COLOR[GRASS]=[0,255,0]
COLOR[DIRT]=[130,50,10]
COLOR[STONE]=[50,50,70]
COLOR[LEAVES]=[255,150,0]
COLOR[WOOD]=[140,100,10]
COLOR[LAVA]=[255,0,0]
COLOR[IRON]=[100,50,50]
COLOR[DEADLY]=[200,0,200]
COLOR[CHEST]=[140,60,80]
COLOR[MGRASS]=[0,50,200]
COLOR[SOIL]=[0,0,255]
COLOR[MWOOD]=[100,0,200]
COLOR[MLEAVES]=[0,150,255]

class editableChunk:

    def __init__(s):

        s.data = {}

    def setBlock(s, x, y, z, w, block):

        s.data[(x,y,z,w)] = block
    
    def toBin(s):

        d = s.data
        
        output = b""

        lastBlock = 0

        count = 0
        
        for x in range(chunkSize):
            for y in range(chunkHeight):
                for z in range(chunkSize):
                    for w in range(chunkSize):

                        coords = (x,y,z,w)
                        currentBlock = 0
                        if coords in d:
                            currentBlock = d[coords]

                        if currentBlock != lastBlock or count >= 255:

                            output = output + lastBlock.to_bytes(1, "big") + count.to_bytes(1, "big")
                            
                            lastBlock = currentBlock
                            count = 0

                        count += 1

        count -= 1
        output = output + lastBlock.to_bytes(1, "big") + count.to_bytes(1, "big")

        return output

def loadChunk(path,x,z,w):
    chunkCoords = (
                x//chunkSize,
                z//chunkSize,
                w//chunkSize
            )
    chunkStr = f"x{chunkCoords[0]}z{chunkCoords[1]}w{chunkCoords[2]}"
    chunkDir = f"{path}/chunks/{chunkStr}"
    if (os.path.exists(chunkDir)):
        with open(chunkDir,"rb") as f:
            bins=f.read()
            chunk=editableChunk()
            fcoord=0
            for i in range(len(bins)):
                block=int.from_bytes(bins[i:i+1],"big")
                count=int.from_bytes(bins[i:i+2],"big")
                if (block!=0):
                    for j in range(count):
                        p=hoxlib.unflattenCA(fcoord)
                        chunk.setBlock(p[0],p[1],p[2],p[3],block)
                        fcoord=fcoord+1
                else:
                    fcoord=fcoord+count
                i=i+1
            return chunk
def combineTopChunkOntoBottomChunk(top,bot):
    for coords in top.data:
        
        bot.setBlock(coords[0],coords[1],coords[2],coords[3],top.data[coords])
        


class editableWorld:

    def __init__(s):

        s.data = {}
    
    def getBlock(s,x,y,z,w):
        if (x,y,z,w) in s.data:
            return s.data[(x,y,z,w)]

        return 0

    def setBlock(s, x, y, z, w, block):

        s.data[(x,y,z,w)] = block

    def setPoint(s,p,block):
        s.setBlock(p.x,p.y,p.z,p.w,block)

    def fill(s, x1, y1, z1, w1, x2, y2, z2, w2, block):

        for x in range(x2 - x1 + 1):
            for y in range(y2 - y1 + 1):
                for z in range(z2 - z1 + 1):
                    for w in range(w2 - w1 + 1):

                        s.setBlock(x1 + x, y1 + y, z1 + z, w1 + w, block)

    def fillR(s, x, y, z, w, lx, ly, lz, lw, block):

        s.fill(x, y, z, w, x+lx-1, y+ly-1, z+lz-1, w+lw-1, block)
          
    def fillP(s,p1,p2,block):
        
        s.fill(p1.x,p1.y,p1.z,p1.w,p2.x,p2.y,p2.z,p2.w,block)
    
    def draw(self,line,block,iterations=-1):
        if (iterations==-1):
            iterations=round(line.length()*1.5)

        tVal=0
        for i in range(iterations+1):
            tVal=i/iterations
            self.setPoint(line.lerp(tVal).round(),block)
    
    def save(s, path):

        chunks = {}
        if not os.path.exists(f"{path}"):
                os.mkdir(f"{path}")
                os.mkdir(f"{path}/chunks")
        for coord in s.data:
        
            chunkCoords = (
                coord[0]//chunkSize,
                coord[2]//chunkSize,
                coord[3]//chunkSize
            )
            
            chunkStr = f"x{chunkCoords[0]}z{chunkCoords[1]}w{chunkCoords[2]}"

            if not (chunkStr in chunks):

                chunks[chunkStr] = editableChunk()

                chunkDir = f"{path}/chunks/{chunkStr}"
                
                if not os.path.isdir(chunkDir):

                    os.mkdir(chunkDir)
                    with open(f"{chunkDir}/entities.json", "w") as file:
                        file.write("[]")

            chunks[chunkStr].setBlock(
                coord[0] % chunkSize,
                coord[1],
                coord[2] % chunkSize,
                coord[3] % chunkSize,
                s.data[coord]
            )
        
        for chunk in chunks:
            
            binPath = f"{path}/chunks/{chunk}/blocks.bin"
            

            with open(binPath, "wb") as file:

                file.write(chunks[chunk].toBin())

class point:
    def __init__(self,x,y,z,w):
        self.x=x
        self.y=y
        self.z=z
        self.w=w
    
    def round(self):
        return point(round(self.x),round(self.y),round(self.z),round(self.w))

    def sub(self,p2):
        return point(self.x-p2.x,self.y-p2.y,self.z-p2.z,self.w-p2.w)

    def add(self,p2):
        return point(self.x+p2.x,self.y+p2.y,self.z+p2.z,self.w+p2.w)
    
    def move(self,p2):
        a=self.add(p2)
        self.x=a.x
        self.y=a.y
        self.z=a.z
        self.w=a.w

    def mag(self):
        return (self.x**2+self.y**2+self.z**2+self.w**2)**(1/2)

class line:
    
    def __init__(self,p1,p2):
        self.p1=p1
        self.p2=p2
        
    def lerp(self,t):
        return point((1-t)*self.p1.x+t*self.p2.x,(1-t)*self.p1.y+t*self.p2.y,(1-t)*self.p1.z+t*self.p2.z,(1-t)*self.p1.w+t*self.p2.w)
        
    def length(self):
        return self.p1.sub(self.p2).mag()

world=editableWorld()



bl=4
size=3
# world.draw(line(point(-10,30,-10,-10),point(10,30,-10,-10)),2)
# world.draw(line(point(-10,30,-10,-10),point(-10,30,10,-10)),2)
# world.draw(line(point(-10,30,10,-10),point(10,30,10,-10)),2)
# world.draw(line(point(10,30,10,-10),point(10,30,-10,-10)),2)
# world.draw(line(point(10,30,10,-10),point(-10,30,-10,-10)),2)

sm=1
lg=6
tileSize=(width-lg*6-sm*20)/25

class camera:
    def __init__(self,pos,wrld):
        self.pos=pos
        self.w=wrld
        self.elements=[]

    def contains(self,p):
        return p.x>=self.pos.x and p.x<=self.pos.x+4 and p.y>=self.pos.y and p.y<=self.pos.y+4 and p.z>=self.pos.z and p.z<=self.pos.z+4 and p.w>=self.pos.w and p.w<=self.pos.w+4
    
    def getScreenPos(self,p):
        trans=p.sub(self.pos)
        
        return Point(round(trans.x*(tileSize+sm)+trans.w*(tileSize*5+sm*4+lg)+lg),round((4-trans.y)*(tileSize+sm)+(4-trans.z)*(tileSize*5+sm*4+lg))+lg)
    
    def move(self,v):
        self.pos.move(v)

    def draw(self,window):
        
        newElements=[]
        exceptions=[]
        for i in range(5):
            for k in range(5):
                for j in range(5):
                    for l in range(5):
                        wp=point(self.pos.x+i,self.pos.y+j,self.pos.z+k,self.pos.w+l)
                        block=self.w.getBlock(wp.x,wp.y,wp.z,wp.w)
                        sp=self.getScreenPos(wp)
                        sp2=Point(sp.getX()+tileSize,sp.getY()+tileSize)
                        vox=Rectangle(sp,sp2)
                        c=COLOR[block]
                        vox.setFill(color_rgb(c[0],c[1],c[2]))
                        if vox in self.elements:
                            exceptions.append(vox)
                        else:
                            vox.draw(window)
                        newElements.append(vox)
        crect=Rectangle(Point(lg+2,lg+2),Point(lg+140,lg+30))
        crect.setFill(color_rgb(255,255,255))
        crect.draw(window)
        newElements.append(crect)
        coords=Text(Point(lg+70,lg+20),"X: "+str(self.pos.x+2)+" Y:"+str(self.pos.y+2)+" Z:"+str(self.pos.z+2)+" W:"+str(self.pos.w+2))
        coords.draw(window)
        newElements.append(coords)

        self.partialUndraw(exceptions)
        self.elements=newElements

    def undraw(self):
        for e in self.elements:
            e.undraw()
        self.elements=[]
    
    def partialUndraw(self,exceptions):
        for e in self.elements:
            if not e in exceptions:
                e.undraw()
        self.elements=exceptions

# sq=Rectangle(Point(10,10),Point(20,20))
# sq=Rectangle(Point(10,10),Point(20,20))
# sq.setFill(color_rgb(200,10,200))
# sq.draw(win)

# world.fill(-20,18,-20,-20,20,20,20,20,1)
#world.fill(-2,18,-2,-2,2,20,2,2,1)
#print("drawing lines...")
#world.draw(line(point(0,20,size,-10),point(size*(10+2*5**(1/2))**(1/2)/4,20,size*(5**(1/2)-1)/4,-10)),bl)
#world.draw(line(point(0,20,size,-10),point(-size*(10+2*5**(1/2))**(1/2)/4,20,size*(5**(1/2)-1)/4,-10)),bl)
#world.draw(line(point(size*(10+2*5**(1/2))**(1/2)/4,20,size*(5**(1/2)-1)/4,-10),point(size*(10-2*5**(1/2))**(1/2)/4,20,-size*(5**(1/2)+1)/4,-10)),bl)
#world.draw(line(point(-size*(10-2*5**(1/2))**(1/2)/4,20,-size*(5**(1/2)+1)/4,-10),point(size*(10-2*5**(1/2))**(1/2)/4,20,-size*(5**(1/2)+1)/4,-10)),bl)
#world.draw(line(point(-size*(10-2*5**(1/2))**(1/2)/4,20,-size*(5**(1/2)+1)/4,-10),point(-size*(10+2*5**(1/2))**(1/2)/4,20,size*(5**(1/2)-1)/4,-10)),bl)
files=[]
for filename in os.listdir("hox"):
    if filename.endswith(".json") or filename.endswith(".hox"):
        files.append(filename)
    else:
        continue

windowWidth=750
windowHeight=750
bl=4
size=3

sm=1
lg=6
tileSize=(windowWidth-lg*6-sm*20)/25
selectedFile=0
win.setBackground("white")
elements=[]
def drawFileNames():
    for i in range(10):
        fileNo=selectedFile+5-i
        if (fileNo>-1 and fileNo<len(files)):
            if fileNo==selectedFile:
                rect=Rectangle(Point(0,3*lg+20*(i)),Point(windowWidth,3*lg+20*(i+1)))
                rect.setFill(color_rgb(0,255,0))
                rect.draw(win)
                elements.append(rect)
            text=Text(Point(lg+70,lg+20*(i+1)),files[fileNo])
            text.draw(win)
            elements.append(text)

   

drawFileNames()
key=""

while not key=="Return":
    key=win.getKey()
    if key=="w":
        if selectedFile<len(files)-1:
            selectedFile=selectedFile+1
            for e in elements:
                e.undraw()
            elements=[]
            drawFileNames()
    elif key=="s":
        if selectedFile>0:
            selectedFile=selectedFile-1
            for e in elements:
                e.undraw()
            elements=[]
            drawFileNames()
for e in elements:
    e.undraw()
elements=[]

model=hoxlib.loadHoxelModelData("hox/"+files[selectedFile])

cam=camera(point(-2,20,-2,-2),world)
cam.draw(win)

key=""

while not key=="Return":
    key=win.getKey()
    if key=="w":
        cam.move(point(0,0,1,0))
        cam.draw(win)
    elif key=="s":
        cam.move(point(0,0,-1,0))
        cam.draw(win)
    elif key=="d":
        cam.move(point(1,0,0,0))
        cam.draw(win)
    elif key=="a":
        cam.move(point(-1,0,0,0))
        cam.draw(win)
    elif key=="e":
        cam.move(point(0,0,0,1))
        cam.draw(win)
    elif key=="q":
        cam.move(point(0,0,0,-1))
        cam.draw(win)
    elif key=="space":
        cam.move(point(0,1,0,0))
        cam.draw(win)
    elif key=="Shift_L":
        cam.move(point(0,-1,0,0))
        cam.draw(win)

for i in range(len(model["mat"])):
    unflat=hoxlib.unflattenCA(i,model["width"],model["height"],model["length"],model["trength"])
    block=model["mat"][i]
    if block==6:
        block=7
    wp=point(unflat[0],unflat[1],unflat[2],unflat[3]).add(cam.pos)
    world.setPoint(wp,block)

# print("Saving world...")
world.save(gpath+"square")
# print("World saved")
# input("press enter to continue")

