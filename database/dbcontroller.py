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
    capacity INTEGER NOT NULL
    );
    ''')

    conn.commit()


class UsersTools:
    @staticmethod
    def set_nickname(telegram_id: int, nickname: str) -> None:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO users (telegram_id, nickname) VALUES (?, ?)', (telegram_id, nickname))
            conn.commit()


class RoomsTools:
    @staticmethod
    def delete_room(room: int) -> None:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM rooms WHERE id =?', (room,))
            conn.commit()

    @staticmethod
    def set_room(telegram_id: int, room: int) -> None:
        with sqlite3.connect(PATH) as conn:
            cur = conn.cursor()
            cur.execute('UPDATE users SET room =? WHERE telegram_id =?', (room, telegram_id))
            conn.commit()


