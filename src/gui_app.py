# tree_generator_project/src/gui_app.py
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


class TreeGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("文件树生成器 v2.1")
        master.geometry("1200x800")

        # 初始化变量
        self.depth_var = tk.IntVar(value=0)
        self.format_var = tk.StringVar(value="md")
        self.target_dir = os.getcwd()
        self.save_path = os.getcwd()  # 新增保存路径变量

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左半区优化
        left_frame = ttk.LabelFrame(main_frame, text="生成文件树")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # 控制按钮区（调整顺序）
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=5)

        # 第一行控件
        top_controls = ttk.Frame(control_frame)
        top_controls.pack(fill=tk.X)

        ttk.Button(top_controls, text="选择目录", command=self.select_directory).pack(
            side=tk.LEFT
        )
        ttk.Button(
            top_controls, text="选择生成位置", command=self.select_save_path
        ).pack(side=tk.LEFT, padx=5)
        ttk.Label(top_controls, text="保存位置:").pack(side=tk.LEFT)
        self.save_path_label = ttk.Label(top_controls, text=self.save_path)
        self.save_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 第二行控件
        bottom_controls = ttk.Frame(control_frame)
        bottom_controls.pack(fill=tk.X, pady=5)

        ttk.Label(bottom_controls, text="遍历深度:").pack(side=tk.LEFT)
        tk.Radiobutton(
            bottom_controls, text="当前", variable=self.depth_var, value=0
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            bottom_controls, text="一级", variable=self.depth_var, value=1
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            bottom_controls, text="穿透", variable=self.depth_var, value=-1
        ).pack(side=tk.LEFT)

        ttk.Label(bottom_controls, text="  格式:").pack(side=tk.LEFT)
        tk.Radiobutton(
            bottom_controls, text="MD", variable=self.format_var, value="md"
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            bottom_controls, text="TXT", variable=self.format_var, value="txt"
        ).pack(side=tk.LEFT)
        ttk.Button(bottom_controls, text="生成文件树", command=self.generate_tree).pack(
            side=tk.RIGHT
        )

        # 树状结构显示
        self.tree_text = scrolledtext.ScrolledText(left_frame, wrap=tk.NONE)
        self.tree_text.pack(fill=tk.BOTH, expand=True)

    def select_directory(self):
        dir_selected = filedialog.askdirectory(initialdir=self.target_dir)
        if dir_selected:
            self.target_dir = dir_selected
            self.tree_text.delete(1.0, tk.END)

    def select_save_path(self):
        path = filedialog.askdirectory(initialdir=self.save_path)
        if path:
            self.save_path = path
            self.save_path_label.config(text=path)

    def generate_tree(self):
        try:
            if not os.path.isdir(self.target_dir):
                raise ValueError("请先选择有效目录")

            depth = self.depth_var.get()
            format_type = self.format_var.get()

            # 生成带根目录的树结构
            dir_name = os.path.basename(self.target_dir)
            tree_lines = [f"{dir_name}/"]  # 添加根目录标题
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


if __name__ == "__main__":
    root = tk.Tk()
    app = TreeGeneratorApp(root)
    root.mainloop()
