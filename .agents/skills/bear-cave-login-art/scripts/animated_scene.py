"""Original small MD20 animation: snow quads and optionally a pinned cloth grid."""
import math,struct,random
from build_scene import scene as static_scene,P
DURATION=12000
def scene(banner=False):
 base,unused=static_scene();m=bytearray(base)
 def raw(data):
  m.extend(b'\0'*((-len(m))%16));o=len(m);m.extend(data);return o
 def arr(at,n,data):struct.pack_into('<II',m,at,n,raw(data))
 empty=P('Hh4I',0,-1,0,0,0,0)
 def motion(keys):
  times=raw(b''.join(P('I',t)for t,v in keys));values=raw(b''.join(P('3f',*v)for t,v in keys))
  ta=raw(P('II',len(keys),times));va=raw(P('II',len(keys),values))
  return P('Hh4I',1,-1,1,ta,1,va)
 bones=[P('iIhHI',-1,0,-1,0,0)+empty*3+P('3f',0,0,0)]
 def bone(keys):
  i=len(bones);bones.append(P('iIhHI',-1,0x200,-1,0,0)+motion(keys)+empty*2+P('3f',0,0,0));return i
 vertices=[];indices=[];sections=[]
 def vertex(x,y,z,u,v,b=0):
  i=len(vertices);vertices.append(P('3f4B4B3f4f',x,y,z,255,0,0,0,b,0,0,0,1,0,0,u,v,u,v));return i
 def quad(x,left,right,top,bottom,uv=(0,1,0,1),b=0):
  n=len(vertices);l,r,t,bt=uv
  for y,z,u,v in [(left,top,l,t),(right,top,r,t),(right,bottom,r,bt),(left,bottom,l,bt)]:vertex(x,y,z,u,v,b)
  indices.extend([n,n+1,n+2,n,n+2,n+3])
 def section(startv,starti,texture):sections.append((startv,len(vertices)-startv,starti,len(indices)-starti,texture))
 quad(0,-8,8,4.571429,-4.571429,(.0625,.9375,0,1));section(0,0,0)
 textures=['Interface\\Glues\\BearCave\\Background.blp','Interface\\Glues\\BearCave\\Snow.tga']
 if banner:
  textures+=['Interface\\Glues\\BearCave\\Cloth.blp','Interface\\Glues\\BearCave\\Frame.blp']
  sv,si=len(vertices),len(indices);cols,rows=6,5
  # Both supplied canvases share 512x1024 dimensions. Fit cloth under rope beam.
  for row in range(rows+1):
   v=row/rows
   for col in range(cols+1):
    u=col/cols;free=max(0,min(1,(v-(.02+.25*u))/.65))
    b=0
    if free:
     keys=[]
     for k in range(25):
      t=k*500;angle=2*math.pi*k/24+u*3-v*2
      keys.append((t,(.10*free*math.sin(angle),.045*free*math.sin(angle),.02*free*math.cos(angle))))
     b=bone(keys)
    vertex(.8,3.2+(40+.8*512*u)/512*3.0,3.7-(80+.8*1024*v)/1024*6.0,u,v,b)
  for row in range(rows):
   for col in range(cols):
    i=sv+row*(cols+1)+col;indices.extend([i,i+1,i+cols+2,i,i+cols+2,i+cols+1])
  section(sv,si,2)
  sv,si=len(vertices),len(indices);quad(1,3.2,6.2,3.7,-2.3);section(sv,si,3)
 # Snow starts above and finishes below the viewport; wrap happens offscreen.
 rng=random.Random(20260926);sv,si=len(vertices),len(indices)
 for i in range(56):
  phase=rng.randrange(DURATION);y=rng.uniform(-8,8);size=rng.uniform(.017,.035);drift=rng.uniform(.08,.22)
  wrap=DURATION-phase;times=sorted(set([0,DURATION]+list(range(0,DURATION+1,500))+([wrap-1,wrap]if 0<wrap<DURATION else [])))
  keys=[]
  for t in times:
   elapsed=(t+phase)%DURATION
   keys.append((t,(0,drift*math.sin(2*math.pi*(t+phase)/DURATION),6-12*elapsed/DURATION)))
  b=bone(keys);quad(2,y-size,y+size,size,-size,b=b)
  if (i+1)%28==0:
   section(sv,si,1);sv,si=len(vertices),len(indices)
 assert len(bones)<256 and len(vertices)<65536
 arr(44,len(bones),b''.join(bones));arr(60,len(vertices),b''.join(vertices))
 palettes=[sorted({vertices[j][16] for j in range(sv,sv+nv)}) for sv,nv,si,ni,tex in sections]
 assert max(map(len,palettes))<=53,'Per-section bone palette exceeds conservative renderer limit'
 lookup=[b for palette in palettes for b in palette]
 arr(120,len(lookup),P('H'*len(lookup),*lookup))
 texture_data=b''
 for path in textures:
  name=path.encode()+b'\0';o=raw(name);texture_data+=P('4I',0,0,len(name),o)
 arr(80,len(textures),texture_data);arr(128,len(textures),P('H'*len(textures),*range(len(textures))))
 arr(112,2,P('4H',7,0,23,2))
 # Preserve the working static camera and opacity track. Extend Stand duration.
 n,o=struct.unpack_from('<II',m,28);struct.pack_into('<I',m,o+4,DURATION)
 s=bytearray(48);s[:4]=b'SKIN'
 def sa(at,n,data):
  s.extend(b'\0'*((-len(s))%16));o=len(s);s.extend(data);struct.pack_into('<II',s,at,n,o)
 sa(4,len(vertices),P('H'*len(vertices),*range(len(vertices))));sa(12,len(indices),P('H'*len(indices),*indices))
 props=bytearray(len(vertices)*4)
 for (sv,nv,si,ni,tex),palette in zip(sections,palettes):
  for j in range(sv,sv+nv):props[j*4]=palette.index(vertices[j][16])
 sa(20,len(vertices),bytes(props))
 sm=b'';batches=b'';palette_start=0
 for i,(sv,nv,si,ni,tex)in enumerate(sections):
  sm+=P('10H7f',0,0,sv,nv,si,ni,len(palettes[i]),palette_start,1,0,0,0,0,0,0,0,12)
  palette_start+=len(palettes[i])
  batches+=P('BbHHHh7H',0,0,0,i,i,-1,0 if tex==0 else 1,0,1,tex,0,0,0)
 sa(28,len(sections),sm);sa(36,len(sections),batches);struct.pack_into('<I',s,44,max(map(len,palettes)))
 validate(bytes(m),bytes(s));return bytes(m),bytes(s)
