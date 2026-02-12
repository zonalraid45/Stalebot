import json
import threading
import sys


def initial_board():
    board = {}
    for file_char in "abcdefgh":
        board[f"{file_char}2"] = "P"
        board[f"{file_char}7"] = "p"
    board.update(
        {
            "a1": "R",
            "b1": "N",
            "c1": "B",
            "d1": "Q",
            "e1": "K",
            "f1": "B",
            "g1": "N",
            "h1": "R",
            "a8": "r",
            "b8": "n",
            "c8": "b",
            "d8": "q",
            "e8": "k",
            "f8": "b",
            "g8": "n",
            "h8": "r",
        }
    )
    return board


def uci_to_pretty(move, board):
    from_sq = move[:2]
    to_sq = move[2:4]
    promotion = move[4] if len(move) > 4 else ""
    piece = board.get(from_sq, "")

    if piece in {"K", "k"} and from_sq == "e1" and to_sq == "g1":
        return "o-o"
    if piece in {"K", "k"} and from_sq == "e1" and to_sq == "c1":
        return "o-o-o"
    if piece in {"K", "k"} and from_sq == "e8" and to_sq == "g8":
        return "o-o"
    if piece in {"K", "k"} and from_sq == "e8" and to_sq == "c8":
        return "o-o-o"

    piece_letter = ""
    if piece and piece.lower() != "p":
        piece_letter = piece.lower()

    capture = "x" if to_sq in board else ""

    if piece and piece.lower() == "p" and capture:
        notation = f"{from_sq[0]}x{to_sq}"
    else:
        notation = f"{piece_letter}{capture}{to_sq}"

    if promotion:
        notation = f"{notation}={promotion.lower()}"

    return notation


def apply_uci_move(board, move):
    from_sq = move[:2]
    to_sq = move[2:4]
    promotion = move[4] if len(move) > 4 else ""
    piece = board.get(from_sq)
    if not piece:
        return

    if piece in {"K", "k"} and from_sq == "e1" and to_sq == "g1":
        board["g1"] = piece
        board.pop("e1", None)
        rook = board.pop("h1", None)
        if rook:
            board["f1"] = rook
        return
    if piece in {"K", "k"} and from_sq == "e1" and to_sq == "c1":
        board["c1"] = piece
        board.pop("e1", None)
        rook = board.pop("a1", None)
        if rook:
            board["d1"] = rook
        return
    if piece in {"K", "k"} and from_sq == "e8" and to_sq == "g8":
        board["g8"] = piece
        board.pop("e8", None)
        rook = board.pop("h8", None)
        if rook:
            board["f8"] = rook
        return
    if piece in {"K", "k"} and from_sq == "e8" and to_sq == "c8":
        board["c8"] = piece
        board.pop("e8", None)
        rook = board.pop("a8", None)
        if rook:
            board["d8"] = rook
        return

    if piece.lower() == "p" and from_sq[0] != to_sq[0] and to_sq not in board:
        capture_rank = str(int(to_sq[1]) - 1) if piece == "P" else str(int(to_sq[1]) + 1)
        board.pop(f"{to_sq[0]}{capture_rank}", None)

    board.pop(from_sq, None)
    board.pop(to_sq, None)

    if promotion and piece.lower() == "p":
        board[to_sq] = promotion.upper() if piece.isupper() else promotion.lower()
    else:
        board[to_sq] = piece


def format_result(status, winner):
    winner_text = "White" if winner == "white" else "Black" if winner == "black" else "No one"
    loser_text = "Black" if winner == "white" else "White" if winner == "black" else "No one"

    if status == "resign" and winner in {"white", "black"}:
        return f"{loser_text} resigned, {winner_text.lower()} is victorious (win)"
    if status == "mate" and winner in {"white", "black"}:
        return f"Checkmate, {winner_text.lower()} is victorious (win)"
    if status == "timeout" and winner in {"white", "black"}:
        return f"{loser_text} flagged on time, {winner_text.lower()} is victorious (win)"
    if status == "draw":
        return "Game drawn"
    if status == "stalemate":
        return "Stalemate, game drawn"
    if status == "aborted":
        return "Game aborted"

    if winner in {"white", "black"}:
        return f"Game finished, {winner_text.lower()} is victorious (win)"
    return f"Game finished with status: {status}"


