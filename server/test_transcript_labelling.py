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
            'orgs' : []
        }]

        self.assertEqual(compute_intervals(input), expected)

    def test_no_merge_basic(self): 
        input = [{
            'start' : 10, 
            'label' : 1,
            'orgs' : ['org1']
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
            'orgs' : ['org1']
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
            'orgs' : [] 
        }]

    def test_all_merge_basic_orgs_same(self): 
        input = [{
            'start' : 10, 
            'label' : 1, 
            'orgs' : ['org1'] 
        }, {
            'start' : 20, 
            'label' : 1, 
            'orgs' : ['org1'] 
        }, {
            'start' : 30, 
            'label' : 1, 
            'orgs' : [] 
        }]

        expected = [{
            'start_time': 10, 
            'end_time': 30, 
            'orgs' : ['org1'] 
        }]

    def test_all_merge_basic_orgs_dijoint(self): 
        input = [{
            'start' : 10, 
            'label' : 1, 
            'orgs' : ['org1'] 
        }, {
            'start' : 20, 
            'label' : 1, 
            'orgs' : ['org2'] 
        }, {
            'start' : 30, 
            'label' : 1, 
            'orgs' : [] 
        }]

        expected = [{
            'start_time': 10, 
            'end_time': 30, 
            'orgs' : ['org1', 'org2'] 
        }]

    def test_all_merge_basic_orgs_single(self): 
        input = [{
            'start' : 10, 
            'label' : 1, 
            'orgs' : ['org1', 'org2'] 
        }, {
            'start' : 20, 
            'label' : 1, 
            'orgs' : [] 
        }, {
            'start' : 30, 
            'label' : 1, 
            'orgs' : [] 
        }]

        expected = [{
            'start_time': 10, 
            'end_time': 30, 
            'orgs' : ['org1', 'org2'] 
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
            'orgs' : [] 
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
            'orgs' : [] 
        },{
            'start_time': 21, 
            'end_time': 25, 
            'orgs' : [] 
        }]

        self.assertEqual(compute_intervals(input), expected)
if __name__ == '__main__':
    unittest.main()