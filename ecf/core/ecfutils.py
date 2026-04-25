from __future__ import annotations

import hashlib


def get_hash_key(str_to_hash: str):
    return hashlib.sha1(str_to_hash.encode(), usedforsecurity=True).hexdigest()