def play_game(game_id, api, bot_name, engine, max_takebacks, on_game_finish=None):
    print(f"Starting game loop for {game_id}")
    board = initial_board()
    processed_plies = 0
    announced = False
    opponent_name = "unknown"
    bot_is_white = None
    takebacks_accepted = 0
    takeback_offer_seen = False

    try:
        for line in api.stream_game(game_id).iter_lines(chunk_size=1):
            if not line:
                continue

            data = json.loads(line.decode("utf-8"))

            if data.get("type") == "gameFull":
                white = data.get("white", {})
                black = data.get("black", {})
                white_id = (white.get("id") or "").lower()
                black_id = (black.get("id") or "").lower()
                bot_lower = bot_name.lower()
                bot_is_white = white_id == bot_lower
                opponent = black if bot_is_white else white
                opponent_name = opponent.get("name") or opponent.get("id") or "unknown"
                announced = True
                print(f"Game {game_id} ({opponent_name}) started")

            state = data.get("state", data)
            moves = state.get("moves", "").strip()
            move_list = moves.split() if moves else []

            if bot_is_white is not None:
                opponent_takeback_offer = (
                    state.get("btakeback", False) if bot_is_white else state.get("wtakeback", False)
                )
                if opponent_takeback_offer and not takeback_offer_seen:
                    accept_takeback = takebacks_accepted < max_takebacks
                    api.respond_takeback(game_id, accept=accept_takeback)
                    if accept_takeback:
                        takebacks_accepted += 1
                    takeback_offer_seen = True
                elif not opponent_takeback_offer:
                    takeback_offer_seen = False

            while processed_plies < len(move_list):
                uci_move = move_list[processed_plies]
                pretty = uci_to_pretty(uci_move, board)

                move_by_white = processed_plies % 2 == 0
                fullmove_number = (processed_plies // 2) + 1
                move_label = f"{fullmove_number}." if move_by_white else f"{fullmove_number}..."

                is_engine_move = bot_is_white is not None and bot_is_white == move_by_white
                move_prefix = "Engine" if is_engine_move else "Move"
                print(f"{move_prefix}: {move_label} {pretty}     |     game {game_id} ({opponent_name})")

                apply_uci_move(board, uci_move)
                processed_plies += 1

            if bot_is_white is None:
                my_turn = False
            else:
                my_turn = (len(move_list) % 2 == 0) if bot_is_white else (len(move_list) % 2 != 0)

            status = state.get("status", "started")
            terminal_statuses = {
                "aborted",
                "mate",
                "resign",
                "stalemate",
                "timeout",
                "draw",
                "outoftime",
                "cheat",
                "noStart",
                "variantEnd",
                "unknownFinish",
            }
            if status in terminal_statuses:
                result = format_result(status, state.get("winner"))
                if not announced:
                    print(f"Game {game_id} ({opponent_name})")
                print(f"Result: game {game_id} ({opponent_name}): {result}")
                break

            if status != "started":
                continue

            if my_turn:
                move = engine.get_best_move(moves)
                api.make_move(game_id, move)
    finally:
        if on_game_finish is not None:
            on_game_finish(game_id)


def start():
    import yaml
    from api import LichessAPI
    from challenge import ChallengeHandler
    from Engine.engine import UCIEngine

    print("Loading settings.yml")
    with open("settings.yml", "r") as f:
        conf = yaml.safe_load(f)

    print(f"Bot Name: {conf['bot_name']}")
    api = LichessAPI()
    challenge_conf = conf.get("challenge", {})
    eng = UCIEngine(
        conf["engine_path"],
        movetime_ms=conf.get("move_time_ms", 60),
        uci_options=conf.get("uci_options", {}),
    )
    max_takebacks = int(challenge_conf.get("max_takebacks", 0))
    active_games = set()
    active_games_lock = threading.Lock()

    def get_active_games_count():
        with active_games_lock:
            return len(active_games)

    def mark_game_finished(game_id):
        with active_games_lock:
            active_games.discard(game_id)

    ch = ChallengeHandler(api, challenge_conf, active_games_getter=get_active_games_count)

    events = api.stream_events()
    for line in events.iter_lines(chunk_size=1):
        if line:
            event = json.loads(line.decode("utf-8"))
            if "type" not in event:
                continue

            print(f"Received event type: {event['type']}")
            ch.handle(event)
            if event["type"] == "gameStart":
                game_id = event["game"]["id"]
                print(f"Game Detected: {game_id}")
                with active_games_lock:
                    active_games.add(game_id)
                threading.Thread(
                    target=play_game,
                    args=(game_id, api, conf["bot_name"], eng, max_takebacks, mark_game_finished),
                ).start()


def run_upgrade():
    from api import LichessAPI

    api = LichessAPI()
    api.upgrade_account()


def main():
    command = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "run"

    if command in {"run", "start"}:
        start()
    elif command in {"upgrade", "!upgrade"}:
        run_upgrade()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python -u bot.py [run|upgrade]")
        sys.exit(2)


if __name__ == "__main__":
    main()
