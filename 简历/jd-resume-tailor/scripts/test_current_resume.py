"""Behavior checks for schema-v2 and independent experience switches."""
import json
import tempfile
import unittest
import io
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import build_current_resume as m

class CurrentResumeTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(m.CONTENT.read_text(encoding='utf-8'))
        self.legacy=json.loads((m.ROOT.parent/'定制投递/通用嵌入式-20260917-含实习双版本/排版定稿/approved-content.json').read_text(encoding='utf-8'))

    def test_current_long_snapshot_validates(self):
        self.assertTrue(m.validate(self.data))

    def test_current_short_campus_validates(self):
        d=deepcopy(self.data)
        d['campus']={'mode':'short', 'short_text':d['campus']['short_text'],
                     'source_refs':d['campus']['source_refs']}
        self.assertTrue(m.validate(d))

    def test_current_no_campus_validates(self):
        d=deepcopy(self.data);d['campus']={'mode':'none'}
        self.assertTrue(m.validate(d))

    def test_legacy_snapshot_validates(self):
        self.assertTrue(m.validate(self.legacy))

    def test_note_based_approval_requires_provenance(self):
        d=deepcopy(self.data);d['approval_record']={'approved_by':'user'}
        with self.assertRaisesRegex(ValueError, 'provenance'): m.validate(d)

    def test_current_snapshot_cannot_enter_legacy_renderer(self):
        with self.assertRaisesRegex(ValueError, 'pending|Dynamic snapshot|Legacy renderer'):
            m.validate_legacy_build(self.data)

    def test_pending_snapshot_cannot_bypass_guard_as_legacy(self):
        d=deepcopy(self.legacy);d['sync_status']='partial_pending_protected_wording_sync'
        with self.assertRaisesRegex(ValueError, 'pending'): m.validate_legacy_build(d)

    def test_four_independent_combinations(self):
        # Disposable test documents never enter a formal delivery or master directory.
        with tempfile.TemporaryDirectory(prefix='jd-legacy-options-') as td:
            for internship in (True,False):
                for campus in (True,False):
                    with self.subTest(internship=internship,campus=campus):
                        out=Path(td)/f'{internship}-{campus}.docx'
                        m.build(self.legacy,out,campus,internship)
                        with ZipFile(out) as z:
                            root=E.fromstring(z.read('word/document.xml'))
                        txt=m.text(root)
                        self.assertEqual('烟台东方威思顿电气有限公司' in txt,internship)
                        self.assertEqual('校园经历' in txt,campus)
                        self.assertEqual('担任校学生会科创部部长' in txt,campus)
                        for p in self.legacy['projects']:
                            self.assertIn(p['name'],txt)
                            self.assertIn(p['intro']['text'],txt)
                            for bullet in p['bullets']: self.assertIn(bullet['text'],txt)
                        self.assertNotIn('自我评价',txt)
                        with self.assertRaises(ValueError): m.build(self.legacy,out,campus,internship)

    def test_unapproved_rejected(self):
        d=deepcopy(self.data);d['approved']=False
        with self.assertRaises(ValueError): m.validate(d)

    def test_unknown_source_rejected(self):
        d=deepcopy(self.data);d['skills'][0]['source_refs']=['nonexistent']
        with self.assertRaises(ValueError): m.validate(d)

    def test_two_campus_sentences_rejected_only_by_legacy_build(self):
        d=deepcopy(self.legacy);d['campus']['text']+='第二句话。'
        self.assertTrue(m.validate(d))
        with self.assertRaisesRegex(ValueError, 'single-sentence'): m.validate_legacy_build(d)

    def test_unknown_long_campus_source_rejected(self):
        d=deepcopy(self.data);d['campus']['bullets'][0]['source_refs']=['missing.campus']
        with self.assertRaisesRegex(ValueError, 'unknown source_ref'): m.validate(d)

    def test_string_metadata_cannot_be_evidence(self):
        d=deepcopy(self.data);d['skills'][0]['source_refs']=['content_source']
        with self.assertRaisesRegex(ValueError, 'unknown source_ref'): m.validate(d)

    def test_prohibited_policy_cannot_be_hidden_by_local_source(self):
        d=deepcopy(self.data);d['sources']['skill.java']={'status':'user_provided'}
        d['skills'][0]['source_refs']=['skill.java']
        with self.assertRaisesRegex(ValueError, 'prohibited source_ref'): m.validate(d)

    def test_new_code_requires_qualification(self):
        d=deepcopy(self.data);it=d['projects'][0]['bullets'][0]
        it['source_refs']=['lora.oled_power_code'];it['text']='实现OLED供电隔离'
        with self.assertRaisesRegex(ValueError, 'qualifier'): m.validate(d)
        it['text']+='，硬件待验证'
        self.assertTrue(m.validate(d))

    def test_long_campus_must_not_be_silently_omitted(self):
        d=deepcopy(self.data);del d['campus']['bullets']
        with self.assertRaisesRegex(ValueError, 'Long campus bullets'): m.validate(d)

    def test_python_uses_later_confirmation(self):
        profile=m.load_json(m.DEFAULT_PROFILE)
        python=next(it for it in profile['skill_boundaries'] if it['id']=='skill.python')
        self.assertEqual(python['status'], 'user_confirmed')
        self.assertEqual(python['resume_policy'], 'allowed')

    def test_metric_correction_is_recorded(self):
        car=next(p for p in self.data['projects'] if p['id']=='car_contest')
        self.assertIn('98%', car['intro']['text'])
        fusion=next(it for it in car['bullets'] if it['label']=='融合定位')
        self.assertIn('98%', fusion['text'])
        self.assertIn('car_contest.ai_recognition_eval', fusion['source_refs'])

    def test_source_file_match_then_change_detected_without_rewriting(self):
        with tempfile.TemporaryDirectory(prefix='jd-source-check-') as td:
            source=Path(td)/'base.txt';source.write_bytes(b'first')
            d={'sources':{'base':{'path':'base.txt','sha256':m.digest(source)}}}
            original=deepcopy(d)
            self.assertEqual(m.source_file_issues(d, td), [])
            source.write_bytes(b'changed')
            self.assertIn('hash is stale', m.source_file_issues(d, td)[0])
            self.assertEqual(d, original)
            self.assertEqual(source.read_bytes(), b'changed')

    def test_missing_source_reported(self):
        with tempfile.TemporaryDirectory(prefix='jd-source-check-') as td:
            d={'sources':{'base':{'path':'missing.pdf','sha256':'a'*64}}}
            self.assertIn('missing', m.source_file_issues(d, td)[0])

    def test_directory_is_not_valid_source(self):
        with tempfile.TemporaryDirectory(prefix='jd-source-check-') as td:
            d={'sources':{'base':{'path':td,'sha256':'a'*64}}}
            self.assertIn('not a file', m.source_file_issues(d, td)[0])

    def test_invalid_digest_is_not_treated_as_match(self):
        d={'sources':{'base':{'path':'base.pdf','sha256':'see current file'}}}
        self.assertIn('invalid SHA256', m.source_file_issues(d)[0])

    def test_non_file_sources_and_metadata_are_not_opened(self):
        d={'sources':{'user-note':{'status':'user_provided','reference':'conversation'},
                      'content_source':'metadata, not an evidence object'}}
        self.assertEqual(m.source_file_issues(d), [])

    def test_strict_check_rejects_stale_file_but_regular_check_warns(self):
        with tempfile.TemporaryDirectory(prefix='jd-source-check-') as td:
            source=Path(td)/'base.txt';source.write_bytes(b'actual')
            d=deepcopy(self.legacy)
            d['sources']['baseline-20260917']['path']='base.txt'
            d['sources']['baseline-20260917']['sha256']='0'*64
            with redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
                self.assertEqual(m.check_content(d, workspace_root=td), 0)
                self.assertIn('hash is stale', output.getvalue())
                self.assertEqual(m.check_content(d, True, td), 2)

    def test_strict_check_accepts_matched_legacy_sources(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(m.check_content(self.legacy, True), 0)

    def test_strict_check_still_rejects_pending_wording_with_matching_hash(self):
        d=deepcopy(self.legacy);d['sync_status']='partial_pending_protected_wording_sync'
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(m.check_content(d, True), 2)

if __name__=='__main__': unittest.main()
