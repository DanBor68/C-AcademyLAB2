# client_todo.py
import socket
import sys

HOST = "127.0.0.1"   # tem de corresponder ao servidor
PORT = 8888

def send(cmd: str) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        # recebe banner
        s.recv(4096)
        s.sendall((cmd.strip() + "\n").encode("utf-8"))
        data = s.recv(1_000_000)
        return data.decode("utf-8", errors="ignore")

def shell():
    print(f"Cliente ligado a {HOST}:{PORT}. Escreve HELP para ajuda. CTRL+C para sair.")
    while True:
        try:
            cmd = input("> ").strip()
            if not cmd:
                continue
            out = send(cmd)
            print(out, end="")
            if out.startswith("BYE"):
                break
        except (EOFError, KeyboardInterrupt):
            print("\nA sair…")
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(send(" ".join(sys.argv[1:])), end="")
    else:
        shell()
