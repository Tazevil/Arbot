from pathlib import Path
import json
import os
import sys


def test_collect_and_save(tmp_path: Path):
    # Arrange test files
    img_a = tmp_path / "a.jpg"
    txt_b = tmp_path / "b.txt"
    sub = tmp_path / "sub"
    sub.mkdir()
    img_c = sub / "c.png"

    img_a.write_bytes(b"fakejpg")
    txt_b.write_text("not an image", encoding="utf-8")
    img_c.write_bytes(b"fakepng")

    # Ensure repository root on path
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from gpt4o_batch_analysis_oauth import collect_images, save_result

    images = collect_images(tmp_path)
    stems = {p.stem for p in images}
    assert stems == {"a", "c"}

    out_dir = tmp_path / "out"
    result = {"ok": True}
    out_path = save_result(out_dir, img_a, result)
    assert out_path.exists()
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data == result
