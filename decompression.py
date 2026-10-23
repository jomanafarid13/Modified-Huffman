import json
import struct

def read_compressed_file(path):
    with open(path, "rb") as f:
        header_len = struct.unpack(">I", f.read(4))[0]
        header = json.loads(f.read(header_len).decode("utf-8"))
        data = f.read()
    return header, data

def bytes_to_bits(data, bit_length):
    bits = "".join(format(b, "08b") for b in data)
    return bits[:bit_length]          

def decode_bits(bits, header):
    codes = header["codes_dict"]
    fixed = header["fixed_codes"]
    total = header["original_char_count"]

    rev_codes = {c: ch for ch, c in codes.items()}
    rev_fixed = {c: ch for ch, c in fixed.items()}
    fixed_len = len(next(iter(fixed.values()))) if fixed else 0

    out, cur, i = [], "", 0
    while i < len(bits) and len(out) < total:
        cur += bits[i]
        i += 1
        if cur in rev_codes:
            sym = rev_codes[cur]
            if sym == "Others":
                out.append(rev_fixed[bits[i:i + fixed_len]])
                i += fixed_len
            else:
                out.append(sym)
            cur = ""
    return "".join(out)

def decompress_file(compressed_path, output_path):
    header, data = read_compressed_file(compressed_path)
    bits = bytes_to_bits(data, header["original_bit_length"])
    text = decode_bits(bits, header)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return text