import os
from typing import Optional
import PyPDF2
from docx import Document


class FileReader:
    """
    文件读取模块，支持读取PDF和Word文档
    """
    
    @staticmethod
    def read_pdf(file_path: str) -> Optional[str]:
        """
        读取PDF文件内容
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            提取的文本内容，失败返回None
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"读取PDF文件失败: {e}")
            return None
    
    @staticmethod
    def read_word(file_path: str) -> Optional[str]:
        """
        读取Word文档内容
        
        Args:
            file_path: Word文件路径
            
        Returns:
            提取的文本内容，失败返回None
        """
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"读取Word文件失败: {e}")
            return None
    
    @staticmethod
    def read_text(file_path: str) -> Optional[str]:
        """
        读取文本文件内容
        
        Args:
            file_path: 文本文件路径
            
        Returns:
            提取的文本内容，失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # 尝试使用其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    return file.read()
            except Exception as e:
                print(f"读取文本文件失败（GBK编码）: {e}")
                return None
        except Exception as e:
            print(f"读取文本文件失败: {e}")
            return None
    
    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        """
        根据文件扩展名自动选择适当的读取方法
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的文本内容，失败返回None
        """
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return FileReader.read_pdf(file_path)
        elif file_ext in ['.docx']:
            return FileReader.read_word(file_path)
        elif file_ext == '.txt':
            return FileReader.read_text(file_path)
        else:
            # 对于其他文件，尝试作为文本文件读取
            return FileReader.read_text(file_path)


if __name__ == "__main__":
    # 测试代码
    test_file = "example.pdf"  # 替换为实际的测试文件
    if os.path.exists(test_file):
        content = FileReader.read_file(test_file)
        if content:
            print(f"文件内容长度: {len(content)} 字符")
            print("文件前200个字符:")
            print(content[:200])