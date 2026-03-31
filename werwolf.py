import random
import os
import copy
import json


def clear_screen():
    # Löscht das Terminal (Windows = cls, Mac/Linux = clear)
    os.system('cls' if os.name == 'nt' else 'clear')


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def red(text):
    return f"\033[91m{text}\033[0m"


def green(text):
    return f"\033[92m{text}\033[0m"


def yellow(text):
    return f"\033[93m{text}\033[0m"


def blue(text):
    return f"\033[94m{text}\033[0m"


def rainbow(text):
    """Split by newline first, then color every non-space character in rainbow order."""
    colors = ["\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"]
    lines = str(text).split("\n")
    output_lines = []

    for line in lines:
        color_index = 0
        colored = []
        for char in line:
            if char.isspace():
                colored.append(char)
            else:
                colored.append(f"{colors[color_index % len(colors)]}{char}\033[0m")
            color_index += 1
        output_lines.append("".join(colored))

    return "\n".join(output_lines)


rng = random.SystemRandom()
SETUP_FILE = "werwolf_setup.json"


def save_setup(safe_mode_value, num_players_value, players_names_value, deck_string_value):
    setup_data = {
        "safe_mode": safe_mode_value,
        "num_players": num_players_value,
        "players_names": players_names_value,
        "deck_string": deck_string_value,
    }
    with open(SETUP_FILE, "w", encoding="utf-8") as file:
        json.dump(setup_data, file, ensure_ascii=False, indent=2)


def load_setup():
    if not os.path.exists(SETUP_FILE):
        return None

    try:
        with open(SETUP_FILE, "r", encoding="utf-8") as file:
            setup_data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None

    required_keys = {"safe_mode", "num_players", "players_names", "deck_string"}
    if not required_keys.issubset(setup_data.keys()):
        return None

    if not isinstance(setup_data["safe_mode"], bool):
        return None
    if not isinstance(setup_data["num_players"], int):
        return None
    if not isinstance(setup_data["players_names"], list):
        return None
    if not isinstance(setup_data["deck_string"], str):
        return None

    return setup_data


def pick_line(key_or_lines, _depth=0, **kwargs):
    if _depth > 8:
        return ""

    def resolve_value(value):
        """If a placeholder value is a list/tuple, pick one random item."""
        if isinstance(value, (list, tuple)):
            if not value:
                return ""
            return resolve_value(rng.choice(value))
        return value

    if isinstance(key_or_lines, str):
        entry = TEXTS.get(key_or_lines, key_or_lines)
    else:
        entry = key_or_lines

    if isinstance(entry, (list, tuple)):
        template = str(rng.choice(entry)) if entry else ""
    else:
        template = str(entry)

    while "{{" in template and "}}" in template and _depth <= 8:
        start = template.find("{{")
        end = template.find("}}", start + 2)
        if end == -1:
            break
        key = template[start + 2:end].strip()
        replacement = pick_line(key, _depth=_depth + 1, **kwargs)
        template = template[:start] + replacement + template[end + 2:]

    resolved_kwargs = {key: resolve_value(value) for key, value in kwargs.items()}
    return template.format_map(SafeDict(**resolved_kwargs))


def random_alive_player(fallback="jemand"):
    """Return a random alive player name for dynamic text placeholders."""
    if "players" not in globals():
        return fallback
    alive_players = [name for name, data in players.items() if data.get("lebt")]
    if not alive_players:
        return fallback
    return rng.choice(alive_players)


def read_int_input(prompt_key):
    """Read an integer input safely without crashing on empty input."""
    while True:
        raw = input(pick_line(prompt_key)).strip()
        if raw.isdigit():
            return int(raw)
        print(pick_line("not_a_number"))


def announce_phase_awake(phase_key, color_func=yellow, plural=False):
    phase_label = pick_line(phase_key)
    key = "phase_awake_plural" if plural else "phase_awake_single"
    print(color_func(pick_line(key, phase=phase_label)))


