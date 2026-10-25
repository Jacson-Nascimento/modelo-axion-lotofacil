"""Rebuild the checked derivative using archived official spot checks."""
import json
from pathlib import Path

from .core import derive_checked_history

if __name__=='__main__':
    root=Path(__file__).parent/'data'
    edits=derive_checked_history(root/'lotofacil_history.csv',
                                 json.loads((root/'official_spot_checks.json').read_text()),
                                 root/'lotofacil_history_checked.csv')
    print(json.dumps(edits,indent=2,ensure_ascii=False))
