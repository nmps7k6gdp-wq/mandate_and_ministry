"""Small publication regressions; no CK3 process is launched or modified."""
from pathlib import Path
import hashlib
import runpy
import tempfile
import os

ROOT=Path(__file__).resolve().parents[1]
helpers=runpy.run_path(str(ROOT/'tools/stage_common_fund.py'))


def verify():
    changes=helpers['changes'];replace=helpers['replace_file'];check=helpers['check_unchanged']
    p=Path('events/example.txt')
    assert changes({p:'same'},{p:'same'})==([],[]), 'No-op builds must not trigger script reload'
    assert changes({p:'old'},{p:'new'})==([p],[]), 'One final change, not intermediate generator outputs'
    assert changes({p:'old'}, {})==([],[]), 'Missing stage input must not delete authored scripts'
    parent=Path(os.environ.get('MAM_BUILD_STAGING_DIR',tempfile.gettempdir())).resolve()
    parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='mam-publish-test-',dir=parent) as name:
        work=Path(name).resolve()
        assert work.parent==parent and work.name.startswith('mam-publish-test-')
        source=work/'source.txt';destination=work/'destination.txt'
        source.write_bytes(b'\xef\xbb\xbfcomplete final script\n');destination.write_bytes(b'old script')
        replace(source,destination)
        assert destination.read_bytes()==source.read_bytes()
        assert not list(work.glob('.mam-publish-*')), 'Temporary publication files leaked'
        before={Path('destination.txt'):hashlib.sha256(destination.read_bytes()).hexdigest()}
        check(work,before,[Path('destination.txt')])
        destination.write_bytes(b'concurrent edit')
        try:check(work,before,[Path('destination.txt')])
        except RuntimeError:pass
        else:raise AssertionError('Concurrent author changes must stop publication')
    print('PASS: no-op filtering, final-only change planning, atomic file replacement, cleanup and concurrent-edit refusal.')
    print('NOT TESTED: CK3 live-reload safety or the cause of an engine pure-virtual crash.')


if __name__=='__main__':verify()
