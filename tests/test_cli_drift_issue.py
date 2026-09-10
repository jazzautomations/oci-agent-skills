"""Notification behavior can be exercised without sending GitHub messages."""
import importlib.util
import json
from pathlib import Path
from unittest import TestCase, mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('drift_issue', ROOT / 'scripts/ci/drift_issue.py')
drift = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drift)


class DriftNotificationTests(TestCase):
    def test_no_drift_makes_no_requests(self):
        client = mock.Mock()
        self.assertEqual(drift.notify(' \n', client)['status'], 'no-drift')
        self.assertEqual(client.mock_calls, [])

    def test_manual_preview_never_publishes(self):
        client = mock.Mock()
        client.existing.return_value = []
        self.assertEqual(drift.notify('real change', client)['status'], 'would-create')
        client.create.assert_not_called()

    def test_rerun_reuses_existing_issue(self):
        client = mock.Mock()
        client.existing.side_effect = [[], [42]]
        client.create.return_value = 'https://github.com/example/repo/issues/42'
        self.assertTrue(drift.notify('change', client, publish=True)['published'])
        self.assertEqual(drift.notify('change', client, publish=True)['status'], 'existing')
        client.create.assert_called_once()

    def test_discovery_failure_does_not_create_duplicate(self):
        client = mock.Mock()
        client.existing.side_effect = RuntimeError('read failed')
        with self.assertRaises(RuntimeError):
            drift.notify('change', client, publish=True)
        client.create.assert_not_called()

    def test_large_diff_retains_link_and_fits_body_limit(self):
        client = mock.Mock()
        client.existing.return_value = []
        result = drift.notify('x' * 90000, client, publish=True,
                              evidence_url='https://github.com/example/repo/actions/runs/1')
        body = client.create.call_args.args[0]
        self.assertLessEqual(len(body), drift.BODY_LIMIT)
        self.assertIn('/actions/runs/1', body)
        self.assertTrue(result['diff_truncated'])

    def test_search_requires_exact_title(self):
        client = drift.GitHub('example/repo')
        with mock.patch.object(client, 'invoke', return_value=json.dumps([
            {'number': 1, 'title': 'Unrelated CLI required-flag drift question'},
            {'number': 2, 'title': drift.TITLE}])):
            self.assertEqual(client.existing(), [2])

    def test_truncated_discovery_stops(self):
        client = drift.GitHub('example/repo')
        with mock.patch.object(client, 'invoke', return_value=json.dumps(
                [{'number': i, 'title': drift.TITLE} for i in range(1000)])):
            with self.assertRaises(ValueError):
                client.existing()

    def test_malformed_discovery_stops(self):
        client = drift.GitHub('example/repo')
        with mock.patch.object(client, 'invoke', return_value='[{"title":"missing number"}]'):
            with self.assertRaises(ValueError):
                client.existing()
