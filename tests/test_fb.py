import tempfile
import unittest
from pathlib import Path

from raven_formats.fb import FBFileHeader, decompile, iter_entries


def entry(path: bytes, kind: bytes, payload: bytes) -> bytes:
    return FBFileHeader.pack(path, kind, len(payload)) + payload


class FbEntryTests(unittest.TestCase):
    def test_iterator_preserves_duplicate_paths(self):
        package = entry(b"same.xmlb", b"xml", b"first") + entry(
            b"same.xmlb", b"xml", b"second"
        )
        observed = list(iter_entries(package))
        self.assertEqual([item.file_path for item in observed], ["same.xmlb", "same.xmlb"])
        self.assertEqual([item.data for item in observed], [b"first", b"second"])

    def test_decompiler_uses_iterator_validation(self):
        package = entry(b"cut.xmlb", b"xml", b"payload")[:-1]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "cut.fb"
            source.write_bytes(package)
            with self.assertRaisesRegex(ValueError, "truncated FB entry"):
                decompile(source, root / "cut.xml")

    def test_truncated_header_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "truncated FB entry header"):
            list(iter_entries(b"partial"))


if __name__ == "__main__":
    unittest.main()
