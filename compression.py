import json
import struct

def encode_text(text, codes_dict, fixed_codes):
    bitstream = ""

    for char in text:
        if char in fixed_codes:
            # The character belongs to the Others group
            bitstream += codes_dict["Others"]
            bitstream += fixed_codes[char]

        elif char in codes_dict:
            # The character has a normal Huffman code
            bitstream += codes_dict[char]

        else:
            raise ValueError(
                f"No code found for character: {repr(char)}"
            )

    return bitstream

def bits_to_bytes(bitstream):
    original_bit_length = len(bitstream)

    padding_length = (8 - original_bit_length % 8) % 8

    padded_bitstream = bitstream + ("0" * padding_length)

    data = bytearray()

    for i in range(0, len(padded_bitstream), 8):
        byte = padded_bitstream[i:i + 8]
        data.append(int(byte, 2))

    return bytes(data), original_bit_length

def write_compressed_file(
    output_path,
    data,
    codes_dict,
    fixed_codes,
    original_bit_length,
    original_char_count,
    min_limit
):
    header = {
        "codes_dict": codes_dict,
        "fixed_codes": fixed_codes,
        "original_bit_length": original_bit_length,
        "original_char_count": original_char_count,
        "min_limit": min_limit
    }

    # Convert the header dictionary to JSON bytes
    header_bytes = json.dumps(
        header,
        ensure_ascii=False
    ).encode("utf-8")

    # Store the header length using 4 bytes
    header_length = struct.pack(">I", len(header_bytes))

    # Write the complete compressed file
    with open(output_path, "wb") as file:
        file.write(header_length)
        file.write(header_bytes)
        file.write(data)

    print(f"Compressed file saved to: {output_path}")

    