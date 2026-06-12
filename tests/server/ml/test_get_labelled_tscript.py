import os
import unittest
from unittest.mock import MagicMock, patch

from tests.support.path import setup_server_import_path

setup_server_import_path()


class TestGetLabelledTscript(unittest.TestCase):
    def _snippets(self, count: int):
        return [MagicMock(text=f"word{i}", start=float(i * 5)) for i in range(count)]

    @patch("org_extractor.get_orgs")
    @patch("transcript_labelling._classify_windows", return_value=[0, 1, 0])
    @patch("transcript_labelling.ytt_api.fetch")
    def test_ner_runs_only_on_ad_windows(self, mock_fetch, _mock_classify, mock_get_orgs):
        mock_fetch.return_value = self._snippets(25)
        mock_get_orgs.return_value = ["Acme"]

        from transcript_labelling import get_labelled_tscript  # noqa: E402

        with patch.dict(os.environ, {"NER_ENABLED": "true"}, clear=False):
            segments = get_labelled_tscript("dQw4w9WgXcQ")

        mock_get_orgs.assert_called_once()
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[1]["orgs"], ["Acme"])
        self.assertEqual(segments[0]["orgs"], [])
        self.assertEqual(segments[2]["orgs"], [])

    @patch("org_extractor.get_orgs")
    @patch("transcript_labelling._classify_windows", return_value=[0, 1, 0])
    @patch("transcript_labelling.ytt_api.fetch")
    def test_ner_skipped_when_disabled(self, mock_fetch, _mock_classify, mock_get_orgs):
        mock_fetch.return_value = self._snippets(25)

        from transcript_labelling import get_labelled_tscript  # noqa: E402

        with patch.dict(os.environ, {"NER_ENABLED": "false"}, clear=False):
            segments = get_labelled_tscript("dQw4w9WgXcQ")

        mock_get_orgs.assert_not_called()
        self.assertEqual(segments[1]["orgs"], [])


if __name__ == "__main__":
    unittest.main()
