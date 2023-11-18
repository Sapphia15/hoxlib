#!/usr/bin/python3
# (still runs on the windows too tho)
# unsurprisingly this needs python

# Place this script file into your 4D Miner folder (the one with '4D Miner.exe', 'assets', etc.)
# This script doesn't modify any data (outside of the schematics folder), so it is safe to use
# by Redjard
#  (GPLv3 or whatever, like mod it but don't close-source it and don't publish it without telling others not to close-source your version)

write = lambda *strs: print( *strs, sep='', end='', flush=True )

import numpy as np
import os
import itertools


class Chunk:
    # all coords are (x, y, z, w)
    
    dims = (8,128,8,8)
    
    # coords in (x//8,z//8,w//8)
    @classmethod
    def fromChunkcoords(self, worlddir, coords ):
        return self.fromChunkname(worlddir, f'x{coords[0]}z{coords[1]}w{coords[2]}' )
    
    @classmethod
    def fromChunkname(self, worlddir, chunkname ):
        
        # if (chunk := self.fromFile(os.path.join(worlddir,chunkname,'blocks.bin'))) is not None:
        if (chunk := self.fromFile(os.path.join(worlddir,chunkname+'.bin'))) is not None:
            return chunk
        
        print(f"Couldn't find chunk {chunkname}!")
        return None
    
    @classmethod
    def fromFile(self, filename ):
        if not os.path.isfile(filename):
            return None
        
        with open( filename, 'rb' ) as blocksbin:
            return self( blocksbin.read() )
    
    def __init__(self, data=None, dims=None ):
        if dims is not None:
            self.dims = dims
        self.blockdata = np.zeros( shape=self.dims, dtype='uint8' )
        if data is not None:
            self.loadData(data)
    
    # gets run-length encoded data used by 4dm
    def loadData(self,data):
        data = np.array(list(data),dtype='uint8')
        data = data.reshape( (len(data)//2,2) )
        
        self.blockdata.resize((np.prod(self.dims),))
        index = 0
        for blocktype, runlength in data:
            self.blockdata[ index : index+runlength ] = blocktype
            index += runlength
        self.blockdata.resize(self.dims)
    
    def serializeData(self):
        self.blockdata.resize((np.prod(self.dims),))
        
        out = b''
        curBlock = self.blockdata[0]
        runLength = 0
        for block in self.blockdata:
            if runLength >= 255 or block != curBlock:
                out += bytes([ curBlock, runLength ])
                runLength = 0
                curBlock = block
            runLength += 1
        out += bytes([ curBlock, runLength ])
        
        self.blockdata.resize(self.dims)
        return out
            
    
    def __getitem__(self,index):
        return self.blockdata.__getitem__(cleanIndex(index))
    
    def __setitem__(self,index,val):
        return self.blockdata.__setitem__(cleanIndex(index),val)
    
    def __len__(self):
        return np.prod(self.dims)


def cleanIndex(index):
    
    if isinstance(index,slice):
        if index.start is None and index.stop is None:
            return index
        
        try: # if iterable
            start = np.full(index.stop.shape, None) if index.start is None else index.start
            stop  = np.full(index.start.shape,None) if index.stop  is None else index.stop
            iter(start),iter(stop)
        except:
            return index
        
        if len(start) != len(stop):
            raise TypeError('vectors of slice must be of equal length')
        
        return tuple( slice(strt,stp) for strt, stp in zip(start,stop) )
    
    return index


def serializeInt(num:int):
    
    num *= 2
    if num < 0:
        num = -num -1
    
    return serialize_uint(num)

#Unsigned Int Serialization:

#Big endian
#The integer is serialized as the value of an Integer Chunk
#  
#Integer Chunk:
#  length of integer value in bytes : 1 byte with non 0 value and a bias of 1 if preceded by x00, otherwise the bias is 0 or x00 followed by an integer chunk
#  value of integer : the value of the integer that this chunk encodes using the number of bytes indicated by the length of integer value in bytes
#
#Examples:
#
#  /x01/x14 encodes 20 because the first byte indicates that the integer is one byte long while the second byte indicates the encoded value
#  /x02/x01/x00 encodes 256 because the first byte indicates that the integer is two bytes long while the two bytes that follow indicate the encoded values as a two byte int
#  /x00/x01/x01/x01/x01/(x00)*256 encodes 16^512 because the first byte indicates that the integer length is encoded as an Integer Chunk instead of as one byte so the second byte indicates that the value of of the length of the integer that inticates the length of the integer being serialized is 2 becuase it has a bias of 1 since it follows an x00 byte. The third and fourth bit indicate the value of the length of the integer being encoded as a two byte integer which is 257. The 257 bytes that come after the fourth byte encode the value of the integer being serialized as a 257 byte integer which has the value of 16^512.
def serialize_uint(num:int):
    
    bitstr = b''
    while num:
        bitstr += bytes([ num %2**8 ])
        num //= 2**8
    bitstr = bitstr[::-1]
    
    if len(bitstr) == 0:
        bitstr = b'\x00'
    
    if len(bitstr) >= 2**8:
        return b'\x00' + serialize_uint(len(bitstr)-2**8) + bitstr
    
    return bytes([len(bitstr)]) + bitstr

def unserializeInt(bitstr:int):
    
    num, bitstr = unserialize_uint(bitstr)
    
    if num %2:
        num = -num -1
    num >>= 1  # same as  //= 2  but faster
    
    return num, bitstr

def unserialize_uint(bitstr:int):
    
    if bitstr[0] == 0:
        numlen, bitstr = unserialize_uint(bitstr[1:])
        numlen += 2**8
    else:
        numlen, bitstr = bitstr[0], bitstr[1:]
    
    if numlen > len(bitstr):
        raise ValueError('Incomplete integer')
    
    num = 0
    for bit in bitstr[:numlen]:
        num *= 2**8
        num += bit
    
    return num, bitstr[numlen:]


basedir = os.path.dirname(__file__)

expectedfiles = ['4D Miner.exe','4D Server.exe']
#if not True in [ os.path.isfile(os.path.join(basedir, expectedfile)) for expectedfile in expectedfiles ]:
    #print(f"current directory is '{basedir}', which unexpectedly does not contain '{expectedfile}'. Are you sure this is correct? If so, you may now edit the script and comment out this check. If you cannot do that, you probably shouldn't either.")
    #raise SystemExit

worldname = input('please enter name of worlddir: ')

worldname = worldname.lower()
worldname = worldname.replace('/','_').replace("'",'_')

worlddir = os.path.join( basedir, 'worlds', worldname, 'chunks' )

if not os.path.exists(worlddir):
    print(f"World '{worldname}' not found ({repr(worlddir)})")
    raise SystemExit

write('\x1b[1A\x1b[K', f"World: {worldname}", "\n")

coord1 = input('please input your first corner in the form (x,y,z,w): ')
try:
    coord1 = tuple(map(int,coord1.replace('(','').replace(')','').split(',')))
    if len(coord1) != 4: raise SystemExit
except:
    print(f"Input was not understood as valid coordinate")
    raise SystemExit
write('\x1b[1A\x1b[K', f"1st corner: {coord1}", "\n")

coord2 = input('please input the opposing corner in the form (x,y,z,w): ')
try:
    coord2 = tuple(map(int,coord2.replace('(','').replace(')','').split(',')))
    if len(coord2) != 4: raise SystemExit
except:
    print(f"Input was not understood as valid coordinate")
    raise SystemExit
write('\x1b[1A\x1b[K', f"2nd corner: {coord2}", "\n")

# make coord1 the lower and coord2 the upper corner
coord1, coord2 = np.min((coord1,coord2),axis=0), np.max((coord1,coord2),axis=0)

lengths = coord2 - coord1 +1

print(f"loading {'x'.join(map(str,lengths))} shape")


# get list of all chunks that hold part of the selected region
chunks = np.array(tuple(itertools.product( *map( lambda l,u: range(l,u+1), coord1[[0,2,3]] //8, coord2[[0,2,3]] //8 ) )))

chunks = tuple( (chunkcoords,Chunk.fromChunkcoords(worlddir,chunkcoords)) for chunkcoords in chunks )

if any( 1 for coords, chunk in chunks if chunk is None ):
    print(f"Some chunks in the region you selected are not generated and saved yet. To save them, place and/or break a block within them.")
    raise SystemExit

schematic = Chunk(dims=lengths)
for chunkcoords, chunk in chunks:
    
    chunklower = chunkcoords*8
    chunkupper = chunkcoords*8 +7
    chunklower = np.insert(chunklower,1,0)
    chunkupper = np.insert(chunkupper,1,127)
    
    lower = np.max(( coord1, chunklower ),axis=0) % Chunk.dims
    upper = np.min(( chunkupper, coord2 ),axis=0) % Chunk.dims
    
    partlower = chunklower + lower - coord1
    partupper = chunklower + upper - coord1
    
    schematic[partlower:partupper+1] = chunk[lower:upper+1]

schematicbin = b''.join( serialize_uint(length) for length in lengths ) + serialize_uint(0) + schematic.serializeData()


print(f"Generated schematic containing {len(schematic)} blocks, size is {len(schematicbin)} bytes.")

schemename = input('please enter filename to save schematic under: ')

schemename = schemename.replace('/','∕')
schemename += '.4dmscheme'

schemesdir = os.path.join( basedir, 'schematics' )
schemedir = os.path.join( schemesdir, schemename )

write('\x1b[1A\x1b[K', f"Schematic: {schemename}", "\n")


if not os.path.exists(schemesdir):
    os.makedirs(schemesdir)

with open( schemedir, 'wb' ) as file:
    file.write( schematicbin )


print(f"Schematic saved as {repr(schemedir)}")