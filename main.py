import os
from huffman import (
    get_frequencies,
    apply_modification,
    build_huffman_tree,
    generate_codes
)
from compression import (
    encode_text,
    bits_to_bytes,
    write_compressed_file
)

from decompression import decompress_file


def build_codes(freqs, min_limit):
    modified_freqs, others_freqs, fixed_codes = apply_modification(freqs, min_limit)
    root = build_huffman_tree(modified_freqs)
    codes_dict = generate_codes(root)
    return modified_freqs, others_freqs, fixed_codes, codes_dict


if __name__ == "__main__":

    file_path =  "test.txt"
    min_limit = float(input("Minimum probability (e.g. 0.01): "))

    compressed_path = "compressed.bin"
    decompressed_path = "decompressed.txt"

    print(f"\n[1] Reading file: {file_path}")
    freqs, original_text = get_frequencies(file_path)

    if not freqs:
        print("Empty or missing file. Nothing to compress.")
        raise SystemExit

    print(f"    Distinct symbols: {len(freqs)} | Total chars: {len(original_text)}")

    print(f"\n[2] Applying modification (min limit = {min_limit})")
    modified_freqs, others_freqs, fixed_codes, codes_dict = build_codes(freqs, min_limit)
    print(f"    Normal symbols: {len(modified_freqs) - (1 if others_freqs else 0)}")
    print(f"    Symbols in Others: {len(others_freqs)}")

    print("\n[3] Huffman codes:")
    for sym, code in sorted(codes_dict.items(), key=lambda x: len(x[1])):
        print(f"    {repr(sym):>10} -> {code}")
    if fixed_codes:
        print("    Fixed codes for Others:")
        for sym, code in fixed_codes.items():
            print(f"    {repr(sym):>10} -> {code}")

    print("\n[4] Encoding...")
    bitstream = encode_text(original_text, codes_dict, fixed_codes)
    data, original_bit_length = bits_to_bytes(bitstream)

    print("[5] Writing compressed file...")
    write_compressed_file(
        output_path=compressed_path,
        data=data,
        codes_dict=codes_dict,
        fixed_codes=fixed_codes,
        original_bit_length=original_bit_length,
        original_char_count=len(original_text),
        min_limit=min_limit
    )

    print("\n[6] Decompressing...")
    decoded = decompress_file(compressed_path, decompressed_path)

    with open(file_path, "rb") as f1, open(decompressed_path, "rb") as f2:
        identical = f1.read() == f2.read()

    print("\n========== RESULTS ==========")
    print("Lossless (text equal)  :", decoded == original_text)
    print("Lossless (bytes equal) :", identical)

    orig_size = os.path.getsize(file_path)
    comp_size = os.path.getsize(compressed_path)
    print(f"Original size          : {orig_size} bytes")
    print(f"Compressed (with header): {comp_size} bytes")
    print(f"Compressed (data only)  : {len(data)} bytes")
    print(f"Ratio (with header)     : {orig_size / comp_size:.3f}")
    print(f"Ratio (data only)       : {orig_size / len(data):.3f}")

    # Comparison with standard Huffman (min_limit = 0)
    _, _, fc0, codes0 = build_codes(freqs, 0)
    bits0 = len(encode_text(original_text, codes0, fc0))
    print(f"\nStandard Huffman bits   : {bits0} ({(bits0 + 7) // 8} bytes)")
    print(f"Modified Huffman bits   : {original_bit_length} ({len(data)} bytes)")