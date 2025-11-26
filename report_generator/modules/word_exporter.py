from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement, qn
from typing import Dict, List, Optional, Any
import re
import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入公式转换器
try:
    from modules.formula_converter import FormulaConverter
except ImportError:
    logger.warning("无法导入FormulaConverter")

# 条件导入，支持直接运行或作为包的一部分运行
try:
    # 尝试相对导入
    from .markdown_to_word_converter import MarkdownToWordConverter
except ImportError:
    # 如果相对导入失败，尝试直接导入
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from modules.markdown_to_word_converter import MarkdownToWordConverter
    except ImportError:
        # 如果都失败，创建一个简单的转换器类作为备用
        class MarkdownToWordConverter:
            def convert_sections(self, sections, output_path):
                print(f"警告: MarkdownToWordConverter未找到，将使用原始导出逻辑")
                # 创建一个新的Document对象并实现基本导出功能
                doc = Document()
                
                # 确保输出目录存在
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # 简单地将内容添加到文档中
                if 'title' in sections:
                    doc.add_heading(sections['title'].split('\n')[0], 0)  # 只添加第一行作为标题
                    
                # 添加其他部分
                for module_name, content in sections.items():
                    if module_name != 'title' and content:
                        doc.add_heading(f"{module_name.capitalize()}", level=1)
                        doc.add_paragraph(content)
                
                doc.save(output_path)
                print(f"文档已保存到: {output_path}")
                return True


