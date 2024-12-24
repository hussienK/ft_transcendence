import curses
import requests
import websocket
import threading
import time
import json
import ssl

# ------------------------------
# Configuration / Globals
# ------------------------------
BASE_URL = "https://localhost:8443/api"
TOKEN = None
LOGIN_NAME = None

# WebSocket references
lobby_ws = None  # For lobby/feeds
game_ws = None   # For actual matches

# Curses windows
stdscr = None
HEIGHT, WIDTH = 0, 0

# Whether we are in a match
IN_MATCH = False

# ------------------------------
# Network / API
# ------------------------------
def api_login(username, password):
    """
    Attempt to log in via HTTP and return the token on success.
    Raises an exception if login fails.
    """
    url = f"{BASE_URL}/users/signin/"
    resp = requests.post(
        url, 
        json={"username": username, "password": password},
        verify=False  # For self-signed dev certificates, not recommended for production
    )
    resp.raise_for_status()
    data = resp.json()
    return data["access"]


def api_join_queue():
    """
    Join the game queue.
    """
    headers = {"Authorization": f"Bearer {TOKEN}"}
    url = f"{BASE_URL}/game/join-queue/"
    resp = requests.post(url, headers=headers, verify=False)
    resp.raise_for_status()


def api_leave_queue():
    """
    Leave the game queue.
    """
    headers = {"Authorization": f"Bearer {TOKEN}"}
    url = f"{BASE_URL}/game/leave-queue/"
    resp = requests.post(url, headers=headers, verify=False)
    resp.raise_for_status()


# ------------------------------
# Lobby WebSocket (Feeds / Matches)
# ------------------------------
def start_lobby_websocket():
    """
    Opens a WebSocket to receive feed updates, match_found events, etc.
    """
    global lobby_ws

    ws_url = f"ws://localhost:8080/ws/updates/?token={TOKEN}"
    lobby_ws = websocket.WebSocketApp(
        ws_url,
        on_open=lobby_on_open,
        on_message=lobby_on_message,
        on_error=lobby_on_error,
        on_close=lobby_on_close
    )

    # Run this WebSocket forever in a background thread
    thread = threading.Thread(target=lobby_ws.run_forever, daemon=True)
    thread.start()


def lobby_on_open(ws):
    add_line_to_main("Lobby WebSocket: connected.")

def lobby_on_message(ws, message):
    data = json.loads(message)
    msg_type = data.get("type")

    if msg_type == "feed":
        add_line_to_main(f"Feed: {data['info']}")
    elif msg_type == "match_found":
        session_id = data["session_id"]
        add_line_to_main(f"Match Found! Session ID: {session_id}")
        # Automatically start the game
        start_game_websocket(session_id)
    elif msg_type == "match_found_local":
        session_id = data["session_id"]
        add_line_to_main(f"Local Match Found! Session ID: {session_id}")
        # Also start a game if local matches are relevant
        start_game_websocket(session_id)
    else:
        add_line_to_main(f"Lobby message: {data}")


def lobby_on_error(ws, error):
    add_line_to_main(f"Lobby WS error: {error}")

def lobby_on_close(ws, code, msg):
    add_line_to_main(f"Lobby WebSocket closed ({code}): {msg}")


# ------------------------------
# Game WebSocket (Play Match)
# ------------------------------
def start_game_websocket(session_id):
    """
    Connect to the WebSocket for the given match session.
    """
    global IN_MATCH, game_ws
    if IN_MATCH and game_ws:
        add_line_to_main("Already in a match. Ignoring new match_found.")
        return

    IN_MATCH = True  # Mark that we are in a match
    ws_url = f"ws://localhost:8080/ws/game/{session_id}/?is_local=false&token={TOKEN}"
    add_line_to_main(f"Connecting to game session {session_id}...")

    game_ws = websocket.WebSocketApp(
        ws_url,
        on_open=game_on_open,
        on_message=game_on_message,
        on_error=game_on_error,
        on_close=game_on_close,
    )
    thread = threading.Thread(target=game_ws.run_forever, daemon=True)
    thread.start()

def game_on_open(ws):
    add_line_to_main("Game WebSocket: connected.")
    # No separate input thread here because we will read keystrokes from curses main loop
    # and send them in real-time.

def game_on_message(ws, message):
    data = json.loads(message)
    msg_type = data.get("type", "")

    if msg_type == "state_update":
        render_game_state(data)
    elif msg_type == "game_over":
        winner = data.get("winner", "Unknown")
        add_line_to_main(f"Game Over! Winner: {winner}")
        ws.close()
    else:
        add_line_to_main(f"Game message: {data}")

def game_on_error(ws, error):
    add_line_to_main(f"Game WebSocket error: {error}")

