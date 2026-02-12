import subprocess

class UCIEngine:
    def __init__(self, engine_path, movetime_ms=100, uci_options=None):
        self.process = subprocess.Popen(
            engine_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.movetime_ms = movetime_ms
        self.uci_options = uci_options or {}

        self.send("uci")
        for option_name, option_value in self.uci_options.items():
            self.send(f"setoption name {option_name} value {option_value}")
        self.send("isready")

    def send(self, cmd):
        self.process.stdin.write(f"{cmd}\n")
        self.process.stdin.flush()

    def get_best_move(self, moves_str):
        if moves_str:
            self.send(f"position startpos moves {moves_str}")
        else:
            self.send("position startpos")
        self.send(f"go movetime {self.movetime_ms}")
        while True:
            line = self.process.stdout.readline()
            if "bestmove" in line:
                return line.split()[1]
