"""无屏自动阈值主机回归；不导入硬件库，不替代CanMV上板验证。"""
import ast
import math
import types
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / '矩形8.3.1.py'
text = SOURCE.read_text(encoding='utf-8-sig')
tree = ast.parse(text, filename=str(SOURCE))
ns = {'time': types.SimpleNamespace(ticks_diff=lambda a, b: ((a-b+32768) % 65536)-32768),
      'math': math, 'sqrt': math.sqrt, 'print': lambda *a: None}
ns['time'].sleep_ms = lambda ms: None
for node in tree.body:
    if isinstance(node, ast.Assign):
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                ns[target.id] = value
ns['image_shape'] = [ns['DETECT_HEIGHT'], ns['DETECT_WIDTH']]
definitions = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))]
exec(compile(ast.Module(body=definitions, type_ignores=[]), str(SOURCE), 'exec'), ns)


class FakeGray:
    def __init__(self, threshold=80, low=0, high=255):
        self.threshold, self.low, self.high = threshold, low, high
        self.estimates = 0
        self.binary_calls = []

    def get_histogram(self):
        self.estimates += 1
        return types.SimpleNamespace(
            get_statistics=lambda: types.SimpleNamespace(min=lambda: self.low, max=lambda: self.high),
            get_threshold=lambda: types.SimpleNamespace(value=lambda: self.threshold))

    def binary(self, thresholds):
        self.binary_calls.append(thresholds)
        return types.SimpleNamespace(to_rgb888=lambda: types.SimpleNamespace(to_numpy_ref=lambda: ('pixels', thresholds)))


def rectangle(x=100, y=50, w=200, h=200):
    return [x, y, w, h, x, y, x+w, y, x+w, y+h, x, y+h]