class WordExporter:
    """
    Word格式报告导出器，将生成的报告内容转换为格式化的Word文档
    """
    
    # 模块标题映射
    MODULE_TITLES = {
        'title': '标题页',
        'introduction': '一、引言',
        'background': '二、实验背景与原理',
        'implementation': '三、实验实现',
        'results': '四、实验结果',
        'analysis': '五、结果分析',
        'conclusion': '六、结论',
        'references': '七、参考文献'
    }
    
    def __init__(self):
        """
        初始化Word导出器
        """
        self.document = Document()
        self._setup_document_styles()
        
        # 初始化公式转换器
        try:
            from modules.formula_converter import FormulaConverter
            self.formula_converter = FormulaConverter()
        except ImportError:
            self.formula_converter = None
            logger.warning("公式转换器未找到，将跳过公式转换")
    
    def _setup_document_styles(self):
        """
        设置文档样式
        """
        # 获取或创建样式
        styles = self.document.styles
        
        # 设置正文样式
        normal_style = styles['Normal']
        font = normal_style.font
        font.name = '微软雅黑'
        font.size = Pt(12)
        font.color.rgb = RGBColor(0, 0, 0)  # 确保为黑色
        
        # 创建标题样式
        try:
            title_style = styles.add_style('ReportTitle', WD_STYLE_TYPE.PARAGRAPH)
            title_font = title_style.font
            title_font.name = '微软雅黑'
            title_font.size = Pt(24)
            title_font.bold = False  # 移除粗体
            title_font.color.rgb = RGBColor(0, 0, 0)  # 设置为黑色
            
            # 设置段落格式
            title_para_format = title_style.paragraph_format
            title_para_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_para_format.space_after = Pt(18)
        except:
            pass  # 如果样式已存在则忽略
        
        # 创建一级标题样式
        try:
            heading1_style = styles.add_style('ReportHeading1', WD_STYLE_TYPE.PARAGRAPH)
            heading1_font = heading1_style.font
            heading1_font.name = '微软雅黑'
            heading1_font.size = Pt(16)
            heading1_font.bold = False  # 移除粗体
            heading1_font.color.rgb = RGBColor(0, 0, 0)  # 设置为黑色
            
            # 设置段落格式
            heading1_para_format = heading1_style.paragraph_format
            heading1_para_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            heading1_para_format.space_before = Pt(12)
            heading1_para_format.space_after = Pt(12)
            heading1_para_format.keep_with_next = True
        except:
            pass
        
        # 创建代码样式
        try:
            code_style = styles.add_style('CodeBlock', WD_STYLE_TYPE.PARAGRAPH)
            code_font = code_style.font
            code_font.name = '微软雅黑'  # 修改为与正文字体一致
            code_font.size = Pt(11)  # 稍微缩小但保持相似
            code_font.color.rgb = RGBColor(0, 0, 0)  # 设置为黑色
            
            # 设置段落格式
            code_para_format = code_style.paragraph_format
            code_para_format.left_indent = Inches(0.5)
            code_para_format.space_before = Pt(6)
            code_para_format.space_after = Pt(6)
        except:
            pass
    
    def add_title_page(self, title_content: str):
        """
        添加标题页
        
        Args:
            title_content: 标题页内容
        """
        # 分割标题和其他信息
        lines = title_content.strip().split('\n')
        if lines:
            # 主标题
            title_para = self.document.add_paragraph()
            title_para.style = self.document.styles['ReportTitle']
            title_run = title_para.add_run(lines[0])
            title_run.bold = False  # 确保不是粗体
            
            # 其他信息
            for line in lines[1:]:
                if line.strip():
                    info_para = self.document.add_paragraph(line.strip())
                    info_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 添加分页符
        self.document.add_page_break()
    
    def _add_paragraph_with_formulas(self, text, formulas):
        """
        添加包含公式的段落，将公式转换为图片
        
        Args:
            text: 包含公式的文本
            formulas: 公式列表[(公式文本, 开始位置, 结束位置)]
        """
        try:
            # 排序公式
            formulas.sort(key=lambda x: x[1])
            
            # 处理文本和公式
            last_end = 0
            paragraph = self.document.add_paragraph()
            
            for formula_text, start_pos, end_pos in formulas:
                # 添加公式前的文本
                if start_pos > last_end:
                    text_before = text[last_end:start_pos]
                    if text_before.strip():
                        run = paragraph.add_run(text_before)
                        run.font.name = '微软雅黑'
                        run.font.size = Pt(12)
                
                # 转换公式为图片并插入
                try:
                    image_path = self.formula_converter.convert_formula_to_image(formula_text)
                    if image_path:
                        # 对于行内公式，直接插入
                        if formula_text.startswith('$') and formula_text.endswith('$') and formula_text.count('$') == 2:
                            # 行内公式
                            paragraph.add_run().add_picture(image_path, width=Inches(1.0))
                        else:
                            # 块级公式，单独一行并居中
                            paragraph.add_run()  # 确保当前段落结束
                            formula_paragraph = self.document.add_paragraph()
                            formula_paragraph.add_run().add_picture(image_path, width=Inches(3.0))
                            formula_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            
                            # 重新开始一个段落继续添加文本
                            paragraph = self.document.add_paragraph()
                    else:
                        # 如果转换失败，插入原始公式文本
                        run = paragraph.add_run(formula_text)
                        run.font.name = '微软雅黑'
                        run.font.size = Pt(12)
                        run.font.color.rgb = RGBColor(255, 0, 0)  # 红色标记失败的公式
                except Exception as e:
                    logger.error(f"转换公式失败: {e}")
                    # 插入原始公式文本
                    run = paragraph.add_run(formula_text)
                    run.font.name = '微软雅黑'
                    run.font.size = Pt(12)
                    run.font.color.rgb = RGBColor(255, 0, 0)  # 红色标记
                
                last_end = end_pos
            
            # 添加最后一个公式后的文本
            if last_end < len(text):
                text_after = text[last_end:]
                if text_after.strip():
                    run = paragraph.add_run(text_after)
                    run.font.name = '微软雅黑'
                    run.font.size = Pt(12)
        except Exception as e:
            logger.error(f"添加包含公式的段落时出错: {e}")
            # 出错时回退到普通文本
            self.document.add_paragraph(text)
    
    def add_section(self, module_name: str, content: str):
        """
        添加报告章节
        
        Args:
            module_name: 模块名称
            content: 章节内容
        """
        # 添加章节标题
        title = self.MODULE_TITLES.get(module_name, module_name)
        heading_para = self.document.add_paragraph()
        heading_para.style = self.document.styles['ReportHeading1']
        heading_run = heading_para.add_run(title)
        heading_run.bold = False  # 确保不是粗体
        
        logger.info(f"已添加章节: {title}")
        
        # 处理内容，支持代码块等格式化
        self._add_formatted_content(content)
    
    def _add_formatted_content(self, content: str):
        """
        添加格式化内容，支持代码块识别
        
        Args:
            content: 要添加的内容
        """
        # 尝试识别代码块（Markdown格式）
        code_block_pattern = r'```(?:\w*)\n(.*?)\n```'
        
        if '```' in content:
            # 有代码块
            parts = re.split(r'(```(?:\w*)\n.*?\n```)', content, flags=re.DOTALL)
            
            for part in parts:
                if part.startswith('```'):
                    # 代码块
                    # 提取代码内容
                    code_match = re.match(code_block_pattern, part, re.DOTALL)
                    if code_match:
                        code_content = code_match.group(1)
                        self._add_code_block(code_content)
                else:
                    # 普通文本
                    self._add_normal_text(part)
        else:
            # 普通文本
            self._add_normal_text(content)
    
    def _add_normal_text(self, text: str):
        """
        添加普通文本内容，自动检测并转换公式为图片，同时支持Markdown标题格式
        
        Args:
            text: 文本内容
        """
        # 按段落分割
        paragraphs = text.strip().split('\n')
        
        for para_text in paragraphs:
            if para_text.strip():
                # 检查是否是Markdown标题格式（以#开头）
                heading_match = re.match(r'^(#{1,6})\s+(.*)', para_text)
                if heading_match:
                    # 提取标题级别（#的数量）和标题内容
                    heading_level = len(heading_match.group(1))
                    heading_content = heading_match.group(2)
                    
                    # 根据标题级别设置字体大小
                    # 标题级别1-6对应字体大小24-14，依次递减
                    font_sizes = {
                        1: Pt(24),
                        2: Pt(22),
                        3: Pt(20),
                        4: Pt(18),
                        5: Pt(16),
                        6: Pt(14)
                    }
                    font_size = font_sizes.get(heading_level, Pt(12))
                    
                    # 创建段落并设置格式
                    para = self.document.add_paragraph()
                    run = para.add_run(heading_content)
                    run.font.name = '微软雅黑'
                    run.font.size = font_size
                    run.font.bold = False  # 保持与现有样式一致，不使用粗体
                    
                    # 设置段落格式
                    para.paragraph_format.space_before = Pt(12)
                    para.paragraph_format.space_after = Pt(12)
                # 检查是否是子标题（如 "1.1 什么什么"）
                elif re.match(r'^\d+\.\d+\s', para_text):
                    para = self.document.add_paragraph(para_text.strip())
                    # 移除粗体设置
                else:
                    # 检查是否有公式转换器且文本中可能包含公式
                    if self.formula_converter and ('$' in para_text or '$$' in para_text):
                        try:
                            # 检测段落中的公式
                            formulas = self.formula_converter.extract_formulas(para_text.strip())
                            if formulas:
                                self._add_paragraph_with_formulas(para_text.strip(), formulas)
                                continue
                        except Exception as e:
                            logger.error(f"处理公式时出错: {e}")
                    # 如果没有公式或处理失败，直接添加段落
                    self.document.add_paragraph(para_text.strip())
    
    def _add_code_block(self, code: str):
        """
        添加代码块
        
        Args:
            code: 代码内容
        """
        # 添加代码块前的空行
        self.document.add_paragraph()
        
        # 将代码添加为具有样式的段落
        code_lines = code.strip().split('\n')
        
        for line in code_lines:
            code_para = self.document.add_paragraph(line)
            code_para.style = self.document.styles['CodeBlock']
        
        # 添加代码块后的空行
        self.document.add_paragraph()
    
    def add_table_of_contents(self):
        """
        添加目录
        """
        # 在文档开头添加目录（假设标题页之后）
        # 注意：实际使用时可能需要先生成文档，然后再添加目录
        toc_para = self.document.add_paragraph()
        toc_run = toc_para.add_run('目录')
        toc_run.bold = True
        toc_run.font.size = Pt(16)
        toc_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        self.document.add_paragraph()  # 空行
        
        # 手动添加目录项（简化版）
        for module_name, title in self.MODULE_TITLES.items():
            if module_name != 'title':  # 标题页不加入目录
                toc_item = self.document.add_paragraph()
                toc_item.add_run(title).bold = False
                toc_item.paragraph_format.left_indent = Inches(0.25)
        
        self.document.add_page_break()
    
    def save(self, file_path: str) -> bool:
        """
        保存文档
        
        Args:
            file_path: 保存路径
            
        Returns:
            是否保存成功
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(file_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            self.document.save(file_path)
            print(f"成功保存文档到: {file_path}")
            return True
        except Exception as e:
            print(f"保存文档失败: {e}")
            return False
    
    def export_report(self, sections: Dict[str, str], output_path: str) -> bool:
        """
        导出完整报告
        
        Args:
            sections: 报告各部分内容（Markdown格式）
            output_path: 输出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            # 使用MarkdownToWordConverter将API返回的Markdown内容转换为Word
            converter = MarkdownToWordConverter()
            
            # 直接使用converter转换并保存
            return converter.convert_sections(sections, output_path)
        
        except Exception as e:
            print(f"导出报告失败: {e}")
            return False
    
    def export_report_original(self, sections: Dict[str, str], output_path: str) -> bool:
        """
        原始导出方法（保留用于向后兼容）
        
        Args:
            sections: 报告各部分内容
            output_path: 输出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            # 1. 添加标题页
            if 'title' in sections:
                self.add_title_page(sections['title'])
            else:
                # 默认标题页
                self.add_title_page("实验报告\n\n日期: " + self._get_current_date())
            
            # 2. 添加目录
            self.add_table_of_contents()
            
            # 3. 添加其他章节
            for module in ['introduction', 'background', 'implementation', 
                          'results', 'analysis', 'conclusion', 'references']:
                if module in sections and sections[module]:
                    self.add_section(module, sections[module])
            
            # 4. 保存文档
            return self.save(output_path)
        
        except Exception as e:
            print(f"导出报告失败: {e}")
            return False
    
    def _get_current_date(self) -> str:
        """
        获取当前日期字符串
        
        Returns:
            格式化的日期字符串
        """
        from datetime import datetime
        return datetime.now().strftime("%Y年%m月%d日")


if __name__ == "__main__":
    # 测试代码
    exporter = WordExporter()
    
    # 模拟报告内容
    test_sections = {
        'title': 'Python计算器程序实验报告\n\n作者: 测试用户\n日期: 2024年1月1日\n学号: 123456',
        'introduction': '本实验旨在实现一个简单的计算器程序，支持基本的加减乘除运算。通过本次实验，我们将学习Python编程的基础知识，包括函数定义、错误处理等概念。\n\n实验目标：\n1. 掌握Python函数的定义和使用\n2. 学习基本的错误处理机制\n3. 实现简单的数学运算功能',
        'implementation': '本次实验的代码实现主要包括四个基本运算函数：\n\n```python\ndef add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b == 0:\n        raise ValueError("除数不能为零")\n    return a / b\n```\n\n代码使用了简单的函数定义来实现各个运算功能，并在除法函数中添加了错误处理逻辑，防止除零错误。'
    }
    
    # 导出测试报告
    test_output = "test_report.docx"
    exporter.export_report(test_sections, test_output)
    print(f"测试报告已导出到: {test_output}")