def announce_phase_sleep(phase_key, color_func=yellow, plural=False):
    phase_label = pick_line(phase_key)
    key = "phase_sleep_plural" if plural else "phase_sleep_single"
    print(color_func(pick_line(key, phase=phase_label)))


def colorize_role(role_name):
    """Color roles for clearer Seherin output readability."""
    role_colors = {
        "Werwolf": red,
        "Seherin": blue,
        "Hexe": yellow,
        "Erbe": yellow,
        "Jäger": yellow,
        "Harlekin": yellow,
        "Dorfbewohner": green,
    }
    color_func = role_colors.get(role_name, blue)
    return color_func(role_name)

deck = []
deaths_this_night = []
death_messages_this_night = []

safe_mode = False
death_word = "getötet"

gewonnen_ascii_art = "  ░██████                                                                                      \n ░██   ░██                                                                                     \n░██         ░███████  ░██    ░██    ░██  ░███████  ░████████  ░████████   ░███████  ░████████  \n░██  █████ ░██    ░██ ░██    ░██    ░██ ░██    ░██ ░██    ░██ ░██    ░██ ░██    ░██ ░██    ░██ \n░██     ██ ░█████████  ░██  ░████  ░██  ░██    ░██ ░██    ░██ ░██    ░██ ░█████████ ░██    ░██ \n ░██  ░███ ░██          ░██░██ ░██░██   ░██    ░██ ░██    ░██ ░██    ░██ ░██        ░██    ░██ \n  ░█████░█  ░███████     ░███   ░███     ░███████  ░██    ░██ ░██    ░██  ░███████  ░██    ░██ "
logo = rainbow("░██       ░██                                                  ░██     ░████ \n░██       ░██                                                  ░██    ░██    \n░██  ░██  ░██  ░███████  ░██░████ ░██    ░██    ░██  ░███████  ░██ ░████████ \n░██ ░████ ░██ ░██    ░██ ░███     ░██    ░██    ░██ ░██    ░██ ░██    ░██    \n░██░██ ░██░██ ░█████████ ░██       ░██  ░████  ░██  ░██    ░██ ░██    ░██    \n░████   ░████ ░██        ░██        ░██░██ ░██░██   ░██    ░██ ░██    ░██    \n░███     ░███  ░███████  ░██         ░███   ░███     ░███████  ░██    ░██    ")

def load_texts():
    """Lade alle Strings aus werwolf_strings.json"""
    strings_file = "werwolf_strings.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    primary_path = os.path.join(script_dir, strings_file)

    # Fallback auf aktuelles Verzeichnis, falls das Skript in Sonderfaellen ohne __file__ genutzt wird.
    candidate_paths = [primary_path, strings_file]

    for path in candidate_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except (OSError, json.JSONDecodeError):
            continue

    print(f"Fehler: {strings_file} konnte nicht geladen werden!")
    return {}

TEXTS = load_texts()

def player_selector(options=None):
    if options is None:
        if "players" in globals():
            options = [name for name, data in players.items() if data["lebt"]]
        else:
            options = deck

    if not options:
        print(pick_line("no_valid_players"))
        return None

    print(pick_line("select_player"))
    for i, player in enumerate(options):
        print(pick_line("select_player_option", index=i + 1, player=player))
    while True:
        raw = input(pick_line("select_player_input")).strip()
        if not raw.isdigit():
            print(pick_line("not_a_number"))
            continue

        selection = int(raw)
        if 1 <= selection <= len(options):
            return options[selection - 1]

        print(pick_line("not_a_number"))
def kill_player(player):
    if player is None:
        return
    if not players[player]["lebt"]:
        return

    kill_text = pick_line("kill", player=player, death_word=death_word)
    print(red(kill_text))
    players[player]["lebt"] = False
    deaths_this_night.append(player)
    death_messages_this_night.append(kill_text)

    dead_role = players[player]["rolle"]
    dead_status = copy.deepcopy(players[player]["status"])

    if dead_role == "Werwolf":
        print(pick_line("dead_wolf", player=player))
    elif dead_role == "Jäger":
        print(pick_line("dead_hunter", player=player))
        target = player_selector()
        kill_player(target)

    # Wenn die Person das Ziel des Erben ist, dann erbt der Erbe Rolle und Status.
    if "Erbe" in assignments.values():
        erbe_player = next(player for player, role in assignments.items() if role == "Erbe")
        if players[erbe_player]["status"]["kopie"] == player:
            print(pick_line("heir_inherits", heir=erbe_player, dead_player=player))
            players[erbe_player]["rolle"] = dead_role
            players[erbe_player]["status"] = dead_status
            assignments[erbe_player] = dead_role

