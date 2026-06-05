import unittest

from tests.support.path import setup_server_import_path

setup_server_import_path()

from youtube_url import YouTubeUrlError, parse_video_id  # noqa: E402


class TestYouTubeUrl(unittest.TestCase):
    def test_watch_url(self):
        self.assertEqual(
            parse_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_youtu_be_url(self):
        self.assertEqual(
            parse_video_id("https://youtu.be/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_embed_url(self):
        self.assertEqual(
            parse_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_missing_link(self):
        with self.assertRaisesRegex(YouTubeUrlError, "Missing required query parameter"):
            parse_video_id(None)

    def test_missing_video_id_param(self):
        with self.assertRaisesRegex(YouTubeUrlError, "unsupported YouTube URL format"):
            parse_video_id("https://www.youtube.com/watch")

    def test_invalid_url(self):
        with self.assertRaisesRegex(YouTubeUrlError, "not a valid URL"):
            parse_video_id("not-a-url")

    def test_invalid_video_id_length(self):
        with self.assertRaisesRegex(YouTubeUrlError, "11 characters"):
            parse_video_id("https://www.youtube.com/watch?v=short")


if __name__ == "__main__":
    unittest.main()
