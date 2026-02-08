import webbrowser as wb
from pynput import keyboard
import pyautogui as pyau
import sqlite3
from time import gmtime, strftime
import time
import sys
import os

print("Script starting...")

# ---------------- Utilities for keyboard ----------------
pressed_keys = set()

def is_key_pressed(key):
    return key in pressed_keys

def on_press(key):
    try:
        if hasattr(key, 'char') and key.char is not None:
            pressed_keys.add(key.char)
        else:
            pressed_keys.add(key)
    except Exception as e:
        print("on_press error:", e)

def on_release(key):
    try:
        if hasattr(key, 'char') and key.char is not None:
            pressed_keys.discard(key.char)
        else:
            pressed_keys.discard(key)
    except Exception as e:
        print("on_release error:", e)

# ---------------- Start listening ----------------
try:
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    print("Keyboard listener started")
except Exception as e:
    print("Listener failed:", e)
    input("Press Enter to exit...")
    sys.exit()

# ---------------- Database connection ----------------
try:
    home = os.path.expanduser("~")  # Your user folder
    db_filename = os.path.join(home, "Epstein.db")
    connection = sqlite3.connect(db_filename)

    connection = sqlite3.connect(db_filename)
    db = connection.cursor()

    db.execute(
        "CREATE TABLE IF NOT EXISTS favorites "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, link TEXT, date TEXT)"
    )
    connection.commit()
except Exception as e:
    print("Database error:", e)
    input("Press Enter to exit...")
    sys.exit()

def save_link_as_favorite(link: str):
    date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    db.execute("INSERT INTO favorites (link, date) VALUES (?, ?)", (link, date))
    connection.commit()

def get_favorites():
    db.execute("SELECT * FROM favorites")
    return db.fetchall()

# ---------------- User input ----------------
try:
    input_link = input('enter a link to go off of: ').strip()
    input('press enter to search')
except Exception as e:
    print("Input error:", e)
    input("Press Enter to exit...")
    sys.exit()

link_numb = 0

def get_link(file_num_modifier=0):
    parts = input_link.split('/')
    video_file = parts[-1]

    try:
        file_num = video_file.replace('.mp4', '').replace('EFTA', '')
        file_num_digit_len = len(file_num)
        file_num = int(file_num) + file_num_modifier
    except Exception:
        print("Invalid link format:", video_file)
        return input_link

    parts[-1] = f'EFTA{str(file_num).zfill(file_num_digit_len)}.mp4'
    return '/'.join(parts)

def open_link():
    wb.open(get_link(link_numb))

last_a_state = False
last_d_state = False
last_f_state = False
last_m_state = False

def link_number():
    global link_numb
    global last_a_state, last_d_state, last_f_state, last_m_state

    current_a_state = 'a' in pressed_keys
    current_d_state = 'd' in pressed_keys
    current_f_state = 'f' in pressed_keys
    current_m_state = 'm' in pressed_keys

    if current_d_state and not last_d_state:
        pyau.hotkey('ctrl', 'w')
        link_numb += 1
        open_link()

    elif current_a_state and not last_a_state:
        pyau.hotkey('ctrl', 'w')
        link_numb = max(0, link_numb - 1)
        open_link()

    elif current_f_state and not last_f_state:
        pyau.hotkey('ctrl', 'w')

    elif current_m_state and not last_m_state:
        save_link_as_favorite(get_link(link_numb))
        with open("mem_links1.txt", "w", encoding="utf-8") as f:
            for row in get_favorites():
                f.write(f'[{row[0]} ({row[2]})]: {row[1]}\n')
        print("Saved favorite")

    last_a_state = current_a_state
    last_d_state = current_d_state
    last_f_state = current_f_state
    last_m_state = current_m_state

print("Listening for input... Press Ctrl+C to exit.")

# ---------------- Main loop ----------------
try:
    while True:
        link_number()
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    print("Runtime error:", e)
finally:
    listener.stop()
    connection.close()
    input("Program ended. Press Enter to close.")
