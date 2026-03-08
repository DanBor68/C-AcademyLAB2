#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gera uma chave Fernet e grava-a num ficheiro (por omissão: fernet.key).

Uso:
  python fernet_keygen.py               # cria fernet.key no diretório atual
  python fernet_keygen.py --out my.key  # cria my.key
"""

import argparse
from pathlib import Path
from cryptography.fernet import Fernet

def main():
    parser = argparse.ArgumentParser(description="Gerar chave Fernet e gravar em ficheiro.")
    parser.add_argument("--out", default="fernet.key", help="Caminho do ficheiro de chave. Omissão: fernet.key")
    args = parser.parse_args()

    key = Fernet.generate_key()
    out_path = Path(args.out)
    out_path.write_bytes(key)
    print(f"✅ Chave Fernet gerada e gravada em: {out_path.resolve()}")

if __name__ == "__main__":
    main()