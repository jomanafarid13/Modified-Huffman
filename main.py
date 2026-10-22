import heapq
from collections import Counter
import math

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def get_frequencies(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        if not text:
            print("Warning: The file is empty!")
            return {}, ""

        frequencies = Counter(text)
        return frequencies, text

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {}, ""

def apply_modification(frequencies, min_limit):
    if not frequencies:
        return {}, {}, {}

    total_chars = sum(frequencies.values())
    modified_freqs = {}
    others_freqs = {}

    for char, count in frequencies.items():
        prob = count / total_chars
        if prob <= min_limit:
            others_freqs[char] = count
        else:
            modified_freqs[char] = count

    if others_freqs:
        modified_freqs["Others"] = sum(others_freqs.values())

    fixed_codes = {}
    if others_freqs:
        num_others = len(others_freqs)
        fixed_bits_length = math.ceil(math.log2(num_others)) if num_others > 1 else 1
        
        for i, char in enumerate(others_freqs.keys()):
            fixed_codes[char] = format(i, f'0{fixed_bits_length}b')

    return modified_freqs, others_freqs, fixed_codes


def build_huffman_tree(modified_freqs):
    if not modified_freqs:
        return None

    heap = [HuffmanNode(char, freq) for char, freq in modified_freqs.items()]
    heapq.heapify(heap)

    if len(heap) == 1:
        return heap[0]

    while len(heap) > 1:
        left_node = heapq.heappop(heap)
        right_node = heapq.heappop(heap)

        merged = HuffmanNode(None, left_node.freq + right_node.freq)
        merged.left = left_node
        merged.right = right_node

        heapq.heappush(heap, merged)

    return heap[0]

def generate_codes(root, current_code="", codes_dict=None):
    if codes_dict is None:
        codes_dict = {}

    if root is None:
        return codes_dict

    if root.char is not None:
        if current_code == "":
            codes_dict[root.char] = "0"
        else:
            codes_dict[root.char] = current_code
        return codes_dict

    generate_codes(root.left, current_code + "0", codes_dict)
    generate_codes(root.right, current_code + "1", codes_dict)

    return codes_dict

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