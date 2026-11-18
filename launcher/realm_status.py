"""Public aggregate realm status; never transports operator credentials."""
import json
import socket
import threading
import time
from urllib.request import Request
from .transport import urlopen
from urllib.parse import urlsplit

def validate(data,environment,now):
    if data.get('environment')!=environment:raise ValueError('Wrong environment')
    stamp=data.get('timestamp')
    if type(stamp) not in (int,float) or not 0<=now-stamp<=90:raise ValueError('Stale status')
    if type(data.get('online')) is not bool:raise ValueError('Missing state')
    count=data.get('players')
    if type(count) is not int or not 0<=count<=100000:raise ValueError('Invalid count')
    return {'state':'online' if data['online'] else 'offline','players':count if data['online'] else 0}

class Monitor:
    def __init__(self,root):
        self.root=root;self.lock=threading.Lock();self.cache={};self.pending=set()
    def read(self,environment):
        with self.lock:
            stamp,result=self.cache.get(environment,(0,{'state':'unknown'}))
            if time.monotonic()-stamp>=30 and environment not in self.pending:
                self.pending.add(environment)
                threading.Thread(target=self.refresh,args=(environment,),daemon=True).start()
            return dict(result) if time.monotonic()-stamp<90 else {'state':'unknown'}
    def refresh(self,environment):
        result={'state':'unknown'}
        try:
            config=self.root/'config/realm-status.json'
            url=json.loads(config.read_text()).get(environment) if config.exists() else None
            if url:
                parsed=urlsplit(url)
                if parsed.scheme!='https' or parsed.username or parsed.password or parsed.fragment:raise ValueError('HTTPS required')
                with urlopen(Request(url,headers={'Accept':'application/json'}),timeout=4,allow_redirects=False) as response:
                    raw=response.read(4097)
                if len(raw)>4096:raise ValueError('Oversized status')
                result=validate(json.loads(raw),environment,time.time())
            else:
                host='127.0.0.1' if environment=='development' else '129.121.172.245'
                for port in (3727,8088):
                    with socket.create_connection((host,port),timeout=2):pass
                result={'state':'online','players':None}
        except ConnectionRefusedError:result={'state':'offline'}
        except Exception as error:
            cause=getattr(error,'reason',error)
            result={'state':'unknown','diagnostic':{'type':type(cause).__name__,'errno':getattr(cause,'errno',None)}}
        finally:
            with self.lock:self.cache[environment]=(time.monotonic(),result);self.pending.discard(environment)