class AutoThresholdTests(unittest.TestCase):
    def setUp(self):
        ns['IDE_PREVIEW'] = False
        self.c = ns['AutoThreshold']()
        self.writes = []
        ns['uart'] = types.SimpleNamespace(write=self.writes.append)

    def test_startup_estimates_once(self):
        g = FakeGray(73)
        self.assertEqual(self.c.get(g), 73)
        self.assertEqual(self.c.get(g), 73)
        self.assertEqual((g.estimates, self.c.generation), (1, 1))

    def test_press_reestimates_and_holds(self):
        self.c.get(FakeGray(60))
        g = FakeGray(120)
        self.assertEqual(self.c.get(g), 60)
        self.assertEqual(g.estimates, 0)
        self.c.request()
        self.assertEqual(self.c.get(g), 120)
        self.assertEqual(self.c.generation, 2)

    def test_blank_frame_retry(self):
        self.assertIsNone(self.c.get(FakeGray(0, 0, 0)))
        self.assertTrue(self.c.pending)
        self.assertIsNone(self.c.value)
        self.assertEqual(self.c.get(FakeGray(90)), 90)

    def test_failed_reestimate_never_uses_stale_value(self):
        self.c.get(FakeGray(70))
        self.c.request()
        self.assertIsNone(self.c.get(FakeGray(255, 255, 255)))
        self.assertTrue(self.c.pending)
        self.assertEqual(self.c.get(FakeGray(130)), 130)

    def test_threshold_boundaries_and_invalid_values(self):
        for value in (0, 255):
            self.c.request()
            self.assertEqual(self.c.get(FakeGray(value)), value)
        for value in (-1, 256):
            self.c.request()
            with self.assertRaises(ValueError):
                self.c.get(FakeGray(value))
            self.assertTrue(self.c.pending)

    def test_preprocessing_and_cv_interface(self):
        g = FakeGray(80)
        raw = types.SimpleNamespace(to_grayscale=lambda: g)
        calls = []
        def detector(*args):
            calls.append(args)
            return [rectangle()]
        ns['cv_lite'] = types.SimpleNamespace(rgb888_find_rectangles_with_corners=detector)
        self.assertEqual(ns['process_frame'](raw, self.c), (200, 150))
        self.assertEqual(g.binary_calls, [[(0, 80)]])
        self.assertEqual(calls[0][0], [320, 480])
        self.assertEqual(calls[0][1], ('pixels', [(0, 80)]))
        self.assertEqual(calls[0][2:4], (50, 150))

    def test_blank_frame_skips_cv(self):
        ns['cv_lite'] = types.SimpleNamespace(rgb888_find_rectangles_with_corners=lambda *a: self.fail('should skip CV'))
        raw = types.SimpleNamespace(to_grayscale=lambda: FakeGray(0, 0, 0))
        self.assertIsNone(ns['process_frame'](raw, self.c))

    def test_no_candidate_and_malformed_candidate(self):
        for rects in (None, [], [[1, 2]], [rectangle(w=0)], [rectangle(w=20, h=20)]):
            self.assertIsNone(ns['select_rectangle_center'](rects))

    def test_largest_invalid_does_not_hide_valid_rectangle(self):
        invalid = [0, 0, 450, 300, 0, 0, 1, 0, 1, 1, 0, 1]
        self.assertEqual(ns['select_rectangle_center']([rectangle(), invalid]), (200, 150))

    def test_center_outside_image_rejected(self):
        self.assertIsNone(ns['select_rectangle_center']([rectangle(x=500)]))

    def test_center_and_uart_regression(self):
        self.assertEqual(ns['find_intersection'](100, 50, 300, 250, 100, 250, 300, 50), (200, 150))
        self.assertIsNone(ns['find_intersection'](0, 0, 1, 1, 2, 2, 3, 3))
        ns['send_center']((200, 150))
        ns['send_center']((479, 319))
        ns['send_center'](None)
        self.assertEqual(self.writes, ['[+040+010*]', '[-239-159*]', '(x=999,y=999)'])

    def test_key_bounce_hold_release(self):
        # 高有效：0=未按，1=按下
        key = ns['DebouncedPress'](0, 0)
        for raw, now in [(1, 1), (0, 10), (1, 20), (1, 49)]:
            self.assertFalse(key.update(raw, now))
        self.assertTrue(key.update(1, 50))
        self.assertFalse(key.update(1, 1000))
        self.assertFalse(key.update(0, 1010))
        self.assertFalse(key.update(0, 1040))
        self.assertFalse(key.update(1, 1050))
        self.assertTrue(key.update(1, 1080))

    def test_key_clock_wrap_and_boot_pressed(self):
        key = ns['DebouncedPress'](0, 65520)
        self.assertFalse(key.update(1, 65530))
        self.assertTrue(key.update(1, 24))
        key = ns['DebouncedPress'](1, 0)
        self.assertFalse(key.update(1, 300))

    def test_headless_camera_lifecycle(self):
        events = []
        ns['IDE_PREVIEW'] = False
        class Sensor:
            RGB888 = 1
            def reset(self): events.append('reset')
            def set_framesize(self, **kw): events.append(kw)
            def set_pixformat(self, fmt): events.append(fmt)
            def run(self): events.append('run')
            def stop(self): events.append('stop')
        ns['Sensor'] = Sensor
        ns['MediaManager'] = types.SimpleNamespace(init=lambda: events.append('media_init'), deinit=lambda: events.append('media_deinit'))
        ns['camera_init']()
        ns['camera_deinit']()
        self.assertEqual(events, ['reset', {'width': 480, 'height': 320}, 1, 'media_init', 'run', 'stop', 'media_deinit'])
        self.assertFalse(ns['media_started'])

    def test_virtual_preview_lifecycle_and_overlay(self):
        events = []
        class Sensor:
            RGB888 = 1
            def reset(self): pass
            def set_framesize(self, **kw): pass
            def set_pixformat(self, fmt): pass
            def run(self): events.append('run')
            def stop(self): events.append('stop')
        ns['Sensor'] = Sensor
        ns['IDE_PREVIEW'] = True
        ns['Display'] = types.SimpleNamespace(VIRT=99,
            init=lambda *a, **kw: events.append(('display', a, kw)),
            deinit=lambda: events.append('display_deinit'),
            show_image=lambda img: events.append(('show', img)))
        ns['MediaManager'] = types.SimpleNamespace(init=lambda: events.append('media_init'), deinit=lambda: events.append('media_deinit'))
        ns['camera_init']()
        self.assertEqual(events[0], ('display', (99,), {'width': 480, 'height': 320, 'fps': 30, 'to_ide': True}))
        ns['camera_deinit']()
        self.assertEqual(events[-3:], ['stop', 'display_deinit', 'media_deinit'])
        self.assertFalse(ns['display_started'])

    def test_selected_rectangle_overlay(self):
        lines, circles = [], []
        raw = types.SimpleNamespace(
            draw_line=lambda *a, **kw: lines.append(a),
            draw_circle=lambda *a, **kw: circles.append(a))
        self.assertEqual(ns['select_rectangle_center']([rectangle()], raw), (200, 150))
        self.assertEqual(lines, [(100, 50, 300, 50), (300, 50, 300, 250),
                                 (300, 250, 100, 250), (100, 250, 100, 50)])
        self.assertEqual(circles, [(200, 150, 3)])
        lines.clear()
        circles.clear()
        self.assertIsNone(ns['select_rectangle_center']([], raw))
        self.assertEqual((lines, circles), ([], []))

    def test_preview_failure_still_releases_media(self):
        ns['sensor'] = None
        ns['display_started'] = True
        ns['media_started'] = True
        events = []
        def fail(): raise RuntimeError('display failure')
        ns['Display'] = types.SimpleNamespace(deinit=fail)
        ns['MediaManager'] = types.SimpleNamespace(deinit=lambda: events.append('released'))
        with self.assertRaises(RuntimeError): ns['camera_deinit']()
        self.assertEqual(events, ['released'])

    def test_capture_loop_displays_every_frame_after_detection(self):
        saved = ns.copy()
        events, writes = [], []
        raw = types.SimpleNamespace(to_grayscale=lambda: FakeGray(42),
            draw_line=lambda *a, **kw: events.append('line'),
            draw_circle=lambda *a, **kw: events.append('circle'))
        rounds = [0]
        def exitpoint():
            rounds[0] += 1
            if rounds[0] > 2: raise KeyboardInterrupt()
        def detect(*args):
            events.append('detect')
            return [] if rounds[0] == 1 else [rectangle()]
        try:
            ns.update(IDE_PREVIEW=True, ticks_ms=lambda: 0,
                sensor=types.SimpleNamespace(snapshot=lambda: raw),
                RECALIBRATE_KEY=types.SimpleNamespace(value=lambda: 0),
                os=types.SimpleNamespace(exitpoint=exitpoint),
                Display=types.SimpleNamespace(show_image=lambda img: events.append('show')),
                cv_lite=types.SimpleNamespace(rgb888_find_rectangles_with_corners=detect),
                uart=types.SimpleNamespace(write=writes.append))
            with self.assertRaises(KeyboardInterrupt): ns['capture_picture']()
            self.assertEqual(events, ['detect', 'show', 'detect'] + ['line']*4 + ['circle', 'show'])
            self.assertEqual(writes, ['(x=999,y=999)', '[+040+010*]'])
        finally:
            ns.clear()
            ns.update(saved)

    def test_no_touch_or_old_manual_dependencies(self):
        used_names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        self.assertFalse(used_names & {'TOUCH', 'MODE_KEY', 'INC_KEY', 'DEC_KEY'})
        modules = [n.module for n in tree.body if isinstance(n, ast.ImportFrom)]
        self.assertIn('media.display', modules)
        compile(text, str(SOURCE), 'exec')


if __name__ == '__main__':
    unittest.main(verbosity=2)
