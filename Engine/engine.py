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

    def get_best_move(self, moves_str, movetime_ms=None, wtime=None, btime=None, winc=None, binc=None):
        if moves_str:
            self.send(f"position startpos moves {moves_str}")
        else:
            self.send("position startpos")

        if wtime is not None and btime is not None:
            use_winc = 0 if winc is None else int(winc)
            use_binc = 0 if binc is None else int(binc)
            self.send(f"go wtime {int(wtime)} btime {int(btime)} winc {use_winc} binc {use_binc}")
        else:
            effective_movetime = self.movetime_ms if movetime_ms is None else int(movetime_ms)
            self.send(f"go movetime {max(1, effective_movetime)}")

        while True:
            line = self.process.stdout.readline()
            if "bestmove" in line:
                return line.split()[1]
