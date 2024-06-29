import sqlite3

if __name__ == '__main__':
    PATH = 'database.db'
else:
    PATH = 'database/database.db'

with sqlite3.connect(PATH) as conn:
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER UNIQUE,
    nickname    TEXT    UNIQUE
                        NOT NULL,
    room        INTEGER
    );
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    capacity INTEGER NOT NULL,
    available INTEGER
    );
    ''')

    conn.commit()


class UsersTools:
    @staticmethod
    def set_nickname(telegram_id: int, nickname: str) -> None:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('INSERT OR REPLACE INTO users (telegram_id, nickname) VALUES (?, ?)', (telegram_id, nickname))
            conn.commit()

    @staticmethod
    def choose_room(telegram_id: int, room_id: int):
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE users SET room =? WHERE telegram_id =?', (room_id, telegram_id))
            cur.execute('UPDATE rooms SET available = available - 1 WHERE id =?', (room_id,))
            conn.commit()

    @staticmethod
    def get_room_id(telegram_id: int) -> int:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('SELECT room FROM users WHERE telegram_id =?', (telegram_id,))
            return cur.fetchone()[0]

    @staticmethod
    def get_nickname(telegram_id: int) -> str:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('SELECT nickname FROM users WHERE telegram_id =?', (telegram_id,))
            return cur.fetchone()[0]

    @staticmethod
    def free_room(telegram_id: int) -> None:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('SELECT room FROM users WHERE telegram_id =?', (telegram_id,))
            room_id = cur.fetchone()[0]
            cur.execute('UPDATE users SET room = NULL WHERE telegram_id =?', (telegram_id,))
            cur.execute('UPDATE rooms SET available = available + 1 WHERE id =?', (room_id,))
            conn.commit()

    @staticmethod
    def isnicknamed(telegram_id: int) -> bool:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('SELECT nickname FROM users WHERE telegram_id =?', (telegram_id,))
            return cur.fetchone() is not None


class RoomsTools:
    @staticmethod
    def delete_room(room: int) -> None:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM rooms WHERE id =?', (room,))
            conn.commit()

    @staticmethod
    def set_room(name: str, capacity: int) -> int:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('INSERT OR REPLACE INTO rooms (name, capacity, available) VALUES (?, ?, ?)',
                        (name, capacity, capacity))
            conn.commit()
            cur.execute('SELECT * FROM rooms WHERE name =? AND capacity =? AND available =?',
                        (name, capacity, capacity))
            return cur.fetchone()[0]

    @staticmethod
    def get_rooms() -> list:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM rooms WHERE available != 0')
            rooms = cur.fetchall()
            return [[e for e in rooms[i:i + 8]] for i in range(0, len(rooms), 8)]

    @staticmethod
    def get_room_members(id_: int) -> tuple:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('SELECT telegram_id FROM users WHERE room =?', (id_,))
            return sum(cur.fetchall(), ())

    @staticmethod
    def delete_deadrooms() -> None:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM rooms WHERE available = 0')
            conn.commit()
