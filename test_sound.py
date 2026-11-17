# Test program for the Sound Player microservice
# Run this:  python test_sound.py
# It starts the Sound Player microservice by itself, tests it, then shuts it down.

import json
import os
import signal
import subprocess
import sys
import time
import requests

URL = "http://127.0.0.1:5000/"
PLAYSOUND = URL + "playSound/"
SET_VOLUME = URL + "setVolume/"


def find_service_dir(name, key_file):
    # looks for the microservice in this folder, or in a folder next to this one, e.g. Sound-Player_Microservice
    # (also works if it was downloaded as a zip and ends in -main)
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.isfile(os.path.join(tests_dir, key_file)):
        return tests_dir  # this test is inside the microservice's own folder
    parent = os.path.dirname(tests_dir)
    for folder in sorted(os.listdir(parent)):
        path = os.path.join(parent, folder)
        if folder.lower().startswith(name.lower()) and os.path.isfile(os.path.join(path, key_file)):
            return path
    raise SystemExit(f"Could not find the {name} folder. Put it in the same folder as {os.path.basename(tests_dir)}.")


SERVICE_DIR = find_service_dir("Sound-Player_Microservice", "sound_micro.py")


# ---------------- Terminal output ----------------

if os.name == "nt":
    os.system("")  # turns on colors in the Windows terminal
USE_COLOR = sys.stdout.isatty()
test_number = 0
next_part = None


def color(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def part(title):
    global next_part
    next_part = title


def test(title):
    global test_number, next_part
    test_number += 1
    upcoming = f"TEST {test_number}: {title}"
    if next_part:
        upcoming = f"{next_part}  >  {upcoming}"
    print(color("\n  Next up: ", "2") + color(upcoming, "1;33"))
    input(color("  Press Enter to start...", "2"))

    if next_part:
        print("\n\n" + color("#" * 60, "1;35"))
        print(color(f"   {next_part}", "1;35"))
        print(color("#" * 60, "1;35"))
        next_part = None
    print("\n" + color("-" * 60, "36"))
    print(color(f" TEST {test_number}: {title}", "1;36"))
    print(color("-" * 60, "36"))


def result(text):
    print(color(f"  => {text}", "1;32"))


def check_rejected(status):
    if status is not None and 400 <= status < 500:
        result(f"PASS: the microservice rejected the bad input ({status}), no crash")
    else:
        print(color(f"  => UNEXPECTED: got status {status}", "1;31"))


# ---------------- Starting / stopping the microservice ----------------

def check_service():
    try:
        return requests.post(SET_VOLUME + "1", timeout=2).status_code
    except requests.exceptions.ConnectionError:
        return None


def start_service():
    status = check_service()
    if status == 200:
        print(color("[setup] Sound Player microservice is already running, using that one.", "2"))
        return None
    if status is not None:
        raise SystemExit("Port 5000 is being used by something else (the RNG microservice?). Stop it first.")

    print(color("[setup] Starting the Sound Player microservice (flask --app sound_micro run)...", "2"))
    proc = subprocess.Popen([sys.executable, "-m", "flask", "--app", "sound_micro", "run"], cwd=SERVICE_DIR,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=(os.name != "nt"))
    for _ in range(30):
        if check_service() == 200:
            print(color("[setup] Sound Player microservice is running!", "2"))
            return proc
        time.sleep(0.5)
    stop_service(proc)
    raise SystemExit("The Sound Player microservice did not start. Try running it by itself to see the error.")


def stop_service(proc):
    if proc is None:
        return
    print(color("\n[setup] Shutting down the Sound Player microservice...", "2"))
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        os.killpg(proc.pid, signal.SIGTERM)


# ---------------- Talking to the microservice ----------------

def send(method, url):
    # REQUEST: the sound name or volume goes at the end of the URL
    print(color("  -> REQUEST ", "1;34") + f"  {method} {url}")
    try:
        response = requests.request(method, url, timeout=5)
    except requests.exceptions.ConnectionError:
        print(color("  X  Could not connect to the Sound Player microservice.", "1;31"))
        return None

    # RECEIVE: JSON message saying whether it worked
    try:
        shown = json.dumps(response.json(), indent=2)
    except ValueError:
        shown = "(response was not JSON)"

    code = response.status_code
    code_color = "1;32" if code < 300 else "1;33" if code < 500 else "1;31"
    print(color(f"  <- RESPONSE  {code} {response.reason}", code_color))
    for line in shown.splitlines():
        print("     " + line)
    return code


def play_sound(name):
    status = send("GET", PLAYSOUND + name)
    if status == 200:
        time.sleep(2)  # let the sound finish before the next one
    return status


def set_volume(volume):
    return send("POST", SET_VOLUME + str(volume))


# ---------------- The tests ----------------

def run_tests():
    part("PART 1: NORMAL USE")

    test("Play every sound at full volume")
    for sound in ["Click", "Ding", "Success", "Error", "Game_over", "Victory_sound"]:
        play_sound(sound)
    result("All 6 sounds played")

    test("Turn the volume down to 0.2, then back up to 1")
    set_volume(0.2)
    play_sound("Success")
    set_volume(1)
    play_sound("Success")
    result("The second sound was louder than the first")

    part("PART 2: FAIL CASES (bad input)")

    test("A sound name that doesn't exist")
    check_rejected(play_sound("Explosion"))

    test("Wrong capitalization of a real sound")
    check_rejected(play_sound("click"))

    test("Volume too high (5)")
    check_rejected(set_volume(5))

    test("Volume too low (-1)")
    check_rejected(set_volume(-1))

    test("Volume that isn't a number")
    check_rejected(set_volume("loud"))

    part("PART 3: IS IT STILL RUNNING AFTER THE BAD CALLS?")

    test("Normal call after all the bad ones")
    if play_sound("Victory_sound") == 200:
        result("Yes! It still works")


print(color("\n========== Sound Player Microservice Test ==========\n", "1"))
service = start_service()
try:
    run_tests()
finally:
    stop_service(service)
print(color("\n========== Done testing Sound Player microservice ==========", "1"))