# ============ MAIN PROGRAM ============
def main():
    """Main entry point for the game."""
    while True:
        global num_players, players_names, deck_string
        
        clear_screen()
        print(logo)
        
        # Setup-Logik
        setup = prompt_and_load_setup()
        if setup is not None:
            num_players, players_names, deck_string = initialize_setup_from_file(setup)
        else:
            num_players, players_names, deck_string = prompt_new_setup()
        
        # Deck vorbereiten
        clear_screen()
        print(pick_line("players_header"))
        for name in players_names:
            print(name)
        
        deck = convert_and_validate_deck(deck_string, num_players)
        
        # Spieler initialisieren
        create_player_objects(players_names, deck)
        
        # Rollen zeigen
        show_role_reveal()
        
        # Spiel starten
    
        run_game()
        input(pick_line("restart_prompt"))



def check_winner():
    alive_wolves = sum(1 for name, data in players.items() if data["lebt"] and data["rolle"] == "Werwolf")
    alive_non_wolves = sum(1 for name, data in players.items() if data["lebt"] and data["rolle"] != "Werwolf")

    if alive_wolves == 0:
        if safe_mode:
            print(logo)
            print(green(pick_line("villagers_win_safe")))
        else:
            print(logo)
            print(green(pick_line("villagers_win")))
        return True

    if alive_wolves >= alive_non_wolves:
        print(logo)
        print(red(pick_line("wolves_win")))
        return True

    return False

def print_HUD():
    line = f"{pick_line('hud_players')}: "
    count = 0
    for name, data in players.items():
        if data["lebt"]:
            count += 1
    line += f"{green(count)}/{yellow(len(players))}"
    print(line)
    line = f"{pick_line('hud_wolves')}: "
    count = 0
    for name, data in players.items():
        if data["lebt"] and data["rolle"] == "Werwolf":
            count += 1
    line += f"{red(count)}/{yellow(len([name for name, data in players.items() if data['rolle'] == 'Werwolf']))}"
    print(line)
    line = f"{pick_line('hud_round')}: "
    line += f"{round_number}"
    print(line)

def run_morning_event():
    clear_screen()
    print(logo)
    print(yellow(pick_line("morning_awake")))
    event_type = rng.choice(["hint", "funny", "nothing"])
    text_player = random_alive_player()

    if event_type == "hint":
        alive_players = [name for name, data in players.items() if data["lebt"]]
        if alive_players:
            hinted_player = rng.choice(alive_players)
            print(yellow(pick_line("event_hint", player=hinted_player)))
        else:
            print(yellow(pick_line("event_nothing", player=text_player)))
    elif event_type == "funny":
        print(yellow(pick_line("event_funny", player=text_player)))
    else:
        print(yellow(pick_line("event_nothing", player=text_player)))

    input(pick_line("morning_continue"))
    return


def prompt_and_load_setup():
    """Prompt user to load, edit loaded setup, or create a new setup."""
    action = input(pick_line("setup_action_prompt")).strip().lower()

    if action in ("1", "l", "load"):
        setup = load_setup()
        if setup is None:
            print(pick_line("setup_missing_for_load"))
            return None
        return setup

    if action in ("2", "e", "edit", "bearbeiten"):
        setup = load_setup()
        if setup is None:
            print(pick_line("setup_missing_for_load"))
            return None
        return edit_loaded_setup(setup)

    if action in ("3", "n", "neu", "new", ""):
        return None

    print(pick_line("setup_invalid_choice"))
    return None


