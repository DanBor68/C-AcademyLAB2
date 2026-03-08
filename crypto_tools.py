#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
Ferramentas de apoio ao laboratório de Criptografia com OpenSSL.

Inclui:
  - Hash e HMAC (saída idêntica ao `openssl dgst`)
  - Cifra/decifra simétrica (AES-256-CBC e AES-256-ECB) via OpenSSL
  - Operações de header/body (split, merge, copy binário)
  - Criptografia assimétrica RSA (gerar chaves, assinar, verificar) via OpenSSL

Requisitos:
  - Ter o executável `openssl` acessível no PATH ou indicado por --openssl.

Exemplos rápidos (Windows):

  # HASH (SHA-512)
  python crypto_tools.py hash D:\Lab2\myfile.txt --alg sha512

  # HMAC-SHA512 (chave textual)
  python crypto_tools.py hmac D:\Lab2\myfile.txt --key "mncs12023" --alg sha512

  # Cifrar AES-256-CBC com password
  python crypto_tools.py enc --mode cbc --in D:\Lab2\x.pdf --out D:\Lab2\x.enc --password

  # Decifrar AES-256-CBC com password
  python crypto_tools.py dec --mode cbc --in D:\Lab2\x.enc --out D:\Lab2\x_decrypted.pdf --password

  # Split header/body (ex.: BMP)
  python crypto_tools.py split --in D:\Lab2\p1.bmp --header D:\Lab2\header --body D:\Lab2\body --bytes 54

  # Merge header + body -> new.bmp
  python crypto_tools.py merge --header D:\Lab2\header --body D:\Lab2\body --out D:\Lab2\new.bmp

  # Copy binário (equivalente a comandos head/tail > ficheiros)
  python crypto_tools.py copy --src D:\Lab2\p2.bmp --dst D:\Lab2\p2_copy.bmp --offset 0 --length -1

  # Gerar par de chaves RSA 2048
  python crypto_tools.py rsa-gen --priv D:\Lab2\private-key.pem --pub D:\Lab2\public-key.pem --bits 2048

  # Assinar ficheiro (SHA-256) com a chave privada
  python crypto_tools.py sign --priv D:\Lab2\private-key.pem --in D:\Lab2\x.pdf --sig D:\Lab2\signature.bin --hash sha256

  # Verificar assinatura com a chave pública
  python crypto_tools.py verify --pub D:\Lab2\public-key.pem --in D:\Lab2\x.pdf --sig D:\Lab2\signature.bin --hash sha256
