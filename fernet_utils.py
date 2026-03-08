#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilitários para cifrar/decifrar dados e ficheiros usando cryptography.fernet.
- load_key / create_fernet
- encrypt_bytes / decrypt_bytes
- encrypt_json_to_file / decrypt_json_from_file
"""

import json
import os
from pathlib import Path
from typing import Any, Dict
from cryptography.fernet import Fernet, InvalidToken

def load_key(key_file: os.PathLike | str) -> bytes:
    key_path = Path(key_file)
    if not key_path.is_file():
        raise FileNotFoundError(f"Ficheiro de chave não encontrado: {key_path}")
    key = key_path.read_bytes().strip()
    if not key:
        raise ValueError(f"Ficheiro de chave vazio: {key_path}")
    return key

def create_fernet(key_file: os.PathLike | str) -> Fernet:
    key = load_key(key_file)
    return Fernet(key)

def encrypt_bytes(data: bytes, key_file: os.PathLike | str) -> bytes:
    f = create_fernet(key_file)
    return f.encrypt(data)

def decrypt_bytes(token: bytes, key_file: os.PathLike | str) -> bytes:
    f = create_fernet(key_file)
    try:
        return f.decrypt(token)
    except InvalidToken as e:
        raise ValueError("Token inválido ou chave incorreta ao decifrar.") from e

def encrypt_json_to_file(obj: Any, data_file: os.PathLike | str, key_file: os.PathLike | str) -> None:
    """
    Serializa obj em JSON (UTF-8), cifra com Fernet e grava em data_file de forma atómica.
    """
    data_path = Path(data_file)
    plaintext = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    token = encrypt_bytes(plaintext, key_file)
    tmp = data_path.with_suffix(data_path.suffix + ".tmp")
    tmp.write_bytes(token)
    os.replace(tmp, data_path)  # gravação atómica
    # Opcional: garantir permissões restritas em *nix
    try:
        os.chmod(data_path, 0o600)
    except PermissionError:
        pass

def decrypt_json_from_file(data_file: os.PathLike | str, key_file: os.PathLike | str) -> Any:
    """
    Lê data_file, decifra com Fernet e devolve o JSON como objeto Python.
    """
    data_path = Path(data_file)
    token = data_path.read_bytes()
    plaintext = decrypt_bytes(token, key_file)
    return json.loads(plaintext.decode("utf-8"))