import unittest
from scripts.workflow_validator import validate_workflow, load_json, ROOT


class WorkflowValidationTests(unittest.TestCase):
    def test_main_workflow_has_nine_agents(self):
        flow = load_json(ROOT / 'workflow' / 'main-flow.json')
        self.assertGreaterEqual(len(flow.get('agents', [])), 8)
        self.assertEqual(len(flow.get('agents', [])), 9)

    def test_validation_script_passes(self):
        validate_workflow()

    def test_quality_gate_defined(self):
        flow = load_json(ROOT / 'workflow' / 'main-flow.json')
        acceptance_stage = next(s for s in flow['stages'] if s['id'] == 'acceptance-gate')
        gate = acceptance_stage.get('gate', {})
        self.assertGreaterEqual(gate.get('min_experience_score', 0), 9.5)
        self.assertGreaterEqual(gate.get('required_consecutive_checks', 0), 3)

    def test_screenshot_validation_policy(self):
        validation_flow = load_json(ROOT / 'workflow' / 'validation-flow.json')
        checks = {item['id']: item for item in validation_flow.get('checks', [])}
        self.assertIn('screenshot-validation', checks)
        self.assertTrue(checks['screenshot-validation'].get('required'))

        review = validation_flow.get('acceptance_policy', {}).get('screenshot_review', {})
        self.assertTrue(review.get('required'))
        self.assertGreaterEqual(review.get('dimensions', {}).get('ui_integrity', {}).get('min', 0), 9.5)
        self.assertGreaterEqual(review.get('dimensions', {}).get('ui_aesthetics', {}).get('min', 0), 9.0)
        self.assertGreaterEqual(review.get('dimensions', {}).get('ux_rationality', {}).get('min', 0), 9.0)
        self.assertGreaterEqual(review.get('evidence', {}).get('min_screenshots', 0), 10)
        scenes = set(review.get('evidence', {}).get('required_scenes', []))
        self.assertGreaterEqual(len(scenes), 10)
        self.assertIn('table-in-game', scenes)
        self.assertIn('reconnect-state', scenes)

        weights = review.get('rubric', {}).get('weights', {})
        self.assertEqual(set(weights.keys()), {'ui_integrity', 'ui_aesthetics', 'ux_rationality'})
        self.assertEqual(sum(weights.values()), 100)


if __name__ == '__main__':
    unittest.main()
