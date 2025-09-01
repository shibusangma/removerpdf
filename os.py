import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
import tempfile
import os


def is_blank_page(page):
    """Check if a PDF page is blank by extracting text and checking if it's empty."""
    try:
        text = page.extract_text()
        # Remove whitespace and check if text is empty
        return not text or text.strip() == ""
    except Exception as e:
        st.warning(f"Error extracting text from page: {e}")
        return False


st.set_page_config(page_title="PDF Blank Page Remover", layout="centered")

st.title("📝 PDF Blank Page Remover")
st.markdown("Upload PDF files to remove blank pages automatically.")

uploaded_files = st.file_uploader(
    "Upload one or more PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.subheader(f"Processing: {uploaded_file.name}")

        try:
            # Create a temporary file to work with
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Read the PDF
            reader = PdfReader(tmp_file_path)
            total_pages = len(reader.pages)
            writer = PdfWriter()
            removed_count = 0

            # Add progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, page in enumerate(reader.pages):
                status_text.text(f"Processing page {i + 1}/{total_pages}...")
                progress_bar.progress((i + 1) / total_pages)

                if not is_blank_page(page):
                    writer.add_page(page)
                else:
                    removed_count += 1

            # Clean up temporary file
            os.unlink(tmp_file_path)

            if removed_count > 0:
                # Save cleaned PDF to memory
                output_buffer = io.BytesIO()
                writer.write(output_buffer)
                output_buffer.seek(0)

                st.success(
                    f"✅ Removed {removed_count} blank page(s) from {total_pages} total pages in **{uploaded_file.name}**"
                )

                st.download_button(
                    label=f"⬇️ Download Cleaned {uploaded_file.name}",
                    data=output_buffer,
                    file_name=f"cleaned_{uploaded_file.name}",
                    mime="application/pdf",
                    key=f"download_{uploaded_file.name}"  # Unique key for each button
                )
            else:
                st.info(f"📄 No blank pages found in **{uploaded_file.name}** (Total pages: {total_pages})")

        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
            # Clean up temporary file if it exists
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

else:
    st.info("👆 Please upload one or more PDF files to get started.")