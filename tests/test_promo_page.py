"""Every number the promo page states comes from the repository, not from memory."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def page_text():
    return (ROOT/"docs/index.html").read_text(encoding="utf-8")


class PromoPageTests(unittest.TestCase):
    def test_stated_numbers_match_their_sources(self):
        text = page_text()
        # Calls: the committed measurement.
        line = next(l for l in (ROOT/"scripts/contenders_output.txt").read_text(encoding="utf-8").splitlines()
                    if l.startswith("JSON:"))
        calls = {b["calls"] for b in json.loads(line[len("JSON:"):])["board"] if b["calls"]}
        self.assertEqual(calls, {2871})
        self.assertIn("2,871 five-session calls", text)
        # Tests: the suite this file belongs to.
        stated = int(re.search(r"<strong>(\d+) automated tests</strong>", text).group(1))
        found = unittest.TestLoader().discover(str(ROOT/"tests"), pattern="test*.py").countTestCases()
        self.assertEqual(stated, found)
        # Deliberate bugs: the mutation list.
        mutations = (ROOT/"scripts/mutation_check.py").read_text(encoding="utf-8")
        listed = len(re.findall(r'^    \("', mutations.split("MUTATIONS = [", 1)[1].split("\n]", 1)[0], re.M))
        stated_bugs = int(re.search(r"<strong>(\d+) deliberate bugs</strong>", text).group(1))
        self.assertEqual(stated_bugs, listed)


if __name__ == "__main__":
    unittest.main()
