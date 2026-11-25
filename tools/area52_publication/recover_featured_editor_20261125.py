from pathlib import Path
import hashlib,json,os
from announce_package import deliver
from publication_common import GitHub

package='area52-featured-editor-cloud-20261125'
root=Path('docs/publication')/package
config=json.loads((root/'config.json').read_text())
repo=config['notes_repo'];receipt_path=str(root/'discord-receipt.json')
api=GitHub();raw,_=api.file(repo,receipt_path);receipt=json.loads(raw)
if receipt.get('message_id') or receipt['status']=='complete':
    deliver(config,root,api,os.environ['DISCORD_PATCH_NOTES_WEBHOOK'])
else:
    expected=json.loads((root/'pre-send-recovery.json').read_text())
    assert receipt==expected['receipt'] and receipt['status']=='intent'
    run=api.api('repos/'+repo+'/actions/runs/45651671904')
    assert run['status']=='completed' and run['conclusion']=='failure'
    guard=str(root/'pre-send-recovery-start.json')
    old,_=api.file(repo,guard)
    assert old is None,'Recovery already attempted; reconcile before any further send'
    api.put(repo,guard,json.dumps({'original_run':45651671904,'status':'intent'}).encode(),'Reserve one proven pre-send recovery')
    class Recovery(GitHub):
        first=True
        def file(self,repository,path,ref='main'):
            value,revision=super().file(repository,path,ref)
            if self.first and repository==repo and path==receipt_path:
                assert json.loads(value)==receipt
                self.first=False
                return None,None
            return value,revision
    deliver(config,root,Recovery(),os.environ['DISCORD_PATCH_NOTES_WEBHOOK'])
