import unittest
from sql_profiler import SQLAnalyzer, SQLProfiler, IssueSeverity


class TestSQLProfiler(unittest.TestCase):
    def setUp(self):
        self.analyzer = SQLAnalyzer()

    def test_select_star_and_missing_limit(self):
        query = "SELECT * FROM users WHERE active = 1"
        res = self.analyzer.analyze(query)
        self.assertTrue(res.has_issues)
        codes = [i.code for i in res.issues]
        self.assertIn("PERF001", codes)  # SELECT *
        self.assertIn("PERF002", codes)  # Missing LIMIT

    def test_dangerous_unconstrained_update(self):
        query = "UPDATE users SET active = 0"
        res = self.analyzer.analyze(query)
        self.assertTrue(res.has_danger)
        codes = [i.code for i in res.issues]
        self.assertIn("DANG001", codes)

    def test_cartesian_join_detection(self):
        query = "SELECT orders.id FROM orders, customers WHERE orders.id = 5"
        res = self.analyzer.analyze(query)
        codes = [i.code for i in res.issues]
        self.assertIn("PERF004", codes)

    def test_n_plus_one_detection(self):
        profiler = SQLProfiler(n_plus_one_threshold=3)

        # Simulate N+1 query loop fetching author for each book
        for book_id in range(5):
            profiler.record_query(f"SELECT name, email FROM authors WHERE id = {book_id} LIMIT 1")

        n1 = profiler.detect_n_plus_one()
        self.assertEqual(len(n1), 1)
        pattern = list(n1.keys())[0]
        self.assertIn("WHERE ID = ?", pattern)
        self.assertEqual(n1[pattern], 5)

        report = profiler.generate_report()
        self.assertTrue(report["n_plus_one_detected"])
        self.assertEqual(report["total_queries"], 5)


if __name__ == "__main__":
    unittest.main()
