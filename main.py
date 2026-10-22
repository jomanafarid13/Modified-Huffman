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

if __name__ == "__main__":

    file_path = "test.txt"
    min_limit = 0.15

    print(f"\n[1] Reading file: {file_path}")
    freqs, original_text = get_frequencies(file_path)

    if freqs:
        print(f"    Original Characters Count: {len(freqs)}")

        print(f"\n[2] Applying Modification (Min Limit = {min_limit})")
        modified_freqs, others_freqs, fixed_codes = apply_modification(freqs, min_limit)

        print(f"    Modified Frequencies (For Huffman): {modified_freqs}")
        print(f"    Others Frequencies: {others_freqs}")
        print(f"    Fixed Codes for Others: {fixed_codes}")

        print("\n[3] Building Huffman Tree...")
        root = build_huffman_tree(modified_freqs)

        print("\n[4] Generating Codes...")
        codes_dict = generate_codes(root)
        
        print("\n[5] Encoding text...")

        bitstream = encode_text(
            original_text,
            codes_dict,
            fixed_codes
        )

        print("Original text length:", len(original_text), "characters")
        print("Compressed bit length:", len(bitstream), "bits")

        print("\n[6] Converting bits to bytes...")

        data, original_bit_length = bits_to_bytes(bitstream)

        print("Compressed data size:", len(data), "bytes")

        print("\n[7] Writing compressed file...")

        write_compressed_file(
            output_path="compressed.bin",
            data=data,
            codes_dict=codes_dict,
            fixed_codes=fixed_codes,
            original_bit_length=original_bit_length,
            original_char_count=len(original_text),
            min_limit=min_limit
        )

        print("\n--- FINAL OUTPUT FOR TEAM ---")
        print("1. Huffman Codes Dictionary :")
        print(codes_dict)
        
        print("\n2. Fixed Codes for 'Others' group:")
        print(fixed_codes)

        print("Modified Frequencies to rebuild tree:")
        print(modified_freqs)
        print("Others Frequencies:")
        print(others_freqs)

        print("\n[Test] Simulating Compression:")
        test_char_normal = list(modified_freqs.keys())[0] if modified_freqs else 'A'
        
        if test_char_normal in codes_dict and test_char_normal != "Others":
            print(f"    Normal char '{test_char_normal}' -> Huffman Code: {codes_dict[test_char_normal]}")
            
        if others_freqs:
            test_char_other = list(others_freqs.keys())[0]
            others_huff_code = codes_dict.get("Others", "")
            other_fixed_code = fixed_codes.get(test_char_other, "")
            print(f"    Others char '{test_char_other}' -> '{others_huff_code}' (Others Huffman) + '{other_fixed_code}' (Fixed) = {others_huff_code + other_fixed_code}")

    else:
        print("Please create a 'test.txt' file with some text to test.")