import os
import tempfile
from collections import Counter

import streamlit as st

from huffman import (
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


# Page Configuration


st.set_page_config(
    page_title="Modified Huffman Compressor",
    page_icon="📚",
    layout="wide"
)


# Session State


if "compressed_data" not in st.session_state:
    st.session_state.compressed_data = None

if "compressed_filename" not in st.session_state:
    st.session_state.compressed_filename = None

if "decompressed_data" not in st.session_state:
    st.session_state.decompressed_data = None

if "decompressed_filename" not in st.session_state:
    st.session_state.decompressed_filename = None



# Helper Functions


def compress_text_file(file_bytes, min_limit):
    """
    Compress a UTF-8 text file using Modified Huffman.

    Returns:
        compressed_bytes: Complete compressed file.
        details: Dictionary containing compression information.
    """

    text = file_bytes.decode("utf-8")

    if not text:
        raise ValueError("The uploaded text file is empty.")

    # Calculate character frequencies.
    frequencies = Counter(text)

    # Apply Modified Huffman.
    modified_freqs, others_freqs, fixed_codes = (
        apply_modification(frequencies, min_limit)
    )

    # Build the Huffman tree.
    root = build_huffman_tree(modified_freqs)

    # Generate Huffman codes.
    codes_dict = generate_codes(root)

    # Encode the original text.
    bitstream = encode_text(
        text,
        codes_dict,
        fixed_codes
    )

    # Convert the bitstream into bytes.
    data, original_bit_length = bits_to_bytes(bitstream)

    # Create a temporary compressed file.
    with tempfile.NamedTemporaryFile(
        suffix=".bin",
        delete=False
    ) as temp_file:
        compressed_path = temp_file.name

    try:
        write_compressed_file(
            output_path=compressed_path,
            data=data,
            codes_dict=codes_dict,
            fixed_codes=fixed_codes,
            original_bit_length=original_bit_length,
            original_char_count=len(text),
            min_limit=min_limit
        )

        # Read the complete compressed file.
        with open(compressed_path, "rb") as file:
            compressed_bytes = file.read()

    finally:
        if os.path.exists(compressed_path):
            os.remove(compressed_path)

    details = {
        "frequencies": dict(frequencies),
        "modified_freqs": modified_freqs,
        "others_freqs": others_freqs,
        "fixed_codes": fixed_codes,
        "codes_dict": codes_dict,
        "original_chars": len(text),
        "original_bytes": len(file_bytes),
        "bit_length": original_bit_length,
        "data_bytes": len(data),
        "compressed_bytes": len(compressed_bytes),
    }

    return compressed_bytes, details


def decompress_binary_file(file_bytes):
    """
    Decompress a Modified Huffman binary file.

    Returns:
        original_text: Decoded text.
        output_bytes: UTF-8 bytes for downloading.
    """

    compressed_path = None
    decompressed_path = None

    try:
        # Save the uploaded binary file temporarily.
        with tempfile.NamedTemporaryFile(
            suffix=".bin",
            delete=False
        ) as temp_file:
            compressed_path = temp_file.name
            temp_file.write(file_bytes)

        # Create a temporary output text file.
        with tempfile.NamedTemporaryFile(
            suffix=".txt",
            delete=False
        ) as temp_file:
            decompressed_path = temp_file.name

        # Use the project's existing decompression function.
        original_text = decompress_file(
            compressed_path,
            decompressed_path
        )

        # Read the decompressed file bytes.
        with open(decompressed_path, "rb") as file:
            output_bytes = file.read()

        return original_text, output_bytes

    finally:
        # Delete temporary files.
        for path in (compressed_path, decompressed_path):
            if path and os.path.exists(path):
                os.remove(path)


# Page Title

st.title("📚 Modified Huffman Text Compressor")

st.write(
    "Compress UTF-8 text files using the Modified Huffman algorithm, "
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
        step=0.05,
        format="%.2f"
    )

    submit = st.form_submit_button("Start")



# Process Input

if submit:

    # Clear previous results before processing a new file.
    st.session_state.compressed_data = None
    st.session_state.compressed_filename = None
    st.session_state.decompressed_data = None
    st.session_state.decompressed_filename = None

    if uploaded_file is None:

        st.warning("Please select a file first.")

    elif operation == "Compression":

        if not uploaded_file.name.lower().endswith(".txt"):

            st.error("Please upload a .txt file for compression.")

        else:

            try:
                file_bytes = uploaded_file.getvalue()

                with st.spinner("Compressing your file..."):

                    compressed_bytes, details = compress_text_file(
                        file_bytes,
                        min_limit
                    )

                # Save the result in the session.
                st.session_state.compressed_data = compressed_bytes

                st.session_state.compressed_filename = (
                    os.path.splitext(uploaded_file.name)[0] + ".bin"
                )

                st.success("File compressed successfully!")

                
                # Character Frequencies
                

                st.subheader("1. Character Frequencies")
                st.json(details["frequencies"])

                
                # Modified Frequencies
                

                st.subheader("2. Modified Frequencies")
                st.json(details["modified_freqs"])

                
                # Others Group
                
                st.subheader("3. Others Group")

                if details["others_freqs"]:
                    st.json(details["others_freqs"])
                else:
                    st.info("No characters were assigned to Others.")

                
                # Fixed Codes
                

                st.subheader("4. Fixed Codes")

                if details["fixed_codes"]:
                    st.json(details["fixed_codes"])
                else:
                    st.info("No fixed codes were required.")

                
                # Huffman Codes
                

                st.subheader("5. Huffman Codes")
                st.json(details["codes_dict"])

                
                # Compression Results
                

                st.subheader("6. Compression Results")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Original Characters",
                        details["original_chars"]
                    )

                with col2:
                    st.metric(
                        "Original Size",
                        f'{details["original_bytes"]} bytes'
                    )

                with col3:
                    st.metric(
                        "Compressed File Size",
                        f'{details["compressed_bytes"]} bytes'
                    )

                col4, col5, col6 = st.columns(3)

                with col4:
                    st.metric(
                        "Encoded Bits",
                        details["bit_length"]
                    )

                with col5:
                    st.metric(
                        "Compressed Data",
                        f'{details["data_bytes"]} bytes'
                    )

                with col6:
                    original_size = details["original_bytes"]
                    compressed_size = details["compressed_bytes"]

                    if compressed_size > 0:
                        ratio = original_size / compressed_size

                        st.metric(
                            "Compression Ratio",
                            f"{ratio:.3f}"
                        )
                    else:
                        st.metric("Compression Ratio", "N/A")

                
                # Download Compressed File
                
                st.download_button(
                    label="⬇️ Download Compressed File",
                    data=st.session_state.compressed_data,
                    file_name=st.session_state.compressed_filename,
                    mime="application/octet-stream"
                )

            except Exception as error:
                st.error(f"Compression failed: {error}")

    elif operation == "Decompression":

        if not uploaded_file.name.lower().endswith(".bin"):

            st.error("Please upload a .bin file for decompression.")

        else:

            try:
                compressed_bytes = uploaded_file.getvalue()

                with st.spinner("Decompressing your file..."):

                    original_text, output_bytes = decompress_binary_file(
                        compressed_bytes
                    )

                # Save the result in the session.
                st.session_state.decompressed_data = output_bytes

                st.session_state.decompressed_filename = (
                    os.path.splitext(uploaded_file.name)[0]
                    + "_decompressed.txt"
                )

                st.success("File decompressed successfully!")

            
                # Decompression Results
                
                st.subheader("Decompression Results")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Recovered Characters",
                        len(original_text)
                    )

                with col2:
                    st.metric(
                        "Recovered File Size",
                        f"{len(output_bytes)} bytes"
                    )

                with st.expander("Preview recovered text"):
                    st.text(original_text[:5000])

                
                # Download Decompressed File
            

                st.download_button(
                    label="⬇️ Download Decompressed File",
                    data=st.session_state.decompressed_data,
                    file_name=st.session_state.decompressed_filename,
                    mime="text/plain"
                )

            except Exception as error:
                st.error(f"Decompression failed: {error}")



# Persistent Download Buttons


if (
    st.session_state.compressed_data is not None
    and st.session_state.compressed_filename is not None
):

    st.download_button(
        label="⬇️ Download Compressed File Again",
        data=st.session_state.compressed_data,
        file_name=st.session_state.compressed_filename,
        mime="application/octet-stream",
        key="download_compressed_again"
    )


if (
    st.session_state.decompressed_data is not None
    and st.session_state.decompressed_filename is not None
):

    st.download_button(
        label="⬇️ Download Decompressed File Again",
        data=st.session_state.decompressed_data,
        file_name=st.session_state.decompressed_filename,
        mime="text/plain",
        key="download_decompressed_again"
    )

        