import yaml
import json
import threading
from api import LichessAPI
from challenge import ChallengeHandler
from Engine.engine import UCIEngine

def play_game(game_id, api, bot_name, engine):
    print(f"DEBUG: Starting game loop for {game_id}")
    for line in api.stream_game(game_id).iter_lines():
        if line:
            data = json.loads(line.decode('utf-8'))
            state = data.get("state", data)
            moves = state.get("moves", "")
            move_list = moves.split()
            white_id = data.get("white", {}).get("id")
            is_white = (white_id == bot_name)
            my_turn = (len(move_list) % 2 == 0) if is_white else (len(move_list) % 2 != 0)
            if my_turn:
                move = engine.get_best_move(moves)
                api.make_move(game_id, move)

def start():
    print("DEBUG: Loading settings.yml")
    with open("settings.yml", "r") as f:
        conf = yaml.safe_load(f)
    
    print(f"DEBUG: Bot Name: {conf['bot_name']}")
    api = LichessAPI()
    ch = ChallengeHandler(api)
    eng = UCIEngine(conf["engine_path"])
    
    events = api.stream_events()
    for line in events.iter_lines():
        if line:
            event = json.loads(line.decode('utf-8'))
            if "type" not in event:
                continue
            
            print(f"DEBUG: Received event type: {event['type']}")
            ch.handle(event)
            if event["type"] == "gameStart":
                threading.Thread(target=play_game, args=(event["game"]["id"], api, conf["bot_name"], eng)).start()

if __name__ == "__main__":
    start()
