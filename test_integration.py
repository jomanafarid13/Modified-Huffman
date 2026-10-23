import os
import random
import string
from huffman import (
    get_frequencies, apply_modification,
    build_huffman_tree, generate_codes
)
from compression import encode_text, bits_to_bytes, write_compressed_file
from decompression import decompress_file


def run_case(name, content, min_limit):
    src, comp, out = "_t_in.txt", "_t_comp.bin", "_t_out.txt"
    with open(src, "w", encoding="utf-8", newline="") as f:
        f.write(content)

    try:
        freqs, text = get_frequencies(src)
        mf, of, fixed = apply_modification(freqs, min_limit)
        codes = generate_codes(build_huffman_tree(mf))
        bits = encode_text(text, codes, fixed)
        data, nbits = bits_to_bytes(bits)
        write_compressed_file(comp, data, codes, fixed, nbits, len(text), min_limit)
        decompress_file(comp, out)

        with open(src, "rb") as a, open(out, "rb") as b:
            ok = a.read() == b.read()
        status = "PASS" if ok else "FAIL"
        extra = f"others={len(of)} data={len(data)}B"
    except Exception as e:
        status, extra = "ERROR", repr(e)

    print(f"[{status}] {name:<28} min={min_limit:<5} {extra}")
    return status == "PASS"


if __name__ == "__main__":
    random.seed(1)
    big = "".join(random.choice("etaoin " * 20 + string.ascii_letters + "\n")
                  for _ in range(20000))

    cases = [
        ("single symbol",       "A" * 14),
        ("two symbols",         "AABB"),
        ("AAAAAAAAAABBBBBCD",   "A" * 10 + "B" * 5 + "CD"),
        ("all unique",          "abcdefghij"),
        ("english",             "the quick brown fox jumps over the lazy dog\n" * 5),
        ("arabic",              "السلام عليكم ورحمة الله وبركاته\nأهلا بكم\n"),
        ("mixed + emoji",       "Hello مرحبا 123 !@# 😀🔥\r\nline2\r\n"),
        ("spaces only",         "      "),
        ("newline only",        "\n"),
        ("big random",          big),
    ]
    limits = [0, 0.01, 0.05, 0.1, 0.15, 0.5, 0.9, 1]

    total = passed = 0
    for name, content in cases:
        for lim in limits:
            total += 1
            passed += run_case(name, content, lim)

    print(f"\n{passed}/{total} passed")

    for f in ("_t_in.txt", "_t_comp.bin", "_t_out.txt"):
        if os.path.exists(f):
            os.remove(f)