def snow_texture():
 # Original soft flake sprite, BGRA uncompressed TGA, top-origin.
 data=bytearray(struct.pack('<BBBHHBHHHHBB',0,0,2,0,0,0,0,0,16,16,32,0x28))
 for y in range(16):
  for x in range(16):
   r=math.hypot(x-7.5,y-7.5)/7.5;alpha=int(190*max(0,1-r)**1.5);data.extend((255,250,240,alpha))
 return bytes(data)
def validate(m,s):
 def block(buf,at,size):
  n,o=struct.unpack_from('<II',buf,at);assert o+n*size<=len(buf);return n,o
 nb,ob=block(m,44,88);nv,ov=block(m,60,48);assert nb<256
 for i in range(nb):
  for at in [16,36,56]:
   inter,g,nt,ot,nk,ok=struct.unpack_from('<Hh4I',m,ob+88*i+at);assert nt==nk
   if nt:
    assert nt==1;tc,to=struct.unpack_from('<II',m,ot);kc,ko=struct.unpack_from('<II',m,ok);assert tc==kc and to+tc*4<=len(m) and ko+kc*(8 if at==36 else 12)<=len(m)
    times=struct.unpack_from('<'+'I'*tc,m,to);assert list(times)==sorted(times) and times[-1]==DURATION
 for i in range(nv):assert m[ov+48*i+16]<nb and sum(m[ov+48*i+12:ov+48*i+16])==255
 ni,oi=block(s,4,2);nt,ot=block(s,12,2);assert ni==nv
 assert max(struct.unpack_from('<'+'H'*ni,s,oi))<nv and max(struct.unpack_from('<'+'H'*nt,s,ot))<ni
 for at,size in [(20,4),(28,48),(36,24)]:block(s,at,size)
 nl,ol=block(m,120,2);lookup=struct.unpack_from('<'+'H'*nl,m,ol)
 ns,os=block(s,28,48);np,op=block(s,20,4)
 for i in range(ns):
  fields=struct.unpack_from('<10H',s,os+i*48);sv,nv,si,nt,nb,start=fields[2:8]
  assert nb<=53 and start+nb<=nl and sv+nv<=np
  for j in range(sv,sv+nv):
   local=s[op+j*4];assert local<nb and lookup[start+local]==m[ov+j*48+16]
 assert all(struct.unpack_from('<II',m,a)==(0,0)for a in [240,256,264,288,296])
if __name__=='__main__':
 for banner in [False,True]:
  m,s=scene(banner);validate(m,s);print('PASS original animation', 'snow+banner'if banner else 'snow',len(m),len(s))