def edit_loaded_setup(setup):
    """Allow editing of loaded setup values before game start."""
    edited = dict(setup)

    print(
        pick_line(
            "setup_current_overview",
            safe_mode="on" if edited["safe_mode"] else "off",
            num_players=edited["num_players"],
            deck_string=edited["deck_string"],
        )
    )

    safe_mode_input = input(pick_line("setup_edit_oma_prompt")).strip().lower()
    if safe_mode_input in ("on", "1", "ja", "j", "true"):
        edited["safe_mode"] = True
    elif safe_mode_input in ("off", "0", "nein", "n", "false"):
        edited["safe_mode"] = False

    player_count_input = input(
        pick_line("setup_edit_player_count_prompt", num_players=edited["num_players"])
    ).strip()
    if player_count_input.isdigit() and int(player_count_input) > 0:
        edited["num_players"] = int(player_count_input)

    edit_names = input(pick_line("setup_edit_names_prompt")).strip().lower()
    if edit_names in ("j", "ja", "y", "yes", "1"):
        names = []
        for i in range(edited["num_players"]):
            name = input(pick_line("player_name_prompt", index=i + 1))
            names.append(name)
        edited["players_names"] = names
    else:
        edited["players_names"] = edited["players_names"][: edited["num_players"]]
        while len(edited["players_names"]) < edited["num_players"]:
            edited["players_names"].append(f"Spieler{len(edited['players_names']) + 1}")

    role_input = input(pick_line("setup_edit_role_prompt", deck_string=edited["deck_string"])).strip().upper()
    if role_input:
        edited["deck_string"] = role_input

    save_setup(
        edited["safe_mode"],
        edited["num_players"],
        edited["players_names"],
        edited["deck_string"],
    )
    print(pick_line("setup_saved_after_edit"))
    return edited


def initialize_setup_from_file(setup):
    """Initialize game settings from loaded setup file."""
    global safe_mode, death_word
    safe_mode = setup["safe_mode"]
    death_word = "aus dem Dorf verwiesen" if safe_mode else "getötet"
    num_players = setup["num_players"]
    players_names = setup["players_names"]
    deck_string = setup["deck_string"].upper()
    if num_players != len(players_names):
        num_players = len(players_names)
    print(pick_line("setup_loaded"))
    return num_players, players_names, deck_string


def prompt_new_setup():
    """Prompt user to enter all setup manually."""
    global safe_mode, death_word
    safe_mode_input = input(pick_line("oma_mode_prompt")).strip().lower()
    safe_mode = safe_mode_input in ("on", "1", "ja", "j", "true")
    if safe_mode:
        death_word = "aus dem Dorf verwiesen"

    num_players = read_int_input("player_count_prompt")
    players_names = []
    for i in range(num_players):
        name = input(pick_line("player_name_prompt", index=i + 1))
        players_names.append(name)

    clear_screen()
    print(logo)
    print(pick_line("players_header"))
    for name in players_names:
        print(name)

    deck_string = input(pick_line("roles_input_prompt")).upper()

    save_choice = input(pick_line("setup_save_prompt")).strip().lower()
    if save_choice in ("j", "ja", "y", "yes", "1"):
        try:
            save_setup(safe_mode, num_players, players_names, deck_string)
            print(pick_line("setup_saved", file=SETUP_FILE))
        except OSError:
            print(pick_line("setup_save_failed"))

    return num_players, players_names, deck_string


def convert_and_validate_deck(deck_string, num_players):
    """Convert role string to deck and validate/fill with Dorfbewohner."""
    deck = list(deck_string)
    converted_deck = []
    print(pick_line("roles_in_deck"))
    for role in deck:
        role = role.strip()
        match role:
            case "W":
                role = "Werwolf"
            case "E":
                if not "Erbe" in converted_deck:
                    role = "Erbe"
                else:
                    print(pick_line("only_one_heir"))
                    continue
            case "J":
                role = "Jäger"
            case "H":
                if not "Hexe" in converted_deck:
                    role = "Hexe"
                else:
                    print(pick_line("only_one_witch"))
                    continue
            case "S":
                if not "Seherin" in converted_deck:
                    role = "Seherin"
                else:
                    print(pick_line("only_one_seer"))
                    continue
            case "B":                
                role = "Harlekin"
                
            case _:
                print(pick_line("invalid_role", role=role))
                role = None
                continue
        converted_deck.append(role)
        print(role)
    
    if len(converted_deck) < num_players:
        print(pick_line("not_enough_roles", deck_count=len(converted_deck), num_players=num_players))
        while len(converted_deck) < num_players:
            converted_deck.append("Dorfbewohner")
    
    rng.shuffle(converted_deck)
    return converted_deck


