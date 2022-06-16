from pathlib import Path

from sokoenginepy.io.utilities import in_batches

_SELF_DIR = Path(__file__).absolute().resolve().parent


def encode_spec_to_C_header():
    src_dir = (_SELF_DIR / ".." / "src").resolve()
    src_path = src_dir / "sokoenginepy" / "io" / "SOK_format_specification.txt"
    dst_path = (
        src_dir / "libsokoengine" / "io" / "collection" / "SOK_format_specification.h"
    )

    print(f"Generating \n    {dst_path}\nfrom\n    {src_path}")

    with open(src_path, "r") as f:
        data = "\n".join(_.strip() for _ in f.readlines())
        data = data.encode("UTF-8")

    with open(dst_path, "w") as f:
        f.write("static const std::string SOK_format_specification = {\n")

        lines = [
            "  " + ", ".join(batch)
            for batch in in_batches((f"0x{b:02x}" for b in data), of_size=12)
        ]

        f.write(",\n".join(lines))

        f.write("\n};\n")


if __name__ == "__main__":
    encode_spec_to_C_header()