def game_on_close(ws, code, msg):
    global IN_MATCH, game_ws
    add_line_to_main(f"Game WebSocket closed ({code}): {msg}")
    IN_MATCH = False
    game_ws = None


def send_paddle_direction(direction):
    """
    Called from curses to send arrow-key directions to the game server.
    direction can be "up", "down", or None (stop).
    """
    global game_ws
    if not IN_MATCH or not game_ws:
        return

    if not LOGIN_NAME:
        add_line_to_main("Can't send direction; not logged in.")
        return

    message = {
        "player": LOGIN_NAME,
        "direction": direction,
    }
    try:
        game_ws.send(json.dumps(message))
    except Exception as e:
        add_line_to_main(f"Failed to send direction: {e}")


def render_game_state(state):
    """
    Update the main curses window with the latest game state.
    """
    ball_pos = state.get("ball_position")
    p1_pos = state.get("paddle1_position")
    p2_pos = state.get("paddle2_position")
    score1 = state.get("score1")
    score2 = state.get("score2")
    active = state.get("game_is_active")
    winner = state.get("winner")

    msg = [
        "--- Game State ---",
        f"Ball Position: {ball_pos}",
        f"Paddle1: {p1_pos}",
        f"Paddle2: {p2_pos}",
        f"Score: P1 - {score1} | P2 - {score2}",
        f"Game Active: {active}",
    ]
    if winner:
        msg.append(f"Winner: {winner}")
    msg.append("------------------")

    for line in msg:
        add_line_to_main(line)


# ------------------------------
# Curses UI
# ------------------------------
def init_curses(stdscr_obj):
    """
    Initialize curses environment: color, no-echo, etc.
    """
    global stdscr, HEIGHT, WIDTH
    stdscr = stdscr_obj
    curses.curs_set(0)    # Hide cursor
    curses.noecho()       # Don't show typed characters
    curses.cbreak()       # React to keys without pressing Enter
    stdscr.keypad(True)   # Capture special keys like arrows
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLUE)

    HEIGHT, WIDTH = stdscr.getmaxyx()
    draw_status(f"Not logged in | Press 'L' to login.")


def draw_status(text):
    """
    Render a status bar at the top of the screen.
    """
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(0, 0, " " * (WIDTH - 1))  # Clear line
    stdscr.addstr(0, 1, text[:WIDTH - 2])
    stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()


def add_line_to_main(line):
    """
    Add a line of text to the main area (starting at row=1).
    Keep scrolling if we exceed the screen height.
    """
    stdscr.scroll(1)  # scroll everything up by 1 line
    stdscr.move(HEIGHT - 2, 0)
    stdscr.clrtoeol()

    stdscr.addstr(HEIGHT - 2, 0, line[:WIDTH - 1])
    stdscr.refresh()


def main_loop(stdscr_obj):
    """
    Primary curses loop that handles user input (arrow keys, etc.)
    and updates UI accordingly.
    """
    global TOKEN, LOGIN_NAME

    init_curses(stdscr_obj)

    # We'll keep a simple state for demonstration
    logged_in = False

    while True:
        key = stdscr.getch()

        # If user pressed 'q' or 'Q' globally, exit
        if key in (ord('q'), ord('Q')):
            break

        # Press 'L' or 'l' to attempt a login (just for demo)
        if key in (ord('l'), ord('L')) and not logged_in:
            # For demo, we'll do a "hard-coded" login or prompt in a simplistic way
            # A more robust approach would open a separate curses pad or popup for user input
            username = "jennaturner"
            password = "Hk@12345"
            try:
                token = api_login(username, password)
                TOKEN = token
                LOGIN_NAME = username
                logged_in = True
                draw_status(f"Logged in as {LOGIN_NAME}")
                add_line_to_main("Successfully logged in. Joining queue automatically...")
                start_lobby_websocket()  # Start the feed WebSocket
                # Auto-join queue
                try:
                    api_join_queue()
                    add_line_to_main("Joined queue automatically.")
                except Exception as e:
                    add_line_to_main(f"Failed to join queue: {e}")
            except Exception as e:
                add_line_to_main(f"Login error: {e}")

        # If we are in a match, handle arrow key inputs for paddle
        if IN_MATCH:
            if key == curses.KEY_UP:
                send_paddle_direction("up")
            elif key == curses.KEY_DOWN:
                send_paddle_direction("down")
            elif key == ord(' '):
                # Space to stop
                send_paddle_direction(None)

        # Force refresh
        stdscr.refresh()

    # Cleanup on exit
    if logged_in:
        # Attempt to leave queue if still in
        try:
            api_leave_queue()
        except:
            pass
    curses.endwin()


# ------------------------------
# Entry Point
# ------------------------------
def run_cli():
    """
    Wrapper to launch curses application.
    """
    curses.wrapper(main_loop)

if __name__ == "__main__":
    run_cli()
