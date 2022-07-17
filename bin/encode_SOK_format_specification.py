import itertools
from pathlib import Path

_SELF_DIR = Path(__file__).absolute().resolve().parent


def in_batches(iterable, of_size=1):
    """
    Generator that yields generator slices of iterable.

    Since it is elegant and working flawlessly, it is shameles C/P from
    https://stackoverflow.com/questions/8991506/iterate-an-iterator-by-chunks-of-n-in-python/8998040#8998040

    Warning:
        Each returned batch should be completely consumed before next batch
        is yielded. See example below to better understand what that means.

    Example::

        g = (o for o in range(10))
        for batch in in_batches(g, of_size=3):
            print(list(batch))
        # [0, 1, 2]
        # [3, 4, 5]
        # [6, 7, 8]
        # [9]

        # And don't consume whole batch before yielding another one...
        g = list(range(10))
        for batch in in_batches(g, of_size=3):
            print( [next(batch), next(batch)] )
        # [0, 1]
        # [2, 3]
        # [4, 5]
        # [6, 7]
        # [8, 9]
    """
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, of_size)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk_it)


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
