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
        with open(file_path, 'r', encoding='utf-8', newline='') as file:
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