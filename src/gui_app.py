# tree_generator_project/src/gui_app.py
import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


class TreeGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("文件树生成器 v4.0")
        master.geometry("1200x800")

        # 初始化所有变量
        self.depth_var = tk.IntVar(value=0)
        self.format_var = tk.StringVar(value="md")
        self.target_dir = os.getcwd()
        self.save_path = os.getcwd()  # 左侧保存路径
        self.create_path = os.getcwd()  # 右侧生成路径

        self.create_widgets()

    def create_widgets(self):
        """创建整个界面布局"""
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左半区 - 生成文件树
        left_frame = ttk.LabelFrame(main_frame, text="生成文件树")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # 左侧控制栏
        left_controls = ttk.Frame(left_frame)
        left_controls.pack(fill=tk.X, pady=5)

        # 第一行按钮
        top_controls = ttk.Frame(left_controls)
        top_controls.pack(fill=tk.X)
        ttk.Button(
            top_controls, text="选择目标文件夹", command=self.select_directory
        ).pack(side=tk.LEFT)
        ttk.Button(top_controls, text="保存位置", command=self.select_save_path).pack(
            side=tk.LEFT, padx=5
        )
        self.save_path_label = ttk.Label(top_controls, text=self.save_path)
        self.save_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 第二行选项
        bottom_controls = ttk.Frame(left_controls)
        bottom_controls.pack(fill=tk.X, pady=5)
        ttk.Label(bottom_controls, text="遍历深度:").pack(side=tk.LEFT)
        ttk.Radiobutton(
            bottom_controls, text="当前", variable=self.depth_var, value=0
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            bottom_controls, text="一级", variable=self.depth_var, value=1
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            bottom_controls, text="穿透", variable=self.depth_var, value=-1
        ).pack(side=tk.LEFT)
        ttk.Label(bottom_controls, text="  格式:").pack(side=tk.LEFT)
        ttk.Radiobutton(
            bottom_controls, text="MD", variable=self.format_var, value="md"
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            bottom_controls, text="TXT", variable=self.format_var, value="txt"
        ).pack(side=tk.LEFT)
        ttk.Button(bottom_controls, text="生成", command=self.generate_tree).pack(
            side=tk.RIGHT
        )

        # 左侧文本显示
        self.tree_text = scrolledtext.ScrolledText(left_frame, wrap=tk.NONE)
        self.tree_text.pack(fill=tk.BOTH, expand=True)

        # 右半区 - 反向生成
        right_frame = ttk.LabelFrame(main_frame, text="通过文件树生成文件结构")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # 右侧控制栏
        right_controls = ttk.Frame(right_frame)
        right_controls.pack(fill=tk.X, pady=5)

        ttk.Button(
            right_controls, text="选择生成位置", command=self.select_create_root
        ).pack(side=tk.LEFT)
        self.create_path_label = ttk.Label(right_controls, text=self.create_path)
        self.create_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 右侧输入框（添加height参数确保可见）
        self.input_text = scrolledtext.ScrolledText(
            right_frame, wrap=tk.NONE, height=15
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # 示例内容（确保插入位置正确）
        example = """project/
    ├── src/
    │   ├── __init__.py
    │   └── main.py
    ├── docs/
    │   └── README.md
    └── config.yaml"""
        self.input_text.insert(tk.END, example)

        # 生成按钮（修正打包参数）
        ttk.Button(
            right_frame, text="生成文件结构", command=self.create_structure
        ).pack(pady=5, anchor=tk.E)

    # 左侧功能方法
    def select_directory(self):
        """选择目标目录"""
        dir_selected = filedialog.askdirectory(initialdir=self.target_dir)
        if dir_selected:
            self.target_dir = dir_selected
            self.tree_text.delete(1.0, tk.END)

    def select_save_path(self):
        """选择左侧保存路径"""
        path = filedialog.askdirectory(initialdir=self.save_path)
        if path:
            self.save_path = path
            self.save_path_label.config(text=path)

    def generate_tree(self):
        """生成文件树逻辑"""
        try:
            if not os.path.isdir(self.target_dir):
                raise ValueError("请先选择有效目录")

            depth = self.depth_var.get()
            format_type = self.format_var.get()

            # 生成带根目录的树结构
            dir_name = os.path.basename(self.target_dir)
            tree_lines = [f"{dir_name}/"]
            tree_lines.extend(self._generate_tree(self.target_dir, depth))

            # 显示结果
            self.tree_text.delete(1.0, tk.END)
            self.tree_text.insert(tk.END, "\n".join(tree_lines))

            # 保存文件
            suffix_map = {0: "-0", 1: "-1", -1: "-2"}
            filename = f"{dir_name}_tree{suffix_map[depth]}.{format_type}"
            save_path = os.path.join(self.save_path, filename)

            with open(save_path, "w", encoding="utf-8") as f:
                if format_type == "md":
                    f.write(f"# {dir_name}\n\n")
                f.write("\n".join(tree_lines))

            messagebox.showinfo("保存成功", f"文件已保存至：\n{save_path}")

        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _generate_tree(self, root_dir, depth, current_depth=0):
        """递归生成树结构"""
        if depth != -1 and current_depth > depth:
            return []

        try:
            items = sorted(os.listdir(root_dir))
        except Exception as e:
            return [f"# 错误: {str(e)}"]

        tree = []
        for index, item in enumerate(items):
            path = os.path.join(root_dir, item)
            is_last = index == len(items) - 1
            prefix = "    " * current_depth
            line_prefix = prefix + ("└── " if is_last else "├── ")

            if os.path.isdir(path):
                tree.append(f"{line_prefix}{item}/")
                if depth == -1 or current_depth < depth:
                    tree.extend(self._generate_tree(path, depth, current_depth + 1))
            else:
                tree.append(f"{line_prefix}{item}")
        return tree

    # 右侧功能方法
    def select_create_root(self):
        """选择生成位置"""
        path = filedialog.askdirectory(initialdir=self.create_path)
        if path:
            self.create_path = path
            self.create_path_label.config(text=path)

    def create_structure(self):
        """核心生成方法"""
        md_content = self.input_text.get("1.0", tk.END).strip()
        if not md_content:
            messagebox.showwarning("警告", "请输入Markdown格式的文件树")
            return

        try:
            parsed = self.parse_markdown_tree(md_content)
            self.create_from_parsed(parsed)
            messagebox.showinfo("成功", f"已生成 {len(parsed)} 个文件/目录")
        except Exception as e:
            messagebox.showerror("错误", f"生成失败：{str(e)}")

    def parse_markdown_tree(self, content):
        """解析Markdown树结构（最终优化版）"""
        lines = [line for line in content.split("\n") if line.strip()]
        parsed = []
        stack = [(-1, "")]  # (缩进等级, 当前路径)

        for line in lines:
            # 计算缩进等级
            indent = len(re.findall(r"[│├└]", line)) * 4 + len(
                re.match(r"^[ \t]*", line).group()
            )
            line_content = re.sub(r"^[│├└─┬ \t]+", "", line).strip()

            # 判断是否为目录（终极解决方案）
            is_dir = "/" in line_content and (
                line_content.endswith("/")
                or any(c in line_content for c in "#;%")  # 包含注释特征时特殊处理
            )

            # 提取有效名称（终极清理逻辑）
            name = re.split(r"\s*[#;%]", line_content)[0]  # 简单粗暴分割注释
            name = name.rstrip(" _-")  # 保留左侧重要符号

            # 强制目录识别逻辑
            if "/" in name:
                name = name.split("/")[0] + "/"
                is_dir = True
            elif is_dir and not name.endswith("/"):
                name += "/"

            # 维护缩进栈
            while stack and indent <= stack[-1][0]:
                stack.pop()

            # 构建完整路径
            parent_path = stack[-1][1] if stack else ""
            full_path = os.path.join(parent_path, name.replace("/", ""))

            parsed.append(
                {
                    "type": "dir" if is_dir else "file",
                    "path": os.path.normpath(full_path).replace("\\", "/").rstrip("/")
                    + ("/" if is_dir else ""),
                    "depth": len(stack),
                }
            )

            if is_dir:
                stack.append((indent, full_path))

        return parsed

    def create_from_parsed(self, parsed):
        """根据解析结果创建结构"""
        for item in parsed:
            full_path = os.path.join(self.create_path, item["path"])
            try:
                if item["type"] == "dir":
                    os.makedirs(full_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    open(full_path, "a").close()  # 创建空文件
            except Exception as e:
                raise RuntimeError(f"创建失败 {full_path}: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TreeGeneratorApp(root)
    root.mainloop()
