"""Prepare a project-local environment and a verified BiRefNet HR weight."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mirror", action="store_true", help="Use the explicit public mirror")
    parser.add_argument("--model-file", type=Path, help="Copy an existing verified ONNX model")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 13):
        raise SystemExit("Use Python 3.13 for this pinned deployment.")
    environment = ROOT / ".venv"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    runtime = ROOT / "runtime"
    runtime.mkdir(exist_ok=True)
    os.environ["TMP"] = str(runtime)
    os.environ["TEMP"] = str(runtime)
    os.environ["TMPDIR"] = str(runtime)
    if not python.is_file():
        try:
            import venv
        except ImportError:
            raise SystemExit("This Python lacks venv. Run setup.py using a full Python 3.13 installation.")
        venv.EnvBuilder(with_pip=True).create(environment)
    subprocess.run([str(python), "-m", "pip", "install", "--no-cache-dir", "-r", str(ROOT / "requirements.txt")], check=True)
    manifest = json.loads((ROOT / "model.json").read_text(encoding="utf-8"))
    output = runtime / manifest["name"]
    if output.exists():
        if output.stat().st_size == manifest["size"] and digest(output) == manifest["sha256"]:
            print("Dependencies and model are ready.")
            return
        raise SystemExit("Existing model failed verification; inspect it before replacing.")
    partial = output.with_suffix(".onnx.part")
    if args.model_file:
        if args.model_file.stat().st_size != manifest["size"] or digest(args.model_file) != manifest["sha256"]:
            raise SystemExit("Source model failed SHA-256 verification.")
        shutil.copyfile(args.model_file, partial)
    else:
        url = manifest["mirror"] if args.mirror else manifest["url"]
        offset = partial.stat().st_size if partial.exists() else 0
        headers = {"Range": f"bytes={offset}-"} if offset else {}
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
            if offset and response.status != 206:
                raise SystemExit("Server did not accept resume; retained the partial file.")
            if offset:
                expected = f"bytes {offset}-"
                if not response.headers.get("Content-Range", "").startswith(expected):
                    raise SystemExit("Incorrect resume offset.")
            with partial.open("ab" if offset else "wb") as stream:
                shutil.copyfileobj(response, stream, length=1024 * 1024)
    if partial.stat().st_size != manifest["size"] or digest(partial) != manifest["sha256"]:
        raise SystemExit("Model download incomplete or hash mismatch; partial retained.")
    partial.rename(output)
    print("Dependencies and model are ready.")


if __name__ == "__main__":
    main()