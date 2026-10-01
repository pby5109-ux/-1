"""Behavior checks for schema-v2 and independent experience switches."""
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import build_current_resume as m

class CurrentResumeTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(m.CONTENT.read_text(encoding='utf-8'))

    def test_four_independent_combinations(self):
        cache=m.ROOT.parent/'定制投递/通用嵌入式-20260917-含实习双版本/中间文件'
        with tempfile.TemporaryDirectory(prefix='option-test-',dir=cache) as td:
            for internship in (True,False):
                for campus in (True,False):
                    with self.subTest(internship=internship,campus=campus):
                        out=Path(td)/f'{internship}-{campus}.docx'
                        m.build(self.data,out,campus,internship)
                        with ZipFile(out) as z:
                            root=E.fromstring(z.read('word/document.xml'))
                        txt=m.text(root)
                        self.assertEqual('烟台东方威思顿电气有限公司' in txt,internship)
                        self.assertEqual('校园经历' in txt,campus)
                        self.assertEqual('担任校学生会科创部部长' in txt,campus)
                        for p in self.data['projects']:
                            self.assertIn(p['name'],txt)
                            self.assertIn(p['intro']['text'],txt)
                            for bullet in p['bullets']: self.assertIn(bullet['text'],txt)
                        self.assertNotIn('自我评价',txt)
                        with self.assertRaises(ValueError): m.build(self.data,out,campus,internship)

    def test_unapproved_rejected(self):
        d=deepcopy(self.data);d['approved']=False
        with self.assertRaises(AssertionError): m.validate(d)

    def test_unknown_source_rejected(self):
        d=deepcopy(self.data);d['skills'][0]['source_refs']=['nonexistent']
        with self.assertRaises(AssertionError): m.validate(d)

    def test_two_campus_sentences_rejected(self):
        d=deepcopy(self.data);d['campus']['text']+='第二句话。'
        with self.assertRaises(AssertionError): m.validate(d)

if __name__=='__main__': unittest.main()
