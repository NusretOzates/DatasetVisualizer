"""Decrypt Groq/mtob ciphertext fields for inspection."""

from __future__ import annotations

import os
from base64 import b64decode

from Crypto.Cipher import AES

DEFAULT_MTOB_KEY = "mtob-eval-encode"


def mtob_decrypt_key() -> bytes:
    """Return the AES key used by the public Groq/mtob Hub dataset."""
    raw = os.getenv("MTOB_KEY", DEFAULT_MTOB_KEY).strip()
    if not raw:
        msg = "MTOB_KEY is empty; cannot decrypt MTOB samples"
        raise ValueError(msg)
    return raw.encode("utf-8")


def decrypt_mtob_text(nonce: str, ciphertext: str, *, key: bytes | None = None) -> str:
    """Decrypt a single MTOB AES-CTR field pair."""
    aes_key = key if key is not None else mtob_decrypt_key()
    cipher = AES.new(aes_key, AES.MODE_CTR, nonce=b64decode(nonce))
    return cipher.decrypt(b64decode(ciphertext)).decode("utf-8")
