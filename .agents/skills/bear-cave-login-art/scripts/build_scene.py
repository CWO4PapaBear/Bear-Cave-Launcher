"""Original static WotLK MD20/v264 quad, camera and external SKIN writer.
Field layouts checked against wowdev/pywowlib file_formats/m2_format.py and skin_format.py.
No executable or GlueXML changes. In-client rendering still requires acceptance.
"""
import struct,math
P=lambda fmt,*v:struct.pack('<'+fmt,*v)
# WotLK's camera FOV is diagonal, not vertical. Fit the useful artwork width
# at the reviewed 1920x1080 viewport; retain a small cover margin.
ASPECT=16/9
FOV=.7
CAMERA_DISTANCE=(8/ASPECT)/math.tan((FOV/math.sqrt(1+ASPECT*ASPECT))/2)*.99
def scene():
 m=bytearray(304);m[:8]=P('4sI',b'MD20',264)
 def append(data):
  m.extend(b'\0'*((-len(m))%16));offset=len(m);m.extend(data);return offset
 def array(at,count,data):struct.pack_into('<II',m,at,count,append(data))
 track=P('Hh4I',0,-1,0,0,0,0)
 bounds=P('7f',-.1,-8,-4.571429,.1,8,4.571429,10)
 array(8,14,b'BearCaveLogin\0')
 # Stand sequence, internal data, no aliases or movement.
 sequence=P('HHIfIhHIII',0,0,1000,0,0x20,32767,0,0,0,0)+bounds+P('hH',-1,0)
 assert len(sequence)==64
 array(28,1,sequence);array(36,1,P('H',0))
 bone=P('iIhHI',-1,0,-1,0,0)+track*3+P('3f',0,0,0)
 assert len(bone)==88;array(44,1,bone);array(52,1,P('h',-1))
 vertices=[]
 for y,z,u,v in [(-8,4.571429,.0625,0),(8,4.571429,.9375,0),(8,-4.571429,.9375,1),(-8,-4.571429,.0625,1)]:
  vertices.append(P('3f4B4B3f4f',0,y,z,255,0,0,0,0,0,0,0,1,0,0,u,v,u,v))
 assert all(len(v)==48 for v in vertices);array(60,4,b''.join(vertices));struct.pack_into('<I',m,68,1)
 name=b'Interface\\Glues\\BearCave\\Background.blp\0';offset=append(name)
 array(80,1,P('4I',0,0,len(name),offset))
 # One full-opacity texture weight with a constant key in sequence zero.
 time=append(P('I',0));value=append(P('h',32767))
 times=append(P('II',1,time));values=append(P('II',1,value))
 array(88,1,P('Hh4I',0,-1,1,times,1,values))
 array(112,1,P('HH',1|2|4,0)) # unlit, unfogged, two sided, opaque
 for at,value in [(120,0),(128,0),(136,0),(144,0)]:array(at,1,P('H',value))
 array(152,1,P('h',-1))
 m[160:188]=bounds;m[188:216]=bounds
 camera=P('ifff',0,FOV,1000,.1)+track+P('3f',CAMERA_DISTANCE,0,0)+track+P('3f',0,0,0)+track
 assert len(camera)==100;array(272,1,camera);array(280,1,P('H',0))
 s=bytearray(48);s[:4]=b'SKIN'
 def skin_array(at,count,data):
  s.extend(b'\0'*((-len(s))%16));offset=len(s);s.extend(data);struct.pack_into('<II',s,at,count,offset)
 skin_array(4,4,P('4H',0,1,2,3));skin_array(12,6,P('6H',0,1,2,0,2,3));skin_array(20,4,b'\0'*16)
 skin_array(28,1,P('10H7f',0,0,0,4,0,6,1,0,1,0,0,0,0,0,0,0,10))
 skin_array(36,1,P('BbHHHh7H',0,0,0,0,0,-1,0,0,1,0,0,0,0));struct.pack_into('<I',s,44,1)
 return bytes(m),bytes(s)

def validate(m,s):
 assert m[:8]==P('4sI',b'MD20',264) and s[:4]==b'SKIN'
 for at,stride in [(8,1),(28,64),(36,2),(44,88),(52,2),(60,48),(80,16),(88,20),(112,4),(120,2),(128,2),(136,2),(144,2),(152,2),(272,100),(280,2)]:
  n,o=struct.unpack_from('<II',m,at);assert o>=304 and o+n*stride<=len(m),(at,n,o)
 for at,stride in [(4,2),(12,2),(20,4),(28,48),(36,24)]:
  n,o=struct.unpack_from('<II',s,at);assert o>=48 and o+n*stride<=len(s)
 n,o=struct.unpack_from('<II',s,12);assert max(struct.unpack_from('<'+'H'*n,s,o))<4
 assert not any(struct.unpack_from('<I',m,at)[0]for at in [240,256,264,288,296])
 return True
if __name__=='__main__':
 m,s=scene();validate(m,s);print('PASS: generated M2/SKIN array bounds, strides, indices, camera and no external effects.')
