"""Guard selected-frontier workflows against unauthenticated ledger preflights.

Historical ledger replays must authenticate old source bytes and the reviewed
live successor without changing the current selected record or cold check.
Dennis / antunishdPursuit, with substantial OpenAI Codex assistance.
Apache-2.0.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = (626, 741, 799)
SELECTED = 'python -B scripts/verify_selected_result.py'
LEDGER = 'python -B scripts/replay_historical_check.py tooling-ledger'
COLD = 'name: Cold finite replay and exact composition binding'
UNCHANGED = 'run: git diff --exit-code'
DIRECT = 'python -B scripts/verify_pr_reconciliation.py'


def verify_workflow(content):
    required = (SELECTED, LEDGER, COLD, UNCHANGED)
    if any(content.count(term) != 1 for term in required):
        raise ValueError('Missing or duplicate selected-family acceptance step')
    if DIRECT in content:
        raise ValueError('Historical ledger cannot run against live successor bytes')
    positions = [content.index(term) for term in required]
    if positions != sorted(positions):
        raise ValueError('Selected, ledger, cold and no-drift gates reordered')


class FrontierHistoricalPreflight(unittest.TestCase):
    def test_all_three_frontier_workflows_preserve_gates(self):
        for number in FAMILIES:
            with self.subTest(frontier=number):
                path = ROOT / '.github/workflows' / f'frontier{number}.yml'
                verify_workflow(path.read_text(encoding='utf-8'))

    def test_missing_weakened_and_reordered_gates_reject(self):
        original = (ROOT / '.github/workflows/frontier626.yml').read_text(
            encoding='utf-8')
        mutants = (
            original.replace(SELECTED, '# removed selected check', 1),
            original.replace(LEDGER, 'python -B scripts/replay_historical_check.py tooling-exact', 1),
            original.replace(LEDGER, DIRECT, 1),
            original.replace(UNCHANGED, '# removed tracked-byte check', 1),
            original.replace(SELECTED, '_TEMP_', 1).replace(
                LEDGER, SELECTED, 1).replace('_TEMP_', LEDGER, 1),
        )
        for index, mutant in enumerate(mutants):
            with self.subTest(mutant=index), self.assertRaises(ValueError):
                verify_workflow(mutant)


if __name__ == '__main__':
    unittest.main()
