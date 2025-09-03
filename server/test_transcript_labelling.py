import unittest
from transcript_labelling import compute_intervals

class TestTranscriptLabelling(unittest.TestCase):

    def test_no_merge_basic(self): 
        input = [{
            'start' : 10, 
            'label' : 1
        }, {
            'start' : 20, 
            'label' : 0
        }, {
            'start' : 30, 
            'label' : 1
        }]

        expected = [{
            'start_time': 10, 
            'end_time': 20, 
        }]

        self.assertEqual(compute_intervals(input), expected)


    def test_all_merge_basic(self): 
        input = [{
            'start' : 10, 
            'label' : 1
        }, {
            'start' : 20, 
            'label' : 1
        }, {
            'start' : 30, 
            'label' : 1
        }]

        expected = [{
            'start_time': 10, 
            'end_time': 30, 
        }]

        self.assertEqual(compute_intervals(input), expected)

    def test_no_overlap_hits_threshold_basic(self): 
        input = [{
            'start' : 10, 
            'label' : 1
        }, {
            'start' : 15, 
            'label' : 0
        }, {
            'start' : 20, 
            'label' : 1
        }, {
            'start' : 25, 
            'label' : 0
        }]

        expected = [{
            'start_time': 10, 
            'end_time': 25, 
        }]

    def test_no_overlap_no_threshold_basic(self): 
        input = [{
            'start' : 10, 
            'label' : 1
        }, {
            'start' : 15, 
            'label' : 0
        }, {
            'start' : 21, 
            'label' : 1
        }, {
            'start' : 25, 
            'label' : 0
        }]

        expected = [{
            'start_time': 10, 
            'end_time': 15, 
        },{
            'start_time': 21, 
            'end_time': 25, 
        }]

        self.assertEqual(compute_intervals(input), expected)
if __name__ == '__main__':
    unittest.main()