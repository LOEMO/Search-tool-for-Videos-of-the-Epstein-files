import webbrowser as wb
from pynput import keyboard
import pyautogui as pyau
import sqlite3
from time import gmtime, strftime


# Utilities for keyboard
def is_key_pressed(key):
    return key in pressed_keys

pressed_keys = set()

def on_press(key):
    # Add keys to the set when pressed
    if hasattr(key, 'char') and key.char is not None:
        pressed_keys.add(key.char)
    else:
        pressed_keys.add(key)

def on_release(key):
    # Remove keys from the set when released
    if hasattr(key, 'char') and key.char is not None:
        pressed_keys.discard(key.char)
    else:
        pressed_keys.discard(key)

# Start listening
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Database connection

db_filename = 'Epstein.db'
connection = sqlite3.connect(db_filename)
db = connection.cursor()

db.execute("CREATE TABLE IF NOT EXISTS favorites (id INTEGER PRIMARY KEY AUTOINCREMENT, link TEXT, date TEXT)") # create favorites table
connection.commit() # Save changes

def save_link_as_favorite(link: str):
    date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    db.execute("INSERT INTO favorites (link, date) VALUES (?, ?)", (link, date,))
    connection.commit() # Save changes

def get_favorites():
    db.execute("SELECT * FROM favorites")
    rows = db.fetchall()
    return rows




input_link = input('enter a link to go off of')
message = input('press enter to search')
#input_link = 'https://www.justice.gov/epstein/files/DataSet%2010/EFTA01683424.mp4'
link_numb = 0
def get_link(file_num_modifier=0):
    # Split into parts
    parts = input_link.split('/')
    video_file = parts[-1]

    # Extract file_num
    file_num = video_file.replace('.mp4', '')
    file_num = file_num.replace('EFTA', '')
    file_num_digit_len = len(file_num)
    file_num = int(file_num)

    # Modify file_num
    file_num = file_num + file_num_modifier
    
    # Pad zeroes + reassemble link
    file_num_str = str(file_num).zfill(file_num_digit_len) # pad with zeroes
    parts[-1] = f'EFTA{file_num_str}.mp4'
    return '/'.join(parts)

# get_link()

def open_link():
    wb.open(get_link(link_numb)) # 0 => current file; 1 => file_num + 1; -1 => file_num -1

last_a_state = False
last_d_state = False
last_f_state = False
last_m_state = False


#open prievious and next links or close links with keybinds
def link_number():
    global link_numb
    global last_f_state
    global last_a_state
    global last_d_state
    global last_m_state
    current_a_state = 'a' in pressed_keys
    current_d_state = 'd' in pressed_keys
    current_f_state = 'f' in pressed_keys
    current_m_state = 'm' in pressed_keys
    #next link
    if 'd' in pressed_keys and current_d_state != last_d_state:
        pyau.hotkey('ctrl', 'w')
        link_numb += 1
        open_link()
    #past links
    elif 'a' in pressed_keys and current_a_state != last_a_state:
        pyau.hotkey('ctrl', 'w')
        link_numb -= 1
        open_link()
    #close current link
    elif 'f' in pressed_keys and current_f_state != last_f_state:
        pyau.hotkey('ctrl', 'w')
    #memorize current link
    elif 'm' in pressed_keys and current_m_state != last_m_state:
        save_link_as_favorite(get_link(link_numb))
        #print(get_favorites())
        with open("mem_links1.txt", "w") as f:
            for row in get_favorites():
                f.write(f'[{row[0]} ({row[2]})]: {row[1]} \n')
            


    last_a_state = current_a_state
    last_d_state = current_d_state
    last_f_state = current_f_state
    last_m_state = current_m_state


try:
    open_link()
    while True:
        link_number()
except KeyboardInterrupt:
    # when ctrl + c is pressed
    connection.close()