"""

import argparse
import base64
import hashlib
import hmac
import os
import shutil
import subprocess
import sys
from getpass import getpass
from typing import Iterable, Tuple

# ---------- Utilidades comuns ----------

READ_CHUNK = 1024 * 1024  # 1 MiB


def iter_file_chunks(path: str, chunk_size: int = READ_CHUNK) -> Iterable[bytes]:
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            yield data


def get_hash_obj(alg: str):
    alg = alg.lower()
    try:
        if alg in hashlib.algorithms_available:
            return hashlib.new(alg)
    except Exception:
        pass
    mapping = {
        "sha1": hashlib.sha1,
        "sha224": hashlib.sha224,
        "sha256": hashlib.sha256,
        "sha384": hashlib.sha384,
        "sha512": hashlib.sha512,
        "blake2b": hashlib.blake2b,
        "blake2s": hashlib.blake2s,
        "md5": hashlib.md5,  # legado
    }
    if alg in mapping:
        return mappingalg
    raise ValueError(f"Algoritmo '{alg}' não reconhecido/suportado.")


def file_hash(path: str, alg: str = "sha512") -> Tuple[str, str]:
    h = get_hash_obj(alg)
    for chunk in iter_file_chunks(path):
        h.update(chunk)
    return h.hexdigest(), base64.b64encode(h.digest()).decode("ascii")


def file_hmac(path: str, key: bytes, alg: str = "sha512") -> Tuple[str, str]:
    alg = alg.lower()
    hash_funcs = {
        "sha1": hashlib.sha1,
        "sha224": hashlib.sha224,
        "sha256": hashlib.sha256,
        "sha384": hashlib.sha384,
        "sha512": hashlib.sha512,
        "blake2b": hashlib.blake2b,
        "blake2s": hashlib.blake2s,
        "md5": hashlib.md5,
    }
    if alg not in hash_funcs:
        raise ValueError(f"Algoritmo '{alg}' não suportado para HMAC.")
    hm = hmac.new(key, digestmod=hash_funcs[alg])
    for chunk in iter_file_chunks(path):
        hm.update(chunk)
    return hm.hexdigest(), base64.b64encode(hm.digest()).decode("ascii")


def check_file_exists(path: str, label: str = "ficheiro"):
    if not os.path.isfile(path):
        print(f"Erro: {label} não encontrado: {path}", file=sys.stderr)
        sys.exit(2)


def resolve_openssl(path_from_arg: str = None) -> str:
    """
    Resolve o executável do OpenSSL. Tenta:
      1) Argumento --openssl
      2) 'openssl' no PATH
    """
    if path_from_arg:
        return path_from_arg
    exe = shutil.which("openssl")
    if not exe:
        print(
            "Erro: 'openssl' não encontrado no PATH. "
            "Instala o OpenSSL ou usa --openssl <caminho_para_openssl>.",
            file=sys.stderr,
        )
        sys.exit(2)
    return exe


# ---------- Comandos OpenSSL (simétrico e RSA) ----------

def openssl_enc(openssl: str, mode: str, infile: str, outfile: str, password: str, encrypt: bool = True):
    """
    Wrapper para: openssl enc -aes-256-<mode> -in ... -out ... -pass pass:<pwd>
    """
    mode = mode.lower()
    if mode not in ("cbc", "ecb"):
        raise ValueError("Modo inválido. Use 'cbc' ou 'ecb'.")
    cipher = f"aes-256-{mode}"
    cmd = [openssl, "enc", f"-{cipher}", "-in", infile, "-out", outfile, "-pass", f"pass:{password}"]
    if not encrypt:
        cmd.append("-d")
    # Compatível com versões que usam/esperam salt por omissão; podes acrescentar -salt/-nosalt se o professor pedir.
    run_subprocess(cmd, "Falhou cifra/decifra com OpenSSL")


def openssl_rsa_gen(openssl: str, priv_out: str, pub_out: str, bits: int = 2048):
    """
    Gera chave privada e pública:
      openssl genrsa -out private-key.pem 2048
      openssl rsa -in private-key.pem -pubout -out public-key.pem
    """
    run_subprocess([openssl, "genrsa", "-out", priv_out, str(bits)], "Falhou a geração da chave privada RSA")
    run_subprocess([openssl, "rsa", "-in", priv_out, "-pubout", "-out", pub_out], "Falhou a extração da chave pública")


def openssl_sign(openssl: str, priv_key: str, infile: str, sig_out: str, hash_alg: str = "sha256"):
    """
    openssl dgst -<hash> -sign private-key.pem -out signature.bin <ficheiro>
    """
    hash_flag = f"-{hash_alg.lower()}"
    run_subprocess([openssl, "dgst", hash_flag, "-sign", priv_key, "-out", sig_out, infile], "Falhou assinatura")


def openssl_verify(openssl: str, pub_key: str, infile: str, sigfile: str, hash_alg: str = "sha256") -> bool:
    """
    openssl dgst -<hash> -verify public-key.pem -signature signature.bin <ficheiro>
    Retorna True se "Verified OK".
    """
    hash_flag = f"-{hash_alg.lower()}"
    # Precisamos ler stdout/stderr para verificar a mensagem do OpenSSL
    result = run_subprocess(
        [openssl, "dgst", hash_flag, "-verify", pub_key, "-signature", sigfile, infile],
        "Falhou verificação",
        capture_output=True,
        check_rc=False,
    )
    out = (result.stdout or b"") + (result.stderr or b"")
    ok = b"Verified OK" in out
    print(out.decode("utf-8", errors="ignore").strip())
    return ok


def run_subprocess(cmd, err_msg, capture_output=False, check_rc=True):
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            check=False,
        )
        if check_rc and result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        stdout = (e.stdout or b"").decode("utf-8", errors="ignore")
        stderr = (e.stderr or b"").decode("utf-8", errors="ignore")
        print(err_msg, file=sys.stderr)
        if stdout:
            print("stdout:", stdout, file=sys.stderr)
        if stderr:
            print("stderr:", stderr, file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print("Erro: executável não encontrado. Verifica o caminho no comando.", file=sys.stderr)
        sys.exit(2)


# ---------- Operações de header/body/copy ----------

def split_file(infile: str, header_out: str, body_out: str, nbytes: int):
    """
    Divide o ficheiro: primeiros nbytes -> header; resto -> body.
    """
    with open(infile, "rb") as f_in, open(header_out, "wb") as f_h, open(body_out, "wb") as f_b:
        header = f_in.read(nbytes)
        f_h.write(header)
        shutil.copyfileobj(f_in, f_b)


def merge_files(header_file: str, body_file: str, out_file: str):
    """
    Concatena header + body -> out_file.
    """
    with open(out_file, "wb") as f_out, open(header_file, "rb") as f_h, open(body_file, "rb") as f_b:
        shutil.copyfileobj(f_h, f_out)
        shutil.copyfileobj(f_b, f_out)


def copy_binary(src: str, dst: str, offset: int = 0, length: int = -1):
    """
    Copia bytes do ficheiro `src` para `dst`, a partir de `offset`.
    Se length=-1, copia até ao fim.
    """
    with open(src, "rb") as f_src, open(dst, "wb") as f_dst:
        if offset > 0:
            f_src.seek(offset)
        if length is None or length < 0:
            shutil.copyfileobj(f_src, f_dst)
        else:
            remaining = length
            while remaining > 0:
                chunk = f_src.read(min(READ_CHUNK, remaining))
                if not chunk:
                    break
                f_dst.write(chunk)
                remaining -= len(chunk)


# ---------- CLI ----------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ferramentas para o lab de Criptografia com OpenSSL")
    parser.add_argument("--openssl", help="Caminho para o executável openssl (se não estiver no PATH).")

    sub = parser.add_subparsers(dest="cmd")

    # hash
    p_hash = sub.add_parser("hash", help="Calcula hash (saída estilo OpenSSL).")
    p_hash.add_argument("file", help="Ficheiro de entrada.")
    p_hash.add_argument("--alg", default="sha512", help="Algoritmo (sha256, sha512, ...).")
    p_hash.add_argument("--show-base64", action="store_true", help="Também imprime Base64.")

    # hmac
    p_hmac = sub.add_parser("hmac", help="Calcula HMAC (saída estilo OpenSSL).")
    p_hmac.add_argument("file", help="Ficheiro de entrada.")
    p_hmac.add_argument("--key", required=True, help="Chave (texto). Para hex, usa --key-hex.")
    p_hmac.add_argument("--key-hex", action="store_true", help="Interpreta a chave como hexadecimal.")
    p_hmac.add_argument("--alg", default="sha512", help="Algoritmo (sha256, sha512, ...).")
    p_hmac.add_argument("--show-base64", action="store_true", help="Também imprime Base64.")

    # enc (cifra) e dec (decifra)
    for name, encrypt in (("enc", True), ("dec", False)):
        p = sub.add_parser(name, help=("Cifrar" if encrypt else "Decifrar") + " com AES-256-(CBC|ECB) via OpenSSL.")
        p.add_argument("--mode", choices=["cbc", "ecb"], required=True, help="Modo de operação AES-256.")
        p.add_argument("--in", dest="infile", required=True, help="Ficheiro de entrada.")
        p.add_argument("--out", dest="outfile", required=True, help="Ficheiro de saída.")
        pw = p.add_mutually_exclusive_group(required=True)
        pw.add_argument("--password", action="store_true", help="Pergunta a password interativamente.")
        pw.add_argument("--pass", dest="pass_inline", help="Password inline (atenção ao histórico do shell).")

    # split/merge/copy (modos de operação)
    p_split = sub.add_parser("split", help="Divide ficheiro em header/body (primeiros N bytes).")
    p_split.add_argument("--in", dest="infile", required=True)
    p_split.add_argument("--header", required=True)
    p_split.add_argument("--body", required=True)
    p_split.add_argument("--bytes", type=int, required=True, help="Número de bytes do header (ex.: 54 para BMP).")

    p_merge = sub.add_parser("merge", help="Junta header+body em novo ficheiro.")
    p_merge.add_argument("--header", required=True)
    p_merge.add_argument("--body", required=True)
    p_merge.add_argument("--out", required=True)

    p_copy = sub.add_parser("copy", help="Copia intervalo de bytes (binário).")
    p_copy.add_argument("--src", required=True)
    p_copy.add_argument("--dst", required=True)
    p_copy.add_argument("--offset", type=int, default=0, help="Offset inicial (default 0).")
    p_copy.add_argument("--length", type=int, default=-1, help="Comprimento; -1 até ao fim.")

    # rsa-gen
    p_rsa = sub.add_parser("rsa-gen", help="Gera par de chaves RSA.")
    p_rsa.add_argument("--priv", required=True, help="Caminho para private-key.pem")
    p_rsa.add_argument("--pub", required=True, help="Caminho para public-key.pem")
    p_rsa.add_argument("--bits", type=int, default=2048, help="Tamanho (default 2048).")

    # sign
    p_sign = sub.add_parser("sign", help="Assina ficheiro com chave privada (OpenSSL).")
    p_sign.add_argument("--priv", required=True, help="private-key.pem")
    p_sign.add_argument("--in", dest="infile", required=True)
    p_sign.add_argument("--sig", required=True, help="signature.bin")
    p_sign.add_argument("--hash", default="sha256", help="Algoritmo de hash (sha256, sha384, sha512...).")

    # verify
    p_verify = sub.add_parser("verify", help="Verifica assinatura com chave pública (OpenSSL).")
    p_verify.add_argument("--pub", required=True, help="public-key.pem")
    p_verify.add_argument("--in", dest="infile", required=True)
    p_verify.add_argument("--sig", required=True, help="signature.bin")
    p_verify.add_argument("--hash", default="sha256", help="Algoritmo de hash (sha256, sha384, sha512...).")

    return parser


def parse_args_with_autohash(argv=None) -> argparse.Namespace:
    raw = list(sys.argv[1:] if argv is None else argv)
    if raw and raw[0] not in ("hash", "hmac", "enc", "dec", "split", "merge", "copy", "rsa-gen", "sign", "verify", "-h", "--help"):
        # Conveniência: se o primeiro argumento parece um ficheiro, assume 'hash'
        raw = ["hash"] + raw
    parser = build_parser()
    return parser.parse_args(raw)


def main(argv=None):
    args = parse_args_with_autohash(argv)

    if args.cmd in {"hash", "hmac", "split", "merge", "copy", "sign", "verify", "enc", "dec", "rsa-gen"}:
        pass
    else:
        build_parser().print_help()
        sys.exit(2)

    try:
        if args.cmd == "hash":
            check_file_exists(args.file)
            digest_hex, digest_b64 = file_hash(args.file, args.alg)
            alg_upper = args.alg.upper()
            print(f"{alg_upper}({args.file})= {digest_hex}")
            if getattr(args, "show_base64", False):
                print(f"{alg_upper}_BASE64({args.file})= {digest_b64}")

        elif args.cmd == "hmac":
            check_file_exists(args.file)
            if args.key_hex:
                try:
                    key_bytes = bytes.fromhex(args.key)
                except ValueError:
                    print("Erro: --key-hex fornecido mas a chave não é hex válido.", file=sys.stderr)
                    sys.exit(2)
            else:
                key_bytes = args.key.encode("utf-8")
            digest_hex, digest_b64 = file_hmac(args.file, key_bytes, args.alg)
            alg_upper = args.alg.upper()
            print(f"HMAC-{alg_upper}({args.file})= {digest_hex}")
            if getattr(args, "show_base64", False):
                print(f"HMAC-{alg_upper}_BASE64({args.file})= {digest_b64}")

        elif args.cmd in ("enc", "dec"):
            openssl = resolve_openssl(args.openssl)
            check_file_exists(args.infile, "entrada")
            # password
            if args.password:
                pwd = getpass("Password: ")
            else:
                pwd = args.pass_inline or ""
            encrypt = (args.cmd == "enc")
            openssl_enc(openssl, args.mode, args.infile, args.outfile, pwd, encrypt=encrypt)
            print(f"OK: {'Cifrado' if encrypt else 'Decifrado'} -> {args.outfile}")

        elif args.cmd == "split":
            check_file_exists(args.infile, "entrada")
            if args.bytes <= 0:
                print("Erro: --bytes tem de ser > 0 (ex.: 54 para BMP).", file=sys.stderr)
                sys.exit(2)
            split_file(args.infile, args.header, args.body, args.bytes)
            print(f"OK: header -> {args.header} ; body -> {args.body}")

        elif args.cmd == "merge":
            check_file_exists(args.header, "header")
            check_file_exists(args.body, "body")
            merge_files(args.header, args.body, args.out)
            print(f"OK: gerado -> {args.out}")

        elif args.cmd == "copy":
            check_file_exists(args.src, "src")
            copy_binary(args.src, args.dst, args.offset, args.length)
            print(f"OK: cópia binária -> {args.dst}")

        elif args.cmd == "rsa-gen":
            openssl = resolve_openssl(args.openssl)
            openssl_rsa_gen(openssl, args.priv, args.pub, args.bits)
            print(f"OK: chaves geradas -> {args.priv} (priv), {args.pub} (pub)")

        elif args.cmd == "sign":
            openssl = resolve_openssl(args.openssl)
            check_file_exists(args.priv, "chave privada")
            check_file_exists(args.infile, "entrada")
            openssl_sign(openssl, args.priv, args.infile, args.sig, args.hash)
            print(f"OK: assinatura -> {args.sig}")

        elif args.cmd == "verify":
            openssl = resolve_openssl(args.openssl)
            check_file_exists(args.pub, "chave pública")
            check_file_exists(args.infile, "entrada")
            check_file_exists(args.sig, "assinatura")
            ok = openssl_verify(openssl, args.pub, args.infile, args.sig, args.hash)
            # A função já imprime "Verified OK" ou "Verification Failure"
            sys.exit(0 if ok else 1)

    except ValueError as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"Erro de E/S: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()