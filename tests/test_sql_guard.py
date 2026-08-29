import sqlite3
import tempfile
import unittest
from pathlib import Path

from sql_guard import normalize_read_only_sql, query_db


class SqlGuardTest(unittest.TestCase):
    def test_rejects_state_changing_or_multiple_statements(self):
        unsafe_queries = [
            "DELETE FROM STUDENT",
            "SELECT * FROM STUDENT; DROP TABLE STUDENT",
            "WITH changed AS (DELETE FROM STUDENT RETURNING *) SELECT * FROM changed",
            "PRAGMA table_info(STUDENT)",
        ]
        for sql in unsafe_queries:
            with self.subTest(sql=sql), self.assertRaises(ValueError):
                normalize_read_only_sql(sql)

    def test_accepts_fenced_select(self):
        self.assertEqual(
            normalize_read_only_sql("```sql\nSELECT * FROM STUDENT;\n```"),
            "SELECT * FROM STUDENT",
        )

    def test_query_is_read_only_and_caps_results(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "students.db"
            connection = sqlite3.connect(database)
            connection.execute("CREATE TABLE STUDENT(NAME TEXT)")
            connection.executemany("INSERT INTO STUDENT VALUES (?)", [(str(i),) for i in range(105)])
            connection.commit()
            connection.close()

            _, rows, truncated = query_db("SELECT * FROM STUDENT", str(database))
            self.assertEqual(len(rows), 100)
            self.assertTrue(truncated)


if __name__ == "__main__":
    unittest.main()
