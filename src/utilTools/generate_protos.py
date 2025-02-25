#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

def main():
    project_root = Path(__file__).parent.parent
    proto_dir = project_root / "proto"
    output_dir = project_root / "grpc_json_server" / "generated"

    output_dir.mkdir(parents=True, exist_ok=True)

    proto_file = proto_dir / "comms.proto"
    subprocess.run([
        "python", "-m", "grpc_tools.protoc",
        f"--proto_path={proto_dir}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        proto_file
    ], check=True)

    init_file = output_dir / "__init__.py"
    init_file.touch()

if __name__ == "__main__":
    main()
