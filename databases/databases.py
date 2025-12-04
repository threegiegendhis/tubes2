import sqlite3
import modules.generate_barcode as barcode
import os

db_dir = "databases"
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
# Membuat tabel data untuk data diri


def init_data_diri_db():
    conn = sqlite3.connect(os.path.join(db_dir, 'data_diri.db'))
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        nomor INTEGER NOT NULL,
        NIK INTEGER NOT NULL,
        gender CHAR(1) NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Membuat tabel data untuk info login


def init_login_db():
    conn = sqlite3.connect(os.path.join(db_dir, 'data_diri.db'))
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS loginInfo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Membuat tabel data untuk informasi kereta


def init_kereta_db():
    conn = sqlite3.connect(os.path.join(db_dir, 'data_kereta.db'))
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kereta_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asal TEXT NOT NULL,
        tujuan TEXT NOT NULL,
        jam_keberangkatan TEXT NOT NULL,
        tiket_id INTEGER NOT NULL
    )
    ''')

# Fungsi untuk register


def register_user(email, password):
    conn = sqlite3.connect(os.path.join(db_dir, 'data_diri.db'))
    cursor = conn.cursor()
    # Mencari apakah ada email inputan dari user yang sama dengan email yang sudah ada di database
    cursor.execute("SELECT id FROM loginInfo WHERE email = ?", (email,))
    if cursor.fetchone():
        print("Email sudah terdaftar. Silakan gunakan email lain.")
        conn.close()
        return False
    cursor.execute(
        "INSERT INTO loginInfo (email, password) VALUES (?, ?)", (email, password))
    conn.commit()
    conn.close()
    print("Registrasi berhasil!")
    return True

# Fungsi untuk login


def login_user(email, password):
    conn = sqlite3.connect(os.path.join(db_dir, 'data_diri.db'))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM loginInfo WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    # Jika ada email dan password yang sama dengan yang ada di database, proses login akan berhasil
    if user:
        print("Login berhasil!")
        return True
    else:
        print("Email atau password salah.")
        return False

# Fungsi untuk input data diri


def add_user(nama, nomor, NIK, gender):
    conn = sqlite3.connect(os.path.join(db_dir, 'data_diri.db'))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (nama, nomor, NIK, gender) VALUES (?, ?, ?, ?)", (nama, nomor, NIK, gender))
    conn.commit()
    conn.close()

# Fungsi untuk pemesanan tiket


def book_ticket(asal, tujuan, jam_keberangkatan, nama):
    conn = sqlite3.connect(os.path.join(db_dir, 'data_kereta.db'))
    cursor = conn.cursor()
    # Membuat barcode
    tiket_id = barcode.create(nama)
    cursor.execute("INSERT INTO kereta_info (asal, tujuan, jam_keberangkatan, tiket_id) VALUES (?, ?, ?, ?)",
                   (asal, tujuan, jam_keberangkatan, tiket_id))
    conn.commit()
    conn.close()
    print(
        f'\nTiket berhasil dipesan untuk {nama}. Asal: {asal}, Tujuan: {tujuan}, Jam Keberangkatan: {jam_keberangkatan}, ID Tiket: {tiket_id}')
    return True

# Mencari nama user dari email


def get_user_by_email(email):
    conn = sqlite3.connect(os.path.join(db_dir, 'data_diri.db'))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nama FROM users WHERE id = (SELECT id FROM loginInfo WHERE email = ?)", (email,))
    user = cursor.fetchone()
    conn.close()
    return user
