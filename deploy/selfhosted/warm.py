import sys

from modal.server import Server

SERVERS = {
    "llm": ("cybercase-llm", "Llm", 2.50),
    "ocr": ("cybercase-ocr", "Ocr", 0.80),
}
USAGE = "usage: python deploy/selfhosted/warm.py up|down [llm] [ocr]"


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    names = sys.argv[2:] or list(SERVERS)
    if action not in ("up", "down") or any(name not in SERVERS for name in names):
        raise SystemExit(USAGE)
    for name in names:
        app_name, server_name, hourly = SERVERS[name]
        server = Server.from_name(app_name, server_name)
        server.update_autoscaler(min_containers=1 if action == "up" else 0)
        if action == "up":
            print(f"{name}: one container kept running, about ${hourly:.2f} an hour until 'down'")
        else:
            print(f"{name}: scales to zero again")


if __name__ == "__main__":
    main()
