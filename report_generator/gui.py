import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import sys
import subprocess
import threading
from pathlib import Path

class ReportGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("实验报告生成器")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.set_fonts()
        
        # 存储文件路径
        self.code_files = []
        self.requirement_files = []
        self.output_path = ""
        
        # 用于跟踪报告生成进度
        self.current_progress = 0
        
        # 创建界面
        self.create_widgets()
        
    def set_fonts(self):
        # 尝试设置支持中文的字体
        try:
            self.font = ("SimHei", 10)
            self.font_bold = ("SimHei", 10, "bold")
            self.font_large = ("SimHei", 12, "bold")
        except:
            # 回退到默认字体
            self.font = ("Arial", 10)
            self.font_bold = ("Arial", 10, "bold")
            self.font_large = ("Arial", 12, "bold")
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="实验报告自动生成器", font=self.font_large)
        title_label.pack(pady=10)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="15")
        file_frame.pack(fill=tk.X, pady=10)
        
        # 代码文件选择
        code_frame = ttk.LabelFrame(file_frame, text="代码文件 (可多选)")
        code_frame.pack(fill=tk.X, pady=5)
        
        # 代码文件列表区域
        code_files_frame = ttk.Frame(code_frame)
        code_files_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(code_files_frame, text="已选择文件:", font=self.font_bold).pack(side=tk.LEFT, padx=5)
        
        # 代码文件列表显示
        self.code_files_listbox = tk.Listbox(code_files_frame, height=3, font=self.font, selectmode=tk.EXTENDED)
        self.code_files_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 添加滚动条
        code_files_scrollbar = ttk.Scrollbar(code_files_frame, orient="vertical", command=self.code_files_listbox.yview)
        code_files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_files_listbox.config(yscrollcommand=code_files_scrollbar.set)
        
        # 按钮区域
        buttons_frame = ttk.Frame(code_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="浏览", command=self.browse_code_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="移除选中", command=self.remove_code_file).pack(side=tk.LEFT, padx=5)
        
        # 实验要求文件选择
        req_frame = ttk.Frame(file_frame)
        req_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(req_frame, text="实验要求:", font=self.font_bold).pack(side=tk.LEFT, padx=5)
        self.req_entry = ttk.Entry(req_frame, width=50, font=self.font)
        self.req_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(req_frame, text="添加", command=self.add_requirement_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(req_frame, text="添加多个", command=self.add_multiple_requirement_files).pack(side=tk.LEFT, padx=5)
        
        # 已选实验要求文件列表
        self.req_listbox = tk.Listbox(file_frame, height=3, font=self.font, selectmode=tk.EXTENDED)
        self.req_listbox.pack(fill=tk.X, pady=5, padx=5)
        ttk.Button(file_frame, text="移除选中", command=self.remove_requirement_file).pack(side=tk.RIGHT, pady=5)
        
        # 输出路径选择
        output_frame = ttk.Frame(file_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="输出路径:", font=self.font_bold).pack(side=tk.LEFT, padx=5)
        self.output_entry = ttk.Entry(output_frame, width=50, font=self.font)
        self.output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="浏览", command=self.browse_output_path).pack(side=tk.LEFT, padx=5)
        
        # 已移除进度条区域
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="执行日志", padding="15")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, font=self.font, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="生成报告", command=self.generate_report).pack(side=tk.RIGHT, padx=10)
        ttk.Button(button_frame, text="重置", command=self.reset_fields).pack(side=tk.RIGHT, padx=10)
    
    def browse_code_file(self):
        file_paths = filedialog.askopenfilenames(
            title="选择代码文件",
            filetypes=[("C/C++文件", "*.c *.cpp *.h *.hpp"), ("Python文件", "*.py"), ("文本文件", "*.txt"), ("所有文件", "*")]
        )
        if file_paths:
            # 添加新文件，避免重复
            for file_path in file_paths:
                if file_path not in self.code_files:
                    self.code_files.append(file_path)
                    self.code_files_listbox.insert(tk.END, os.path.basename(file_path))
                    self.log(f"已添加代码文件: {os.path.basename(file_path)}")
    
    def remove_code_file(self):
        selected_indices = self.code_files_listbox.curselection()
        if selected_indices:
            # 从后往前删除，避免索引变化问题
            for i in sorted(selected_indices, reverse=True):
                removed_file = self.code_files.pop(i)
                self.code_files_listbox.delete(i)
                self.log(f"已移除代码文件: {os.path.basename(removed_file)}")
    
    def reset_fields(self):
        self.code_files = []
        self.requirement_files = []
        self.output_path = ""
        
        self.code_entry.delete(0, tk.END) if hasattr(self, 'code_entry') else None
        self.req_entry.delete(0, tk.END)
        self.req_listbox.delete(0, tk.END)
        self.code_files_listbox.delete(0, tk.END) if hasattr(self, 'code_files_listbox') else None
        self.output_entry.delete(0, tk.END)
        
        # 已移除进度条相关重置代码
        self.log_text.delete(1.0, tk.END)
        
        self.log("已重置所有设置")
    
    def add_requirement_file(self):
        """添加单个实验要求文件"""
        file_path = filedialog.askopenfilename(
            title="选择实验要求文件",
            filetypes=[
                ("PDF文件", "*.pdf"),
                ("Word文件", "*.docx"),
                ("文本文件", "*.txt"),
                ("所有文件", "*")
            ]
        )
        if file_path:
            if file_path not in self.requirement_files:
                self.requirement_files.append(file_path)
                self.req_listbox.insert(tk.END, os.path.basename(file_path))
                self.log(f"已添加实验要求文件: {os.path.basename(file_path)}")
    
    def add_multiple_requirement_files(self):
        """添加多个实验要求文件"""
        file_paths = filedialog.askopenfilenames(
            title="选择多个实验要求文件",
            filetypes=[
                ("PDF文件", "*.pdf"),
                ("Word文件", "*.docx"),
                ("文本文件", "*.txt"),
                ("所有文件", "*")
            ]
        )
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.requirement_files:
                    self.requirement_files.append(file_path)
                    self.req_listbox.insert(tk.END, os.path.basename(file_path))
                    self.log(f"已添加实验要求文件: {os.path.basename(file_path)}")
    
    def add_multiple_requirement_files(self):
        file_paths = filedialog.askopenfilenames(
            title="选择多个实验要求文件",
            filetypes=[("PDF文件", "*.pdf"), ("Word文件", "*.docx"), ("文本文件", "*.txt"), ("所有文件", "*")]
        )
        for file_path in file_paths:
            if file_path not in self.requirement_files:
                self.requirement_files.append(file_path)
                self.req_listbox.insert(tk.END, os.path.basename(file_path))
                self.log(f"已添加实验要求文件: {os.path.basename(file_path)}")
    
    def remove_requirement_file(self):
        selected_indices = self.req_listbox.curselection()
        if selected_indices:
            # 从后往前删除，避免索引变化问题
            for i in sorted(selected_indices, reverse=True):
                removed_file = self.requirement_files.pop(i)
                self.req_listbox.delete(i)
                self.log(f"已移除实验要求文件: {os.path.basename(removed_file)}")
    
    def browse_output_path(self):
        file_path = filedialog.asksaveasfilename(
            title="保存实验报告",
            defaultextension=".docx",
            filetypes=[("Word文档", "*.docx"), ("所有文件", "*")]
        )
        if file_path:
            self.output_path = file_path
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, os.path.basename(file_path))
            self.log(f"已选择输出路径: {os.path.basename(file_path)}")
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def update_progress(self, value, status=""):
        # 更新实例变量中的进度值
        self.current_progress = value
        
        # 已移除进度条，保留此方法以兼容现有调用
        # 确保完成状态被正确显示
        if status:
            # 对于完成状态，确保它被记录到日志中
            self.log(status)
        elif value == 100:
            # 如果没有提供状态但进度值为100，记录完成状态
            self.log("完成")
        self.root.update_idletasks()
    
    def reset_fields(self):
        self.code_files = []
        self.requirement_files = []
        self.output_path = ""
        
        self.code_entry.delete(0, tk.END)
        self.req_entry.delete(0, tk.END)
        self.req_listbox.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)
        
        # 已移除进度条相关重置代码
        self.log_text.delete(1.0, tk.END)
        
        self.log("已重置所有设置")
    
    def validate_inputs(self):
        if not self.code_files:
            messagebox.showerror("错误", "请选择代码文件")
            return False
        
        if not self.requirement_files:
            messagebox.showerror("错误", "请至少添加一个实验要求文件")
            return False
        
        if not self.output_path:
            messagebox.showerror("错误", "请选择输出路径")
            return False
        
        # 检查文件是否存在
        for file_path in self.code_files + self.requirement_files:
            if not os.path.exists(file_path):
                messagebox.showerror("错误", f"文件不存在: {os.path.basename(file_path)}")
                return False
        
        return True
    
    def generate_report(self):
        if not self.validate_inputs():
            return
        
        # 禁用生成按钮防止重复点击
        # 在实际实现中应该找到并禁用生成按钮
        
        # 在单独的线程中运行报告生成，避免UI冻结
        thread = threading.Thread(target=self._run_report_generator)
        thread.daemon = True
        thread.start()
    
    def _run_report_generator(self):
        try:
            # 构建命令行参数
            python_exe = sys.executable
            main_script = os.path.join(os.path.dirname(__file__), "main.py")
            
            # 构建命令
            cmd = [python_exe, main_script]
            
            # 添加代码文件参数
            for code_file in self.code_files:
                cmd.extend(["--code_file", code_file])
            
            # 添加要求文件参数
            for req_file in self.requirement_files:
                cmd.extend(["--requirement_files", req_file])
            
            # 添加输出路径参数
            cmd.extend(["--output_file", self.output_path])
            
            # 添加自动模式参数
            cmd.append("--auto")
            
            # 获取项目根目录（父目录）
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            # 设置PYTHONPATH环境变量，确保子进程能找到report_generator模块
            env = os.environ.copy()
            # 在Windows上使用分号，在其他系统上使用冒号
            path_separator = ";" if os.name == "nt" else ":"
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = project_root + path_separator + env["PYTHONPATH"]
            else:
                env["PYTHONPATH"] = project_root
            
            # 添加PYTHONUNBUFFERED环境变量，确保输出不被缓冲，实时显示
            env["PYTHONUNBUFFERED"] = "1"
            
            self.log("开始生成实验报告...")
            self.update_progress(10, "准备中...")
            
            # 执行命令，使用设置了PYTHONPATH的环境变量
            # 设置bufsize=1以实现行缓冲模式，确保实时读取输出
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲模式
                env=env
            )
            
            # 实时读取输出
            self.update_progress(20, "正在处理...")
            
            # 模拟进度更新
            def update_progress_periodically():
                current_progress = 20
                while process.poll() is None:
                    # 增加进度更新间隔，减少GUI刷新频率
                    current_progress += 0.2  # 减慢进度增长
                    if current_progress < 90:  # 保留最后10%给最终完成
                        self.root.after(0, lambda cp=current_progress: 
                                       self.update_progress(cp, "正在生成报告..."))
                    # 增加等待时间，减少CPU占用
                    import time
                    time.sleep(0.5)  # 每500ms更新一次，而不是100ms
            
            progress_thread = threading.Thread(target=update_progress_periodically)
            progress_thread.daemon = True
            progress_thread.start()
            
            # 实时读取输出，确保与终端显示完全相同
            def read_output():
                # 分别处理stdout和stderr
                while True:
                    # 实时读取stdout
                    stdout_line = process.stdout.readline()
                    if stdout_line:
                        self.root.after(0, lambda l=stdout_line: self.log(l.strip()))
                    
                    # 实时读取stderr
                    stderr_line = process.stderr.readline()
                    if stderr_line:
                        self.root.after(0, lambda l=stderr_line: self.log(l.strip()))
                    
                    # 检查进程是否已结束
                    if process.poll() is not None:
                        # 读取剩余的输出
                        remaining_stdout = process.stdout.read()
                        if remaining_stdout:
                            for line in remaining_stdout.splitlines():
                                self.root.after(0, lambda l=line: self.log(l.strip()))
                        
                        remaining_stderr = process.stderr.read()
                        if remaining_stderr:
                            for line in remaining_stderr.splitlines():
                                self.root.after(0, lambda l=line: self.log(l.strip()))
                        break
                    
                    # 添加小延迟，避免CPU占用过高
                    import time
                    time.sleep(0.01)  # 10ms延迟
                
                # 进程完成后处理
                self.root.after(0, lambda: self._process_complete(process))
            
            # 在单独线程中读取输出，避免阻塞
            output_thread = threading.Thread(target=read_output)
            output_thread.daemon = True
            output_thread.start()
        except Exception as e:
            self.root.after(0, lambda: self.update_progress(100, "错误"))
            self.root.after(0, lambda: self.log(f"运行报告生成器时发生错误: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"运行报告生成器时发生错误:\n{str(e)}"))
            
    def _process_complete(self, process):
        """处理进程完成后的逻辑"""
        try:
            if process.returncode == 0:
                self.update_progress(100, "完成")
                self.log(f"实验报告已成功生成: {os.path.basename(self.output_path)}")
                messagebox.showinfo("成功", f"实验报告已成功生成！\n\n文件位置: {self.output_path}")
            else:
                self.update_progress(100, "失败")
                self.log(f"生成报告失败，退出代码: {process.returncode}")
                messagebox.showerror("错误", "生成报告时出现错误，请查看日志")
        except Exception as e:
            self.update_progress(100, "错误")
            self.log(f"处理完成状态时发生异常: {str(e)}")
            messagebox.showerror("错误", f"处理完成状态时发生异常: {str(e)}")
        finally:
            # 确保进度条完成
            self.update_progress(100, "")
            
    def _run_report_generator(self):
        try:
            # 构建命令行参数
            python_exe = sys.executable
            main_script = os.path.join(os.path.dirname(__file__), "main.py")
            
            # 构建命令
            cmd = [python_exe, main_script]
            
            # 添加代码文件参数
            for code_file in self.code_files:
                cmd.extend(["--code_file", code_file])
            
            # 添加要求文件参数
            for req_file in self.requirement_files:
                cmd.extend(["--requirement_files", req_file])
            
            # 添加输出路径参数
            cmd.extend(["--output_file", self.output_path])
            
            # 添加自动模式参数
            cmd.append("--auto")
            
            # 获取项目根目录（父目录）
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            # 设置PYTHONPATH环境变量，确保子进程能找到report_generator模块
            env = os.environ.copy()
            # 在Windows上使用分号，在其他系统上使用冒号
            path_separator = ";" if os.name == "nt" else ":"
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = project_root + path_separator + env["PYTHONPATH"]
            else:
                env["PYTHONPATH"] = project_root
            
            self.log("开始生成实验报告...")
            self.update_progress(10, "准备中...")
            
            # 执行命令，使用设置了PYTHONPATH的环境变量
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # 实时读取输出和更新进度
            self.update_progress(20, "正在处理...")
            
            # 设置一个定时器来检查进程状态
            def check_process():
                # 非阻塞方式检查进程是否结束
                returncode = process.poll()
                if returncode is not None:
                    # 进程已结束，读取输出
                    stdout, stderr = process.communicate()  # 这不会阻塞，因为进程已经结束
                    
                    # 更新日志
                    if stdout:
                        self.log(stdout.strip())
                    if stderr:
                        self.log(f"错误: {stderr.strip()}")
                    
                    # 处理完成
                    if returncode == 0:
                        self.update_progress(100, "完成")
                        self.log(f"实验报告已成功生成: {os.path.basename(self.output_path)}")
                        self.root.after(0, lambda: messagebox.showinfo("成功", 
                                   f"实验报告已成功生成！\n\n文件位置: {self.output_path}"))
                    else:
                        self.update_progress(100, "失败")
                        self.log(f"生成报告失败，退出代码: {returncode}")
                        self.root.after(0, lambda: messagebox.showerror("错误", 
                                   "生成报告时出现错误，请查看日志"))
                else:
                    # 进程仍在运行，更新进度并继续检查
                    # 使用实例变量跟踪进度
                    if self.current_progress < 90:
                        # 缓慢增加进度
                        new_progress = min(self.current_progress + 0.5, 90)
                        self.update_progress(new_progress, "正在生成报告...")
                    # 继续检查（每1000ms，减少GUI刷新频率）
                    self.root.after(1000, check_process)
            
            # 开始检查进程状态
            self.root.after(1000, check_process)
            
        except subprocess.TimeoutExpired:
            # 处理超时情况
            self.update_progress(100, "超时")
            self.log("生成报告超时")
            messagebox.showerror("错误", "生成报告超时，请尝试简化输入或增加超时时间")
            # 终止进程
            if 'process' in locals():
                process.kill()
        except Exception as e:
            self.update_progress(100, "错误")
            self.log(f"发生异常: {str(e)}")
            messagebox.showerror("错误", f"发生异常: {str(e)}")
        finally:
            # 确保GUI更新
            self.root.update_idletasks()


def main():
    root = tk.Tk()
    # 设置窗口图标（可选）
    # root.iconbitmap("icon.ico")
    
    # 设置样式
    style = ttk.Style()
    try:
        # 尝试设置现代化主题
        if sys.platform == "darwin":  # macOS
            style.theme_use("aqua")
        else:
            style.theme_use("clam")
    except:
        pass
    
    app = ReportGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()