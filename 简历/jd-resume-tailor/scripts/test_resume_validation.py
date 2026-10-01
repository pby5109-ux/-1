"""Regression scenarios; pass an existing approved JSON, never rewrite it."""
import sys
import unittest
from pathlib import Path
from validate_resume_content import load_json, validate, DEFAULT_PROFILE, DEFAULT_PROJECTS

FIXTURE = Path(sys.argv.pop(1)) if len(sys.argv) > 1 else None


class ResumeValidationTests(unittest.TestCase):
    def setUp(self):
        self.payload = load_json(FIXTURE)
        self.profile = load_json(DEFAULT_PROFILE)
        self.projects = load_json(DEFAULT_PROJECTS)

    def errors(self):
        return validate(self.payload, self.profile, self.projects)[0]

    def test_existing_approval(self):
        self.assertEqual(self.errors(), [])

    def test_unapproved(self):
        self.payload['approved'] = False
        self.assertTrue(self.errors())

    def test_target_is_not_skill_claim(self):
        self.payload['company'] = 'Linux Systems'
        self.payload['role'] = 'C++/Linux工程师'
        self.payload['header']['target'] = 'C++/Linux工程师'
        self.assertEqual(self.errors(), [])

    def test_unsupported_assertion(self):
        self.payload['skills'][0]['text'] = '熟练掌握嵌入式Linux驱动'
        self.assertTrue(self.errors())

    def test_header_cannot_bypass(self):
        self.payload['header']['tags'] = 'C++｜CAN'
        self.assertTrue(self.errors())

    def test_unknown_evidence(self):
        self.payload['skills'][0]['evidence_ids'] = ['missing.id']
        self.assertTrue(self.errors())

    def test_new_code_requires_hardware_boundary(self):
        bullet = self.payload['projects'][-1]['bullets'][0]
        bullet['evidence_ids'] = ['lora.oled_power_code']
        bullet['text'] = '实现OLED供电与隔离控制'
        self.assertTrue(self.errors())
        bullet['text'] += '，新增硬件待验证'
        self.assertEqual(self.errors(), [])

    def test_legacy_plan_stays_forbidden(self):
        self.payload['projects'][-1]['bullets'][0]['evidence_ids'] = ['lora.oled_power_plan']
        self.assertTrue(self.errors())

    def test_evidence_status_cannot_be_bypassed_by_policy(self):
        claim = self.projects['projects'][0]['claims'][0]
        claim['status'] = 'unresolved'
        self.payload['skills'][0]['evidence_ids'] = [claim['id']]
        self.assertTrue(self.errors())


if __name__ == '__main__':
    if FIXTURE is None:
        raise SystemExit('Usage: python test_resume_validation.py path/to/approved-content.json')
    unittest.main()