def create_player_objects(players_names, deck):
    """Initialize players dict with roles and status."""
    global players, assignments
    role_data = {
        "Hexe": {"gift": True, "heilung": True},
        "Erbe": {"kopie": None},
        "Seherin": {},
        "Werwolf": {},
        "Dorfbewohner": {},
        "Harlekin": {}
    }
    
    players = {}
    for name in players_names:
        role_name = deck.pop()
        players[name] = {
            "rolle": role_name,
            "status": copy.deepcopy(role_data.get(role_name, {})),
            "lebt": True
        }
    
    assignments = {name: data["rolle"] for name, data in players.items()}
    if "Werwolf" not in assignments.values():
        print(pick_line("missing_wolf"))
        random_player = rng.choice(players_names)
        players[random_player]["rolle"] = "Werwolf"
        players[random_player]["status"] = copy.deepcopy(role_data["Werwolf"])
        assignments[random_player] = "Werwolf"


def show_role_reveal():
    """Show all players their roles (first round only)."""
    for player, role in assignments.items():
        clear_screen()
        print(logo)
        print(pick_line("role_reveal_prompt", player=player))
        input()
        clear_screen()
        print(logo)
        print(pick_line("role_reveal", player=green(player), role=blue(role)))
        input()
    clear_screen()
    print(logo)
    print(pick_line("moderator_start"))
    input()


def run_erbe_phase():
    """Run Erbe (heir) selection phase."""
    if "Erbe" not in assignments.values():
        return
    erbe_player = next(player for player, role in assignments.items() if role == "Erbe")
    if players[erbe_player]["status"]["kopie"] is None:
        clear_screen()
        print(logo)
        print_HUD()
        announce_phase_awake("phase_erbe_label", color_func=yellow)
        print(pick_line("heir_phase", player=erbe_player))
        erbe_target = player_selector([name for name, data in players.items() if data["lebt"] and name != erbe_player])
        players[erbe_player]["status"]["kopie"] = erbe_target
        announce_phase_sleep("phase_erbe_label", color_func=yellow)
        input(pick_line("continue_prompt"))
        clear_screen()


def run_werwolf_phase(round_number):
    """Run wolf target selection phase. Round 1 has no wolf kill."""
    if round_number > 1:
        clear_screen()
        print(logo)
        announce_phase_awake("phase_wolf_label", color_func=red, plural=True)
        print(pick_line("wolf_phase"))
        werwolf_target = player_selector()
        announce_phase_sleep("phase_wolf_label", color_func=red, plural=True)
        input(pick_line("continue_prompt"))
        return werwolf_target
    else:
        print(pick_line("first_night_no_wolf"))
        announce_phase_sleep("phase_wolf_label", color_func=red, plural=True)
        input(pick_line("continue_prompt"))
        return None


def run_seherin_phase():
    """Run Seherin (seer) role check phase."""
    if "Seherin" not in assignments.values():
        return
    
    clear_screen()
    print(logo)
    print_HUD()
    announce_phase_awake("phase_seer_label", color_func=blue)
    seherin_player = next(player for player, role in assignments.items() if role == "Seherin")
    print(pick_line("seer_phase", player=seherin_player))
    seherin_target = player_selector()
    revealed_role = players[seherin_target]["rolle"]
    print(
        pick_line(
            "seer_result",
            player=green(seherin_target),
            role=colorize_role(revealed_role),
        )
    )
    announce_phase_sleep("phase_seer_label", color_func=blue)
    input(pick_line("continue_prompt"))
    clear_screen()


