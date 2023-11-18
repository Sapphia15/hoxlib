#!/usr/bin/python3
# (still runs on the windows too tho)
# unsurprisingly this needs python

# Place this script file into your 4D Miner folder (the one with '4D Miner.exe', 'assets', etc.)
# This script WILL modify world data! If you have any irreplaceably valuable saves, better back them up.
# by Redjard
#  (GPLv3 or whatever, like mod it but don't close-source it and don't publish it without telling others not to close-source your version)

write = lambda *strs: print( *strs, sep='', end='', flush=True )

import numpy as np
import os
import itertools
from sys import argv


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
    
    def toFileByChunkcoords(self, worlddir, coords ):
        # with open( os.path.join(worlddir,f'x{coords[0]}z{coords[1]}w{coords[2]}','blocks.bin'), 'wb' ) as file:
        with open( os.path.join(worlddir,f'x{coords[0]}z{coords[1]}w{coords[2]}.bin'), 'wb' ) as file:
            file.write( self.serializeData() )
    
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
if not True in [ os.path.isfile(os.path.join(basedir, expectedfile)) for expectedfile in expectedfiles ]:
    print(f"current directory is '{basedir}', which unexpectedly does not contain '{expectedfile}'. Are you sure this is correct? If so, you may now edit the script and comment out this check. If you cannot do that, you probably shouldn't either.")
    raise SystemExit

try:
    schemname = argv[1]
except:
    print('Please call this script with a schematic as the first argument (drop the schematic file onto the script)')
    raise SystemExit

if not os.path.isfile(schemname):
    print(f"Schematic {repr(schemname)} not found")
    raise SystemExit

print(f"Schematic: {os.path.basename(schemname)}")


with open( schemname, 'rb' ) as schematic:
    schematicbin = schematic.read()

lengths = []
while True:
    length, schematicbin = unserialize_uint(schematicbin)
    if length == 0:
        break
    lengths.append( length )
lengths = np.array(lengths)

schematic = Chunk( data=schematicbin, dims=lengths )


print(f"Loaded schematic of size {'x'.join(map(str,schematic.dims))} containing {len(schematic)} blocks.")


worldname = input('please enter name of worlddir: ')

worldname = worldname.lower()
worldname = worldname.replace('/','_').replace("'",'_')

worlddir = os.path.join( basedir, 'worlds', worldname, 'chunks' )

if not os.path.exists(worlddir):
    print(f"World '{worldname}' not found ({repr(worlddir)})")
    raise SystemExit

write('\x1b[1A\x1b[K', f"World: {worldname}", "\n")


coord1 = input('please input the lower corner in the form (x,y,z,w): ')
try:
    coord1 = np.array(tuple(map(int,coord1.replace('(','').replace(')','').split(','))))
    if len(coord1) != 4: raise SystemExit
except:
    print(f"Input was not understood as valid coordinate")
    raise SystemExit

coord2 = coord1 + lengths -1

write('\x1b[1A\x1b[K', f"1st corner: {tuple(coord1)}", "\n")
print(f"2nd corner: {tuple(coord2)}")


# get list of all chunks that hold part of the selected region
chunks = np.array(tuple(itertools.product( *map( lambda l,u: range(l,u+1), coord1[[0,2,3]] //8, coord2[[0,2,3]] //8 ) )))

print(f"loading {len(chunks)} chunks ...")

chunks = tuple( (chunkcoords,Chunk.fromChunkcoords(worlddir,chunkcoords)) for chunkcoords in chunks )

if any( 1 for coords, chunk in chunks if chunk is None ):
    print(f"Some chunks in the region you selected are not generated and saved yet. To save them, place and/or break a block within them.")
    raise SystemExit

print(f"modifying {len(chunks)} chunks ...")

for chunkcoords, chunk in chunks:
    
    chunklower = chunkcoords*8
    chunkupper = chunkcoords*8 +7
    chunklower = np.insert(chunklower,1,0)
    chunkupper = np.insert(chunkupper,1,127)
    
    lower = np.max(( coord1, chunklower ),axis=0) % Chunk.dims
    upper = np.min(( chunkupper, coord2 ),axis=0) % Chunk.dims
    
    partlower = chunklower + lower - coord1
    partupper = chunklower + upper - coord1
    
    chunk[lower:upper+1] = schematic[partlower:partupper+1]

print(f"saving {len(chunks)} chunks ...")

for chunkcoords, chunk in chunks:
    chunk.toFileByChunkcoords( worlddir, chunkcoords )