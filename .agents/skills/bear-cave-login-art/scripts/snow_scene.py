"""Keep the original Northrend animated snow batch over a new static art plane.
Donor bytes stay local. Appending preserves all retained animation offsets.
"""
import struct,math
P=lambda fmt,*v:struct.pack('<'+fmt,*v)
def snow_scene(original,skin):
 m=bytearray(original);s=bytearray(skin)
 assert m[:8]==P('4sI',b'MD20',264) and s[:4]==b'SKIN'
 def get(buf,at,stride):
  n,o=struct.unpack_from('<II',buf,at);assert o+n*stride<=len(buf);return n,bytes(buf[o:o+n*stride])
 def put(buf,at,n,data):
  buf.extend(b'\0'*((-len(buf))%16));o=len(buf);buf.extend(data);struct.pack_into('<II',buf,at,n,o);return o
 nt,tex=get(m,80,16);snow=[]
 for i in range(nt):
  kind,flags,n,o=struct.unpack_from('<4I',tex,16*i)
  if m[o:o+n].rstrip(b'\0').upper().endswith(b'SNOWFLAKE01B.BLP'):snow.append(i)
 assert len(snow)==1
 nl,lookup=get(m,128,2);lookup=struct.unpack('<'+'H'*nl,lookup)
 nb,batches=get(s,36,24);keep=[]
 for i in range(nb):
  raw=batches[i*24:(i+1)*24];b=struct.unpack('<BbHHHh7H',raw)
  if b[8]==1 and lookup[b[9]]==snow[0]:keep.append(raw)
 assert len(keep)==1,'Expected the audited original snow layer'
 # No dragon particles, lights, sounds, ribbons or attachments remain active.
 for at in [240,248,256,264,288,296]:struct.pack_into('<II',m,at,0,0)
 struct.pack_into('<I',m,68,1)
 # Preserve original camera so the existing snow retains its placement.
 nc,camera=get(m,272,100);assert nc==1
 _,fov,far,near=struct.unpack_from('<ifff',camera)
 cx,cy,cz=struct.unpack_from('<3f',camera,36)
 tx,ty,tz=struct.unpack_from('<3f',camera,68)
 assert abs(cy-ty)<.001 and abs(cz-tz)<.001 and cx>tx
 depth=50.;aspect=16/9
 halfh=depth*math.tan(fov/math.sqrt(1+aspect*aspect)/2)*1.02
 halfw=halfh*1.75
 # Static root appended without disturbing the original snow bones/tracks.
 bones,bonebytes=get(m,44,88);track=P('Hh4I',0,-1,0,0,0,0)
 put(m,44,bones+1,bonebytes+P('iIhHI',-1,0,-1,0,0)+track*3+P('3f',0,0,0))
 nv,verts=get(m,60,48);quad=b''
 for y,z,u,v in [(-halfw,halfh,.0625,0),(halfw,halfh,.9375,0),(halfw,-halfh,.9375,1),(-halfw,-halfh,.0625,1)]:
  quad+=P('3f4B4B3f4f',cx-depth,cy+y,cz+z,255,0,0,0,0,0,0,0,1,0,0,u,v,u,v)
 put(m,60,nv+4,verts+quad)
 name=b'Interface\\Glues\\BearCave\\Background.blp\0';m.extend(b'\0'*((-len(m))%16));o=len(m);m.extend(name)
 put(m,80,nt+1,tex+P('4I',0,0,len(name),o))
 nm,materials=get(m,112,4);put(m,112,nm+1,materials+P('HH',7,0))
 nbl,bl=get(m,120,2);put(m,120,nbl+1,bl+P('H',bones))
 put(m,128,nl+1,P('H'*nl,*lookup)+P('H',nt))
 # Explicit full-opacity track, UV set zero, no transform.
 def raw(data):m.extend(b'\0'*((-len(m))%16));o=len(m);m.extend(data);return o
 times=raw(P('II',1,raw(P('I',0))));values=raw(P('II',1,raw(P('h',32767))))
 nw,weights=get(m,88,20);put(m,88,nw+1,weights+P('Hh4I',0,-1,1,times,1,values))
 indices={}
 for at,value in [(136,0),(144,nw),(152,65535)]:
  n,data=get(m,at,2);put(m,at,n+1,data+P('H',value));indices[at]=n
 ni,idx=get(s,4,2);put(s,4,ni+4,idx+P('4H',nv,nv+1,nv+2,nv+3))
 ntri,tri=get(s,12,2);put(s,12,ntri+6,tri+P('6H',ni,ni+1,ni+2,ni,ni+2,ni+3))
 np,props=get(s,20,4);assert np==ni;put(s,20,np+4,props+b'\0'*16)
 ns,sections=get(s,28,48)
 put(s,28,ns+1,sections+P('10H7f',0,0,ni,4,ntri,6,1,nbl,1,bones,cx-depth,cy,cz,cx-depth,cy,cz,halfw*2))
 batch=P('BbHHHh7H',0,0,0,ns,ns,-1,nm,0,1,nl,indices[136],indices[144],indices[152])
 put(s,36,2,batch+b''.join(keep))
 # Broaden bounds for background and retained snow.
 bounds=P('7f',cx-depth-1,cy-halfw,cz-halfh,cx+1,cy+halfw,cz+halfh,depth+halfw*2)
 m[160:188]=bounds;m[188:216]=bounds
 assert struct.unpack_from('<I',s,36)[0]==2
 return bytes(m),bytes(s)
