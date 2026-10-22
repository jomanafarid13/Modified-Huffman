import streamlit as st

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

# Page Configuration

st.set_page_config(
    page_title="Modified Huffman",
    page_icon="📄",
    layout="wide"
)


# Session State

if "binary_data" not in st.session_state:
    st.session_state.binary_data = None

if "decompression_ready" not in st.session_state:
    st.session_state.decompression_ready = False


# Page Title

st.title("Modified Huffman Text Compressor")

st.write(
    "Compress text files using the Modified Huffman algorithm "
    "or decompress previously compressed files."
)

st.divider()


# Input Form

with st.form("modified_huffman_form"):

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["txt", "bin"]
    )

    operation = st.radio(
        "Choose an operation",
        ["Compression", "Decompression"],
        horizontal=True
    )

    min_limit = st.number_input(
        "Minimum Probability Limit",
        min_value=0.0,
        max_value=1.0,
        value=0.15,
        step=0.05
    )

    submit = st.form_submit_button("Submit")


# Process Input

if submit:

    if uploaded_file is None:
        st.warning("Please select a file.")

    elif operation == "Compression":

        if not uploaded_file.name.lower().endswith(".txt"):
            st.error("Please upload a .txt file for compression.")

        else:
            try:
                # Read the original text
                text = uploaded_file.getvalue().decode("utf-8")

                if not text:
                    st.warning("The uploaded file is empty.")

                else:
                    # Step 1: Calculate frequencies
                    frequencies = {}

                    from collections import Counter
                    frequencies = Counter(text)

                    st.subheader("1. Character Frequencies")
                    st.write(dict(frequencies))

                    # Step 2: Apply Modified Huffman
                    (
                        modified_freqs,
                        others_freqs,
                        fixed_codes
                    ) = apply_modification(
                        frequencies,
                        min_limit
                    )

                    st.subheader("2. Modified Frequencies")
                    st.write(modified_freqs)

                    st.subheader("3. Others Group")
                    st.write(others_freqs)

                    st.subheader("4. Fixed Codes")
                    st.write(fixed_codes)

                    # Step 3: Build Huffman Tree
                    root = build_huffman_tree(modified_freqs)

                    # Step 4: Generate Huffman Codes
                    codes_dict = generate_codes(root)

                    st.subheader("5. Huffman Codes")
                    st.write(codes_dict)

                    # Step 5: Encode text
                    bitstream = encode_text(
                        text,
                        codes_dict,
                        fixed_codes
                    )

                    st.subheader("6. Compression Results")

                    st.write(
                        f"Original text length: {len(text)} characters"
                    )

                    st.write(
                        f"Compressed bit length: {len(bitstream)} bits"
                    )

                    # Step 6: Convert bits to bytes
                    data, original_bit_length = bits_to_bytes(
                        bitstream
                    )

                    st.write(
                        f"Compressed data size: {len(data)} bytes"
                    )

                    # Step 7: Write compressed file
                    write_compressed_file(
                        output_path="compressed.bin",
                        data=data,
                        codes_dict=codes_dict,
                        fixed_codes=fixed_codes,
                        original_bit_length=original_bit_length,
                        original_char_count=len(text),
                        min_limit=min_limit
                    )

                    # Keep data for download
                    with open("compressed.bin", "rb") as file:
                        st.session_state.binary_data = file.read()

                    st.session_state.decompression_ready = False

                    st.success("File successfully compressed!")

            except Exception as e:
                st.error(f"Compression failed: {e}")

    elif operation == "Decompression":

        if not uploaded_file.name.lower().endswith(".bin"):
            st.error("Please upload a .bin file for decompression.")

        else:
            st.info(
                "The decompression interface is ready, but it must be "
                "connected to the actual decompression functions before "
                "it can restore the original text."
            )


# Download Compressed File


if (
    operation == "Compression"
    and st.session_state.binary_data is not None
):

    st.download_button(
        label="Download compressed.bin",
        data=st.session_state.binary_data,
        file_name="compressed.bin",
        mime="application/octet-stream"
    )