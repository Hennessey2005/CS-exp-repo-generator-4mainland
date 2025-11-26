#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown到Word格式转换器
用于将API返回的Markdown格式报告转换为Word格式
"""

import os
import re
from typing import Dict
from .word_exporter import WordExporter

class MarkdownToWordConverter:
    """
    Markdown到Word转换工具，用于将API返回的Markdown格式内容转换为Word文档
    直接使用WordExporter实现转换功能
    """
    
    def __init__(self):
        """
        初始化转换器
        """
        pass
    
    def convert(self, markdown_content: str, output_path: str) -> bool:
        """
        将Markdown内容转换为Word文档
        
        Args:
            markdown_content: Markdown格式的内容
            output_path: 输出Word文档路径
            
        Returns:
            是否转换成功
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 创建WordExporter实例
            exporter = WordExporter()
            
            # 将单个内容作为一个section处理
            sections = {'content': markdown_content}
            
            # 导出到Word文档
            if exporter.export_report(sections, output_path):
                print(f"转换成功: {output_path}")
                return True
            return False
            
        except Exception as e:
            print(f"转换失败: {e}")
            return False
    
    def convert_sections(self, sections: Dict[str, str], output_path: str) -> bool:
        """
        将多个报告模块的Markdown内容合并并转换为Word文档
        
        Args:
            sections: 包含各模块内容的字典
            output_path: 输出Word文档路径
            
        Returns:
            是否转换成功
        """
        # 合并各模块内容为完整的Markdown文档
        markdown_content = self._merge_sections(sections)
        
        # 调用转换方法
        return self.convert(markdown_content, output_path)
    
    def _preprocess_line(self, line: str) -> str:
        """
        预处理文本行，实现以下功能：
        1. 根据行首#数量标记标题级别
        2. 删除所有反引号
        
        Args:
            line: 原始文本行
            
        Returns:
            处理后的文本行
        """
        # 处理标题行
        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            # 提取标题级别（#的数量）和标题内容
            heading_level = len(heading_match.group(1))
            heading_content = heading_match.group(2)
            
            # 删除内容中的反引号
            heading_content = heading_content.replace('`', '')
            
            # 不保留原始的#格式，直接返回处理后的标题内容
            return heading_content
        else:
            # 普通行，删除所有反引号
            return line.replace('`', '')
    
    def _merge_sections(self, sections: Dict[str, str]) -> str:
        """
        合并各模块内容为完整的Markdown文档
        
        Args:
            sections: 包含各模块内容的字典
            
        Returns:
            合并后的完整Markdown内容
        """
        # 移除了这里多余的 import re 语句
        
        # 按照报告模块的正确顺序合并内容
        ordered_sections = self._section_order()
        merged_content = []
        
        for section_name in ordered_sections:
            if section_name in sections and sections[section_name]:
                # 标题页特殊处理
                if section_name == 'title':
                    # 预处理标题页的每一行
                    processed_lines = []
                    for line in sections[section_name].split('\n'):
                        processed_lines.append(self._preprocess_line(line))
                    merged_content.append('\n'.join(processed_lines))
                else:
                    # 为其他模块添加适当的标题
                    section_title = self._get_section_title(section_name)
                    merged_content.append(f"# {section_title}")
                    
                    # 预处理模块内容的每一行
                    processed_lines = []
                    for line in sections[section_name].split('\n'):
                        processed_lines.append(self._preprocess_line(line))
                    merged_content.append('\n'.join(processed_lines))
                merged_content.append("\n")
        
        return "\n".join(merged_content)
    
    def _section_order(self) -> list:
        """
        返回报告模块的正确顺序
        
        Returns:
            模块名称列表
        """
        return ['title', 'introduction', 'background', 'implementation', 
                'results', 'analysis', 'conclusion', 'references']
    
    def _get_section_title(self, section_name: str) -> str:
        """
        根据模块名称获取对应的中文标题
        
        Args:
            section_name: 模块名称
            
        Returns:
            中文标题
        """
        title_map = {
            'introduction': '一、引言',
            'background': '二、实验背景与原理',
            'implementation': '三、实验实现',
            'results': '四、实验结果',
            'analysis': '五、结果分析',
            'conclusion': '六、结论',
            'references': '七、参考文献'
        }
        return title_map.get(section_name, section_name.capitalize())