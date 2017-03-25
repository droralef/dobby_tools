import unittest


import dobbyt
from dobbyt.stimuli import StimulusSelector
from dobbyt_testing import DummyStimulus


class StimulusSelectorTests(unittest.TestCase):

    def test_select(self):
        a = DummyStimulus()
        b = DummyStimulus()
        sel = StimulusSelector([["a", a], ["b", b]])
        self.assertIsNone(sel.selected_stimulus)

        sel.select("a")
        self.assertEqual(a, sel.selected_stimulus)

        sel.select("b")
        self.assertEqual(b, sel.selected_stimulus)


    def test_select_invalid(self):
        a = DummyStimulus()
        sel = StimulusSelector([["a", a]])
        self.assertRaises(ValueError, lambda: sel.select("c"))


if __name__ == '__main__':
    unittest.main()
