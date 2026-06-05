import unittest
from unittest.mock import MagicMock, patch

from tests.support.path import setup_server_import_path

setup_server_import_path()

from transcript_labelling import TranscriptFetchError, get_labelled_tscript  # noqa: E402


class TestTranscriptFetch(unittest.TestCase):
    @patch("transcript_labelling.ytt_api.fetch")
    def test_fetch_failure_raises_transcript_fetch_error(self, mock_fetch):
        mock_fetch.side_effect = Exception("transcripts disabled")

        with self.assertRaises(TranscriptFetchError) as ctx:
            get_labelled_tscript("dQw4w9WgXcQ")

        self.assertIn("dQw4w9WgXcQ", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, Exception)

    @patch("transcript_labelling.ytt_api.fetch")
    def test_empty_transcript_returns_empty_list(self, mock_fetch):
        mock_fetch.return_value = []

        self.assertEqual(get_labelled_tscript("dQw4w9WgXcQ"), [])

    @patch("transcript_labelling.ytt_api.fetch")
    def test_short_transcript_returns_empty_list(self, mock_fetch):
        snippet = MagicMock(text="hello", start=0.0)
        mock_fetch.return_value = [snippet]

        self.assertEqual(get_labelled_tscript("dQw4w9WgXcQ"), [])


if __name__ == "__main__":
    unittest.main()
