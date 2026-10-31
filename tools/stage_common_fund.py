"""Build/validate outside CK3's watched folders; publish final changed files.

This preserves developer hot reload. Per-file replacement is atomic; the full
batch is not an engine-wide transaction. No claim of crash immunity is made.
"""
from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=('common','gfx','gui','localization','events')
COPY_FOLDERS=(*RUNTIME,'docs','tools')
ROOT_ASSETS=('thumbnail.png','thumbnail-original.png')
CHECKS=('verify_revenue_source.py','verify_common_fund.py','verify_project_contributions.py',
        'verify_auto_projects.py','verify_senior_jurisdiction.py','verify_common_fund_scheduler.py',
        'verify_project_edge_cases.py','verify_completion_safety.py','verify_censor.py','verify_justice.py')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def output_files(root):
    result={}
    for folder in (*RUNTIME,'docs'):
        for p in (root/folder).rglob('*'):
            if p.is_file():result[p.relative_to(root)]=digest(p)
    result[Path('descriptor.mod')]=digest(root/'descriptor.mod')
    for name in ROOT_ASSETS:
        if (root/name).exists():result[Path(name)]=digest(root/name)
    return result


def author_files(root):
    result=output_files(root)
    for p in (root/'tools').rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            result[p.relative_to(root)]=digest(p)
    result[Path('AGENTS.md')]=digest(root/'AGENTS.md')
    return result


def changes(before,after):
    writes=sorted((p for p,sha in after.items() if before.get(p)!=sha),key=str)
    # Only this explicitly retired generated output is removed. Author files
    # are never deleted just because a stage did not happen to contain them.
    obsolete=Path('common/great_projects/types/zz_mam_revenue_common_projects.txt')
    deletes=[obsolete] if obsolete in before and obsolete not in after else []
    return writes,deletes


def check_unchanged(root,before,targets):
    for rel in targets:
        if digest(root/rel)!=before.get(rel):
            raise RuntimeError('Source changed during staging; nothing published. Rebuild after reviewing: '+str(rel))


def replace_file(source,destination):
    destination.parent.mkdir(parents=True,exist_ok=True)
    # Same-volume temporary file, unrecognized .tmp extension. CK3 never sees
    # the destination as an empty/half-written script.
    descriptor,name=tempfile.mkstemp(prefix='.mam-publish-',suffix='.tmp',dir=destination.parent)
    temporary=Path(name)
    try:
        with os.fdopen(descriptor,'wb') as stream:
            stream.write(source.read_bytes());stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,destination)
    finally:
        if temporary.exists():temporary.unlink()


def build():
    before=output_files(ROOT)
    authors_before=author_files(ROOT)
    temp_parent=Path(os.environ.get('MAM_BUILD_STAGING_DIR',tempfile.gettempdir())).resolve()
    if temp_parent.is_relative_to(ROOT):
        raise RuntimeError('Staging must be outside the live mod tree, not in a watched game directory.')
    temp_parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='mam-cf-build-',dir=temp_parent) as name:
        stage_base=Path(name).resolve()
        assert stage_base.parent==temp_parent and stage_base.name.startswith('mam-cf-build-')
        stage=stage_base/'mandate_and_ministry';stage.mkdir()
        for folder in COPY_FOLDERS:
            shutil.copytree(ROOT/folder,stage/folder,ignore=shutil.ignore_patterns('__pycache__'))
        for filename in ['descriptor.mod','AGENTS.md']:
            shutil.copy2(ROOT/filename,stage/filename)
        for filename in ROOT_ASSETS:
            if (ROOT/filename).exists():shutil.copy2(ROOT/filename,stage/filename)
        environment=dict(os.environ,MAM_COMMON_FUND_STAGING='1',MAM_BUILD_STAGING_DIR=str(temp_parent))
        subprocess.run([sys.executable,str(stage/'tools/build_common_fund.py')],cwd=stage,env=environment,check=True)
        for check in CHECKS:
            subprocess.run([sys.executable,str(stage/'tools'/check)],cwd=stage,env=environment,check=True)
        after=output_files(stage)
        writes,deletes=changes(before,after)
        # Check the complete runtime snapshot, not just changed outputs: an
        # author concurrently editing a dependency must invalidate this build.
        if author_files(ROOT)!=authors_before:
            raise RuntimeError('Authored/runtime files changed during staging; nothing published. Review concurrent edits and rebuild.')
        check_unchanged(ROOT,before,list(before)+[p for p in writes if p not in before])
        rank={name:i for i,name in enumerate((*RUNTIME[:-1],'descriptor.mod','events','docs'))}
        def publish_order(rel):return (rank.get(rel.parts[0],99),str(rel))
        for rel in sorted(writes,key=publish_order):replace_file(stage/rel,ROOT/rel)
        for rel in deletes:(ROOT/rel).unlink()
        runtime_count=sum(p.parts[0] in RUNTIME or p==Path('descriptor.mod') for p in writes)
        print(f'Staged validation passed. Published {runtime_count} changed runtime files and {len(writes)-runtime_count} documentation/report files; unchanged files were not rewritten.')
        print('Hot reload remains enabled. Publication is final-only and atomic per file, not a whole-engine transaction.')


if __name__=='__main__':build()
