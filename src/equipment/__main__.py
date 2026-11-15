import argparse
from contextlib import closing
import json
import sqlite3
import sys


def initialize(db):
    db.executescript("""
        CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY CHECK (id > 0));
        CREATE TABLE IF NOT EXISTS equipment (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL REFERENCES students(id),
            equipment_id INTEGER NOT NULL UNIQUE REFERENCES equipment(id)
        );
        INSERT OR IGNORE INTO equipment VALUES
            (1, 'Проектор'), (2, 'Микрофон'), (3, 'Ноутбук');
    """)


def positive_id(value):
    try:
        number = int(value)
    except ValueError:
        number = 0
    if not 0 < number <= 2**63 - 1:
        raise argparse.ArgumentTypeError("ожидается целое число от 1 до 9223372036854775807")
    return number


def parse_args():
    cli = argparse.ArgumentParser(description="Бронирование учебного оборудования")
    cli.add_argument("--db", default="equipment.sqlite3", help="Путь к базе SQLite")
    commands = cli.add_subparsers(dest="command", required=True)
    commands.add_parser("catalog", help="Показать каталог")
    book = commands.add_parser("book", help="Забронировать оборудование")
    book.add_argument("--student", required=True, type=positive_id)
    book.add_argument("--equipment", required=True, type=positive_id)
    mine = commands.add_parser("my-bookings", help="Показать брони студента")
    mine.add_argument("--student", required=True, type=positive_id)
    return cli.parse_args()


def reserve(db, student_id, equipment_id):
    db.execute("BEGIN IMMEDIATE")
    if db.execute("SELECT 1 FROM equipment WHERE id = ?", (equipment_id,)).fetchone() is None:
        return {"error": "equipment_not_found"}, 3
    if db.execute("SELECT 1 FROM bookings WHERE equipment_id = ?", (equipment_id,)).fetchone():
        return {"error": "equipment_unavailable"}, 4
    db.execute("INSERT OR IGNORE INTO students VALUES (?)", (student_id,))
    cursor = db.execute(
        "INSERT INTO bookings (student_id, equipment_id) VALUES (?, ?)",
        (student_id, equipment_id),
    )
    return {
        "id": cursor.lastrowid,
        "student_id": student_id,
        "equipment_id": equipment_id,
        "status": "reserved",
    }, 0


def execute(db, args):
    if args.command == "catalog":
        rows = db.execute("""
            SELECT e.id, e.name, b.id IS NULL AS available
            FROM equipment e LEFT JOIN bookings b ON e.id = b.equipment_id
            ORDER BY e.id
        """)
        return [dict(row, available=bool(row["available"])) for row in rows], 0
    if args.command == "my-bookings":
        rows = db.execute("""
            SELECT id, student_id, equipment_id, 'reserved' AS status
            FROM bookings WHERE student_id = ? ORDER BY id
        """, (args.student,))
        return [dict(row) for row in rows], 0
    return reserve(db, args.student, args.equipment)


def main():
    args = parse_args()
    try:
        with closing(sqlite3.connect(args.db)) as db, db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys = ON")
            initialize(db)
            payload, status = execute(db, args)
    except sqlite3.Error:
        payload, status = {"error": "database_error"}, 5
    stream = sys.stdout if status == 0 else sys.stderr
    stream.buffer.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
    return status


if __name__ == "__main__":
    sys.exit(main())
