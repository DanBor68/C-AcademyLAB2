# client_test.py
import requests
import sys

SERVER = "http://127.0.0.1:5000"

def test_add(task: str):
    print(f"-> POST {SERVER}/add  body={{'task': {task!r}}}")
    r = requests.post(f"{SERVER}/add", json={"task": task})
    print("<- status:", r.status_code)
    print("<- body  :", r.text)
    try:
        print("<- json  :", r.json())
    except Exception:
        pass
    print()

def test_list():
    print(f"-> GET  {SERVER}/list")
    r = requests.get(f"{SERVER}/list")
    print("<- status:", r.status_code)
    print("<- body  :", r.text)
    try:
        print("<- json  :", r.json())
    except Exception:
        pass
    print()

if __name__ == "__main__":
    print("=== start client_test.py ===")
    try:
        test_add("Comprar pão")
        test_add("Preparar aula de GP")
        test_list()
    except Exception as e:
        print("!! Exception:", repr(e), file=sys.stderr)
        raise
    finally:
        print("=== end client_test.py ===")