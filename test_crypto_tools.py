#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testes para crypto_tools.py (hash e HMAC) 100% em Python.

O que faz:
- Cria ficheiros de teste (vazio, 'abc', myfile.txt, random.bin 1MiB).
- Calcula os resultados com o teu crypto_tools.py (formato OpenSSL).
- Valida contra vetores conhecidos (NIST/RFC) para ficheiros pequenos.
- (Opcional) Se 'openssl' estiver no PATH, compara também com ele.
"""

from __future__ import annotations

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Tuple

# --- Configuração ---------------------------------------------

LAB_DIR = Path(r"D:\Lab2")            # pasta do teu lab
TOOL = LAB_DIR / "crypto_tools.py"    # caminho do teu script

# Vetores conhecidos (hex) — SHA-512
V_SHA512_EMPTY = (
    "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce"
    "47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
)

V_SHA512_ABC = (
    "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a"
    "2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f"
)

# Vetor conhecido (hex) — HMAC-SHA512("abc", key="key")
V_HMAC_SHA512_KEY_ABC = (
    "b42af09057bac1e2d41708e48a902e09b5ff7f12ab428a4fe86653c73dd248fb"
    "82f948a549f7b791a5b41915ee4d1ec3935357e4e2317250d0372afa2ebeeb3a"
)

# Chaves para testes extra
KEY_TEXT = "mncs12023"
KEY_HEX = "00112233aabbccddeeff"

# ---------------------------------------------------------------


def parse_hex_from_output(line: str) -> str:
    """
    Extrai o hex da última linha no formato OpenSSL:
    'SHA512(caminho)= <hex>' ou 'HMAC-SHA512(caminho)= <hex>'
    """
    if "=" not in line:
        raise ValueError(f"Não encontrei '=' na linha: {line!r}")
    return line.split("=", 1)[1].strip().lower()


def run_tool_hash(file_path: Path, alg: str = "sha512") -> Tuple[int, str, str]:
    args = [sys.executable, str(TOOL), "hash", str(file_path), "--alg", alg]
    r = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def run_tool_hmac(file_path: Path, key: str, alg: str = "sha512", key_hex: bool = False) -> Tuple[int, str, str]:
    args = [sys.executable, str(TOOL), "hmac", str(file_path), "--alg", alg, "--key", key]
    if key_hex:
        args.append("--key-hex")
    r = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def run_openssl_hash(file_path: Path, alg: str = "sha512") -> Tuple[int, str, str]:
    """
    Tenta correr 'openssl dgst -sha512 <ficheiro>' se existir no PATH.
    Caso não exista, devolve returncode=127.
    """
    if shutil.which("openssl") is None:
        return 127, "", "openssl não encontrado no PATH"
    args = ["openssl", "dgst", f"-{alg}", str(file_path)]
    r = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def ensure_lab_files() -> dict[str, Path]:
    LAB_DIR.mkdir(parents=True, exist_ok=True)
    files = {}

    # 1) vazio
    empty = LAB_DIR / "empty.bin"
    empty.write_bytes(b"")
    files["empty"] = empty

    # 2) abc (sem newline)
    abc = LAB_DIR / "abc.txt"
    abc.write_bytes(b"abc")
    files["abc"] = abc

    # 3) myfile.txt (se não existir, cria)
    myfile = LAB_DIR / "myfile.txt"
    if not myfile.exists():
        myfile.write_text("Este e um ficheiro de teste.\nSegunda linha.\n", encoding="utf-8")
    files["myfile"] = myfile

    # 4) random.bin (1 MiB)
    rand = LAB_DIR / "random.bin"
    rand.write_bytes(os.urandom(1024 * 1024))
    files["random"] = rand

    return files


def assert_eq(label: str, got: str, exp: str, failures: list[str]) -> None:
    if got == exp:
        print(f"PASS {label}")
    else:
        print(f"FAIL {label}")
        print(f"  got: {got}")
        print(f"  exp: {exp}")
        failures.append(label)


def main() -> int:
    failures: list[str] = []

    # Verificações iniciais
    if not TOOL.exists():
        print(f"ERRO: Não encontrei o teu script: {TOOL}")
        return 2

    print("== Preparar ficheiros de teste ==")
    files = ensure_lab_files()
    for k, p in files.items():
        print(f"  - {k}: {p}")

    print("\n== Vetores conhecidos (sem OpenSSL) ==")

    # SHA-512 vazio
    rc, out, err = run_tool_hash(files["empty"], "sha512")
    if rc != 0:
        print("ERRO ao calcular hash vazio:", err or out)
        return 2
    got = parse_hex_from_output(out.splitlines()[-1])
    assert_eq("hash sha512 (ficheiro vazio)", got, V_SHA512_EMPTY, failures)

    # SHA-512 'abc'
    rc, out, err = run_tool_hash(files["abc"], "sha512")
    if rc != 0:
        print("ERRO ao calcular hash abc:", err or out)
        return 2
    got = parse_hex_from_output(out.splitlines()[-1])
    assert_eq("hash sha512 ('abc')", got, V_SHA512_ABC, failures)

    # HMAC-SHA512('abc', key='key')
    rc, out, err = run_tool_hmac(files["abc"], key="key", alg="sha512")
    if rc != 0:
        print("ERRO ao calcular HMAC:", err or out)
        return 2
    got = parse_hex_from_output(out.splitlines()[-1])
    assert_eq("hmac sha512 ('abc','key')", got, V_HMAC_SHA512_KEY_ABC, failures)

    print("\n== Testes adicionais (myfile.txt e random.bin) ==")
    # Apenas executa e mostra a saída (não há vetor 'esperado' aqui)
    for label in ("myfile", "random"):
        fpath = files[label]
        rc, out, err = run_tool_hash(fpath, "sha512")
        if rc != 0:
            print(f"ERRO hash {label}:", err or out)
            failures.append(f"hash {label}")
        else:
            print(out.splitlines()[-1])

        rc, out, err = run_tool_hmac(fpath, key=KEY_TEXT, alg="sha512")
        if rc != 0:
            print(f"ERRO hmac (key texto) {label}:", err or out)
            failures.append(f"hmac texto {label}")
        else:
            print(out.splitlines()[-1])

        rc, out, err = run_tool_hmac(fpath, key=KEY_HEX, alg="sha512", key_hex=True)
        if rc != 0:
            print(f"ERRO hmac (key hex) {label}:", err or out)
            failures.append(f"hmac hex {label}")
        else:
            print(out.splitlines()[-1])

    print("\n== (Opcional) Comparação com OpenSSL, se disponível ==")
    rc, _, _ = run_openssl_hash(files["empty"])
    if rc == 127:
        print("OpenSSL não encontrado no PATH — a comparação será ignorada.")
    else:
        # Compara empty e abc com openssl (se existir)
        for label in ("empty", "abc"):
            fpath = files[label]
            rc1, py_out, _ = run_tool_hash(fpath, "sha512")
            rc2, ssl_out, ssl_err = run_openssl_hash(fpath, "sha512")
            if rc1 != 0 or rc2 != 0:
                print(f"ERRO comparar com openssl [{label}]:", ssl_err or "")
                failures.append(f"openssl {label}")
                continue
            py_hex = parse_hex_from_output(py_out.splitlines()[-1])
            # Saída do openssl já vem no formato 'SHA256(file)= hex'
            ssl_hex = parse_hex_from_output(ssl_out.splitlines()[-1])
            if py_hex == ssl_hex:
                print(f"PASS openssl vs python (hash) -> {label}")
            else:
                print(f"FAIL openssl vs python (hash) -> {label}")
                print(f"  py : {py_hex}")
                print(f"  ssl: {ssl_hex}")
                failures.append(f"openssl {label}")

    if failures:
        print("\n❌ Algumas verificações falharam:", ", ".join(failures))
        return 1
    print("\n✅ Todos os testes PASSARAM.")
    return 0


if __name__ == "__main__":
    sys.exit(main())