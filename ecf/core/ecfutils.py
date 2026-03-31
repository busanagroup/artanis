from __future__ import annotations

import hashlib


def get_hash_key(str_to_hash: str):
    digest = hashlib.sha1(usedforsecurity=True)
    bytes_str = str_to_hash.encode()
    digest.update(bytes_str)
    return digest.hexdigest()