def run_hexe_phase(werwolf_target):
    """Run Hexe (witch) potion phase. Returns (possibly modified werwolf_target, poison_killed)."""
    if "Hexe" not in assignments.values():
        return werwolf_target, None
    
    clear_screen()
    print(logo)
    print_HUD()
    announce_phase_awake("phase_witch_label", color_func=yellow)
    hexe_player = next(player for player, role in assignments.items() if role == "Hexe")
    print(pick_line("witch_phase", player=hexe_player))
    if werwolf_target is not None:
        print(red(pick_line("wolf_target_selected", player=werwolf_target)))
    print(pick_line("witch_heal_option"))
    print(pick_line("witch_poison_option"))
    print(pick_line("do_nothing_option"))
    hexe_choice = read_int_input("witch_choice_prompt")
    
    poison_target = None
    if hexe_choice == 1 and players[hexe_player]["status"]["heilung"]:
        print(green(pick_line("witch_heal_used", player=hexe_player, target=werwolf_target)))
        players[hexe_player]["status"]["heilung"] = False
        werwolf_target = None
    elif hexe_choice == 2 and players[hexe_player]["status"]["gift"]:
        poison_target = player_selector([name for name, data in players.items() if data["lebt"] and name != hexe_player])
        print(red(pick_line("witch_poison_used", player=hexe_player, target=poison_target)))
        players[hexe_player]["status"]["gift"] = False
        kill_player(poison_target)
    announce_phase_sleep("phase_witch_label", color_func=yellow)
    input(pick_line("continue_prompt"))
    
    return werwolf_target, poison_target


def run_night_phase(round_number):
    """Run a complete night: Erbe, Werwolf, Seherin, Hexe phases."""
    global deaths_this_night, death_messages_this_night
    deaths_this_night.clear()
    death_messages_this_night.clear()
    
    print(pick_line("night_start"))
    run_erbe_phase()
    werwolf_target = run_werwolf_phase(round_number)
    run_seherin_phase()
    werwolf_target, _ = run_hexe_phase(werwolf_target)

    # Das Werwolf-Ziel stirbt immer nach der Hexenphase,
    # außer es wurde geheilt (werwolf_target ist dann None).
    kill_player(werwolf_target)


def print_deaths():
    """Print all deaths from this night."""
    clear_screen()
    print(logo)
    if deaths_this_night:
        print(red(pick_line("deaths_header")))
        if death_messages_this_night:
            for message in death_messages_this_night:
                print(red(pick_line("death_detail_item", message=message)))
        else:
            for dead_player in deaths_this_night:
                print(red(pick_line("death_list_item", player=dead_player)))
    else:
        print(green(pick_line("no_deaths")))
    input(pick_line("continue_prompt"))


def run_day_phase():
    """Run day phase: village vote."""
    
    
    clear_screen()
    print(logo)
    print_HUD()
    print(yellow(pick_line("vote_awake")))
    print(pick_line("wake", player=random_alive_player()))
    print(red(pick_line("vote_option")))
    print(pick_line("skip_vote_option"))
    choice = read_int_input("vote_choice_prompt")
    if choice == 1:
        confirm = input(red(pick_line("vote_confirm"))).strip()
        if confirm == "1":
            vote_target = player_selector()
            #wenn harlekin
            if players[vote_target]["rolle"] == "Harlekin":
                clear_screen()
                print(logo)
                print(red(pick_line("harlequin_win", player=vote_target)))
                global game_over
                game_over = True
                return            
            kill_player(vote_target)
    else:
        print(pick_line("no_judgement"))


def run_game():
    """Main game loop."""
    global round_number, game_over
    round_number = 0
    game_over = False
    
    while not game_over:
        round_number += 1
        if check_winner():
            game_over = True
            break
        
        run_night_phase(round_number)
        print_deaths()
        
        if check_winner():
            game_over = True
            break
        run_morning_event()
        run_day_phase()
        
        if check_winner():
            game_over = True
            break

# Entry Point
if __name__ == "__main__":
    main()
    

