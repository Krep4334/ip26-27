import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class BookingContractTest(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        self.database = Path(directory) / "test.sqlite3"

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "src.equipment", "--db", str(self.database), *args],
            capture_output=True,
            encoding="utf-8",
            timeout=10,
        )

    def test_t1_books_available_equipment(self):
        """T-1 / FR-2 / US-2: проектор доступен."""
        result = self.cli("book", "--student", "7", "--equipment", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            json.loads(result.stdout),
            {"id": 1, "student_id": 7, "equipment_id": 1, "status": "reserved"},
        )

    def test_t2_rejects_second_booking_for_same_equipment(self):
        """T-2 / FR-2 / US-2 / NFR-3: проектор уже занят."""
        first = self.cli("book", "--student", "7", "--equipment", "1")
        self.assertEqual(first.returncode, 0, first.stderr)
        second = self.cli("book", "--student", "8", "--equipment", "1")
        self.assertEqual(second.returncode, 4)
        self.assertEqual(second.stdout, "")
        self.assertEqual(json.loads(second.stderr), {"error": "equipment_unavailable"})
        owner = self.cli("my-bookings", "--student", "7")
        other = self.cli("my-bookings", "--student", "8")
        self.assertEqual(owner.returncode, 0, owner.stderr)
        self.assertEqual(other.returncode, 0, other.stderr)
        self.assertEqual(json.loads(owner.stdout), [json.loads(first.stdout)])
        self.assertEqual(json.loads(other.stdout), [])
