import unittest
from unittest.mock import MagicMock, patch

from tests.support.path import setup_server_import_path

setup_server_import_path()


class TestGetLabelledTscript(unittest.TestCase):
    def _snippets(self, count: int):
        return [MagicMock(text=f"word{i}", start=float(i * 5)) for i in range(count)]

    @patch("transcript_labelling.get_orgs")
    @patch("transcript_labelling._classify_windows", return_value=[0, 1, 0])
    @patch("transcript_labelling.ytt_api.fetch")
    def test_ner_runs_only_on_ad_windows(self, mock_fetch, _mock_classify, mock_get_orgs):
        mock_fetch.return_value = self._snippets(25)
        mock_get_orgs.return_value = ["Acme"]

        from transcript_labelling import get_labelled_tscript  # noqa: E402

        segments = get_labelled_tscript("dQw4w9WgXcQ")

        mock_get_orgs.assert_called_once()
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[1]["orgs"], ["Acme"])
        self.assertEqual(segments[0]["orgs"], [])
        self.assertEqual(segments[2]["orgs"], [])

    @patch("transcript_labelling.model")
    @patch("transcript_labelling.tokenizer")
    def test_classify_windows_batches_inputs(self, mock_tokenizer, mock_model):
        import torch

        batch_sizes = []

        def tokenizer_fn(batch_texts, **kwargs):
            batch_sizes.append(len(batch_texts))
            tensor = MagicMock()
            tensor.to.return_value = tensor
            return {"input_ids": tensor, "attention_mask": tensor}

        mock_tokenizer.side_effect = tokenizer_fn

        call_index = {"value": 0}

        def fake_model(**_inputs):
            batch_size = batch_sizes[call_index["value"]]
            call_index["value"] += 1
            outputs = MagicMock()
            outputs.logits = torch.zeros(batch_size, 2)
            return outputs

        mock_model.side_effect = fake_model

        import transcript_labelling as tl  # noqa: E402

        original_batch_size = tl.BATCH_SIZE
        tl.BATCH_SIZE = 8
        try:
            labels = tl._classify_windows(["text"] * 20)
        finally:
            tl.BATCH_SIZE = original_batch_size

        self.assertEqual(labels, [0] * 20)
        self.assertEqual(mock_tokenizer.call_count, 3)
        self.assertEqual(mock_model.call_count, 3)


if __name__ == "__main__":
    unittest.main()
