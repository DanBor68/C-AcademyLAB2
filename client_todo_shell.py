#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import shlex
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def call(method: str, url: str, data: dict | None = None):
    body = None
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req) as resp:
            content = resp.read()
            if not content:
                return resp.status, None
            return resp.status, json.loads(content.decode("utf-8"))
    except HTTPError as e:
        try:
            err = e.read().decode("utf-8")
            return e.code, json.loads(err)
        except Exception:
            return e.code, {"error": str(e)}
    except URLError as e:
        return 0, {"error": str(e)}

def print_help():
    print("""Comandos:
  help                      — mostra esta ajuda
  list                      — lista tarefas
  add "texto da tarefa"     — cria tarefa
  done <id>                 — marca concluída (completed=true)
  undone <id>               — marca não concluída (completed=false)
  title <id> "novo título"  — altera o título
  del <id>                  — apaga
  quit                      — sair
""")

def main():
    p = argparse.ArgumentParser(description="Shell HTTP para o servidor TODO cifrado (Fernet).")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", default=8080, type=int)
    args = p.parse_args()
    base = f"http://{args.host}:{args.port}"

    print(f"Cliente ligado a {base}. Escreve HELP para ajuda. CTRL+C para sair.")
    print_help()

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        parts = shlex.split(line)
        if not parts:
            continue
        cmd = parts[0].lower()

        if cmd in ("help", "?"):
            print_help()
            continue
        if cmd in ("quit", "exit"):
            break

        if cmd == "list":
            code, obj = call("GET", f"{base}/todos")
            print(code, obj)
            continue

        if cmd == "add":
            if len(parts) < 2:
                print("uso: add \"texto da tarefa\"")
                continue
            title = parts[1]
            code, obj = call("POST", f"{base}/todos", {"title": title})
            print(code, obj)
            continue

        if cmd == "done" and len(parts) == 2 and parts[1].isdigit():
            tid = int(parts[1])
            code, obj = call("PATCH", f"{base}/todos/{tid}", {"completed": True})
            print(code, obj)
            continue

        if cmd == "undone" and len(parts) == 2 and parts[1].isdigit():
            tid = int(parts[1])
            code, obj = call("PATCH", f"{base}/todos/{tid}", {"completed": False})
            print(code, obj)
            continue

        if cmd == "title" and len(parts) >= 3 and parts[1].isdigit():
            tid = int(parts[1])
            new_title = parts[2]
            code, obj = call("PATCH", f"{base}/todos/{tid}", {"title": new_title})
            print(code, obj)
            continue

        if cmd == "del" and len(parts) == 2 and parts[1].isdigit():
            tid = int(parts[1])
            code, obj = call("DELETE", f"{base}/todos/{tid}")
            print(code, obj)
            continue

        print("Comando inválido. Escreve HELP para ajuda.")

if __name__ == "__main__":
    main()