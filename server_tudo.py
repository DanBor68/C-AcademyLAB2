# server_todo.py
import socket
import threading

HOST = "127.0.0.1"   # altera se quiseres aceitar fora da máquina local
PORT = 5555          # escolhe uma porta livre e usa a mesma no cliente

# Estrutura simples em memória; persistência não é pedida na alínea 1
tasks = []  # cada item: {"id": int, "text": str, "done": bool}
_next_id = 1
lock = threading.Lock()

HELP = (
    "Comandos:\n"
    "  ADD <texto da tarefa>\n"
    "  LIST\n"
    "  DONE <id>\n"
    "  COUNT            (total de itens)\n"
    "  COUNT_OPEN       (itens não concluídos)\n"
    "  CLEAR            (apaga TODAS as tarefas)\n"
    "  QUIT\n"
)

def handle_cmd(cmdline: str) -> str:
    global _next_id
    parts = cmdline.strip().split(" ", 1)
    if not parts or not parts[0]:
        return "ERR comando vazio\n"
    cmd = parts[0].upper()

    if cmd == "ADD":
        if len(parts) < 2 or not parts[1].strip():
            return "ERR uso: ADD <texto>\n"
        text = parts[1].strip()
        with lock:
            global tasks
            tid = _next_id
            _next_id += 1
            tasks.append({"id": tid, "text": text, "done": False})
        return f"OK added id={tid}\n"

    if cmd == "LIST":
        with lock:
            if not tasks:
                return "OK (vazio)\n"
            lines = []
            for t in tasks:
                status = "✓" if t["done"] else " "
                lines.append(f"[{status}] {t['id']}: {t['text']}")
        return "OK\n" + "\n".join(lines) + "\n"

    if cmd == "DONE":
        if len(parts) < 2 or not parts[1].isdigit():
            return "ERR uso: DONE <id>\n"
        tid = int(parts[1])
        with lock:
            for t in tasks:
                if t["id"] == tid:
                    t["done"] = True
                    return f"OK done id={tid}\n"
        return "ERR id não encontrado\n"

    if cmd == "COUNT":
        with lock:
            return f"OK total={len(tasks)}\n"

    if cmd == "COUNT_OPEN":
        with lock:
            open_count = sum(1 for t in tasks if not t["done"])
            return f"OK abertas={open_count}\n"

    if cmd == "CLEAR":
        with lock:
            tasks.clear()
        return "OK cleared\n"

    if cmd in ("HELP", "?"):
        return HELP

    if cmd == "QUIT":
        return "BYE\n"

    return "ERR comando desconhecido. Use HELP\n"

def client_thread(conn: socket.socket, addr):
    with conn:
        conn.sendall(b"TodoServer pronto. Use HELP\n")
        while True:
            data = b""
            while not data.endswith(b"\n"):
                chunk = conn.recv(4096)
                if not chunk:
                    return
                data += chunk
            resp = handle_cmd(data.decode("utf-8", errors="ignore"))
            conn.sendall(resp.encode("utf-8"))
            if resp.startswith("BYE"):
                return

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"Servidor escutar em {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            print("Cliente ligado:", addr)
            threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
