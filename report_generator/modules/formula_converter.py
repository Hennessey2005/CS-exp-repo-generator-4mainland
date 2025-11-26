#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公式转图片工具
用于将LaTeX格式的数学公式转换为图片
"""

import os
import re
import tempfile
import base64
from typing import Optional, Tuple, List, Dict
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FormulaConverter:
    """
    数学公式转换工具，支持将LaTeX格式的公式转换为图片
    """
    
    def __init__(self):
        """
        初始化公式转换器
        """
        self.cache_dir = os.path.join(tempfile.gettempdir(), "formula_images")
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def convert_formula_to_image(self, formula: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        将LaTeX公式转换为图片
        
        Args:
            formula: LaTeX格式的公式
            output_path: 输出图片路径，若为None则生成临时文件
            
        Returns:
            图片文件路径，失败时返回None
        """
        try:
            # 移除公式周围的美元符号（如果有）
            clean_formula = self._clean_formula(formula)
            
            # 生成缓存文件路径
            formula_hash = self._hash_formula(clean_formula)
            cache_file = os.path.join(self.cache_dir, f"formula_{formula_hash}.png")
            
            # 如果缓存中已有该公式的图片，直接返回
            if os.path.exists(cache_file):
                logger.info(f"使用缓存的公式图片: {cache_file}")
                return cache_file
            
            # 使用MathJax API转换公式
            image_path = self._convert_with_mathjax(clean_formula, output_path or cache_file)
            
            if image_path and os.path.exists(image_path):
                logger.info(f"公式转换成功: {image_path}")
                return image_path
            else:
                logger.error("公式转换失败")
                return None
                
        except Exception as e:
            logger.error(f"转换公式时出错: {e}")
            return None
    
    def _clean_formula(self, formula: str) -> str:
        """
        清理公式，移除美元符号等
        
        Args:
            formula: 原始公式
            
        Returns:
            清理后的公式
        """
        # 移除单美元符号 $ 公式
        if formula.startswith('$') and formula.endswith('$') and formula.count('$') == 2:
            return formula[1:-1].strip()
        # 移除双美元符号 $$ 公式
        elif formula.startswith('$$') and formula.endswith('$$'):
            return formula[2:-2].strip()
        # 移除行内公式标记
        elif formula.startswith('\\(') and formula.endswith('\\)'):
            return formula[2:-2].strip()
        # 移除块级公式标记
        elif formula.startswith('\\[') and formula.endswith('\\]'):
            return formula[2:-2].strip()
        else:
            return formula.strip()
    
    def _hash_formula(self, formula: str) -> str:
        """
        生成公式的哈希值用于缓存
        
        Args:
            formula: 公式内容
            
        Returns:
            哈希字符串
        """
        import hashlib
        return hashlib.md5(formula.encode('utf-8')).hexdigest()[:10]
    
    def _convert_with_mathjax(self, formula: str, output_path: str) -> Optional[str]:
        """
        使用MathJax API转换公式
        
        Args:
            formula: LaTeX公式
            output_path: 输出图片路径
            
        Returns:
            图片路径
        """
        try:
            # 使用MathJax CDN API
            url = "https://math.now.sh/"
            params = {
                "from": formula,
                "color": "000000",  # 黑色
                "background": "ffffff",  # 白色背景
                "format": "png",
                "width": 400,  # 默认宽度
                "size": 16
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # 保存图片
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return output_path
            
        except Exception as e:
            logger.error(f"MathJax API调用失败: {e}")
            # 如果外部API失败，尝试使用备用方案
            return self._convert_with_alt_method(formula, output_path)
    
    def _convert_with_alt_method(self, formula: str, output_path: str) -> Optional[str]:
        """
        备用转换方法
        
        Args:
            formula: LaTeX公式
            output_path: 输出图片路径
            
        Returns:
            图片路径
        """
        try:
            # 尝试使用其他可用的公式渲染服务
            # 这里使用QuickLaTeX API作为备用
            url = "https://quicklatex.com/latex3.f"
            data = {
                "formula": formula,
                "fsize": 16,
                "fcolor": "000000",
                "mode": 0,
                "out": 1,
                "preamble": ""
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            # 解析响应获取图片URL
            response_text = response.text
            if "\n0" in response_text:
                # 成功的响应格式: \n0\n图片URL\n图片哈希\n"
                parts = response_text.split('\n')
                if len(parts) >= 2 and parts[1].startswith('http'):
                    img_url = parts[1]
                    # 下载图片
                    img_response = requests.get(img_url, timeout=10)
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)
                    return output_path
            
            logger.error(f"备用方法转换失败: {response_text}")
            return None
            
        except Exception as e:
            logger.error(f"备用方法调用失败: {e}")
            return None
    
    def extract_formulas(self, text: str) -> List[Tuple[str, int, int]]:
        """
        从文本中提取LaTeX公式
        
        Args:
            text: 包含公式的文本
            
        Returns:
            公式列表，每个元素为(公式文本, 开始位置, 结束位置)
        """
        formulas = []
        
        # 匹配块级公式 $$...$$
        block_pattern = re.compile(r'\$\$([\s\S]*?)\$\$')
        for match in block_pattern.finditer(text):
            formulas.append((match.group(0), match.start(), match.end()))
        
        # 匹配行内公式 $...$
        # 需要避免匹配已经被块级公式包含的部分
        processed_positions = set()
        inline_pattern = re.compile(r'\$([^$\n]+?)\$')
        for match in inline_pattern.finditer(text):
            # 检查是否在块级公式内
            is_inside_block = False
            for _, start, end in formulas:
                if start < match.start() < end:
                    is_inside_block = True
                    break
            
            # 避免重复处理
            if not is_inside_block and match.start() not in processed_positions:
                formulas.append((match.group(0), match.start(), match.end()))
                processed_positions.update(range(match.start(), match.end()))
        
        # 按位置排序
        formulas.sort(key=lambda x: x[1])
        return formulas
    
    def replace_formulas_with_placeholders(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        将文本中的公式替换为占位符
        
        Args:
            text: 原始文本
            
        Returns:
            (替换后的文本, 公式映射字典)
        """
        formulas = self.extract_formulas(text)
        if not formulas:
            return text, {}
        
        # 创建公式映射
        formula_map = {}
        result = text
        offset = 0
        
        # 从后往前替换，避免位置偏移问题
        for i, (formula, start, end) in enumerate(reversed(formulas)):
            placeholder = f"__FORMULA_{i}__"
            formula_map[placeholder] = formula
            
            # 调整位置并替换
            adjusted_start = start - offset
            adjusted_end = end - offset
            result = result[:adjusted_start] + placeholder + result[adjusted_end:]
            
            # 更新偏移量
            offset += (end - start) - len(placeholder)
        
        return result, formula_map
    
    def clean_cache(self):
        """
        清理公式图片缓存
        """
        try:
            for file in os.listdir(self.cache_dir):
                if file.startswith("formula_") and file.endswith(".png"):
                    os.remove(os.path.join(self.cache_dir, file))
            logger.info("公式图片缓存已清理")
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")


if __name__ == "__main__":
    # 测试代码
    converter = FormulaConverter()
    
    # 测试公式
    test_formula = "$$E = mc^2$$"
    print(f"测试公式: {test_formula}")
    
    # 转换公式
    image_path = converter.convert_formula_to_image(test_formula)
    if image_path:
        print(f"公式已转换为图片: {image_path}")
    else:
        print("公式转换失败")
    
    # 测试提取公式
    test_text = "这是一个公式 $F = ma$ 和另一个公式 $$E = mc^2$$。"
    print(f"\n测试文本: {test_text}")
    formulas = converter.extract_formulas(test_text)
    print(f"提取的公式数量: {len(formulas)}")
    for i, (formula, start, end) in enumerate(formulas):
        print(f"公式 {i+1}: {formula} (位置: {start}-{end})")
    
    # 测试替换公式
    replaced_text, formula_map = converter.replace_formulas_with_placeholders(test_text)
    print(f"\n替换后的文本: {replaced_text}")
    print(f"公式映射: {formula_map}")
