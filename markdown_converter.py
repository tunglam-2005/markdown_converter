import streamlit as st
import os
import tempfile
import nbformat
from nbconvert import MarkdownExporter
from docling.document_converter import DocumentConverter

# Cấu hình trang Streamlit
st.set_page_config(page_title="Đa năng Markdown Converter", page_icon="📄", layout="wide")

st.title("📄 Chuyển đổi tài liệu thành Markdown")
st.markdown("Tải lên nhiều tệp (PDF, DOCX, PPTX, HTML, hình ảnh, **Jupyter Notebook .ipynb**...) để chuyển sang định dạng Markdown.")

# Khởi tạo DocumentConverter và cache lại để tăng tốc cho các lần chạy sau
@st.cache_resource
def get_converter():
    return DocumentConverter()

converter = get_converter()

# Widget tải lên tệp tin, cho phép chọn nhiều tệp
uploaded_files = st.file_uploader("Kéo thả hoặc chọn các tệp tài liệu của bạn", accept_multiple_files=True)

if uploaded_files:
    st.write(f"**Đã tải lên {len(uploaded_files)} tệp. Đang sẵn sàng xử lý...**")
    
    # Nút bấm để bắt đầu quá trình xử lý hàng loạt
    if st.button("Bắt đầu chuyển đổi", type="primary"):
        
        # Tạo tiến trình tổng thể
        progress_bar = st.progress(0)
        
        for i, uploaded_file in enumerate(uploaded_files):
            st.divider()
            st.subheader(f"📁 Tệp: {uploaded_file.name}")
            
            # Lấy đuôi tệp và chuyển về chữ thường để dễ so sánh (VD: .IPYNB thành .ipynb)
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            # Lưu tệp tạm thời vào hệ thống
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
                
            try:
                with st.spinner(f"Đang phân tích và chuyển đổi {uploaded_file.name}..."):
                    
                    # Phân nhánh xử lý dựa trên định dạng tệp
                    if file_extension == '.ipynb':
                        # Xử lý bằng nbconvert cho Jupyter Notebook
                        with open(tmp_path, "r", encoding="utf-8") as f:
                            notebook_node = nbformat.read(f, as_version=4)
                        
                        markdown_exporter = MarkdownExporter()
                        # nbconvert trả về nội dung text và một dictionary chứa resources (ảnh...), ở đây ta chỉ lấy text
                        markdown_content, _ = markdown_exporter.from_notebook_node(notebook_node)
                    
                    else:
                        # Xử lý bằng Docling cho các định dạng còn lại (PDF, Word, Ảnh...)
                        result = converter.convert(tmp_path)
                        markdown_content = result.document.export_to_markdown()
                
                st.success("Chuyển đổi thành công!")
                
                # Hiển thị nút tải xuống cho tệp này
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.download_button(
                        label=f"⬇️ Tải file .md",
                        data=markdown_content,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}.md",
                        mime="text/markdown",
                        key=f"download_{i}" # Khóa độc nhất cho mỗi nút
                    )
                
                # Cho phép xem trước nội dung
                with st.expander("Xem trước nội dung Markdown"):
                    st.markdown(markdown_content)
                    
            except Exception as e:
                st.error(f"Đã xảy ra lỗi khi xử lý tệp {uploaded_file.name}: {str(e)}")
                
            finally:
                # Dọn dẹp tệp tạm sau khi xử lý xong (dù thành công hay thất bại)
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            
            # Cập nhật thanh tiến trình
            progress_bar.progress((i + 1) / len(uploaded_files))
            
        st.success("🎉 Đã hoàn tất xử lý tất cả các tệp!")