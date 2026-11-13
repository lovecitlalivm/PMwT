import tkinter as tk
from tkinter import ttk, messagebox
import os
import random
import string
import pyperclip


class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("账号密码管理器")
        self.root.geometry("900x600")  # 稍微加宽窗口以适应新字段
        self.root.minsize(800, 500)  # 设置最小尺寸，防止窗口过小
        self.root.resizable(True, True)

        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=("SimHei", 10, "bold"))
        self.style.configure("Treeview", font=("SimHei", 10))
        self.style.configure("TNotebook", font=("SimHei", 10))
        self.style.configure("TNotebook.Tab", font=("SimHei", 10))

        # 数据文件路径
        self.password_file = "passwords.txt"
        self.url_file = "urls.txt"

        # 加载已有数据
        self.password_entries = self.load_password_data()
        self.url_entries = self.load_url_data()

        # 创建UI
        self.create_widgets()

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建选项卡控件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建账号密码选项卡
        self.account_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.account_tab, text="账号")

        # 创建网址选项卡
        self.url_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.url_tab, text="网址")

        # 初始化账号密码选项卡内容
        self.init_account_tab()

        # 初始化网址选项卡内容
        self.init_url_tab()

    def init_account_tab(self):
        """初始化账号密码选项卡内容（添加用户名字段）"""
        # 创建搜索框
        search_frame = ttk.Frame(self.account_tab)
        search_frame.pack(fill=tk.X, pady=(0, 10), padx=5)

        ttk.Label(search_frame, text="搜索: ", font=("SimHei", 10)).pack(side=tk.LEFT)
        self.account_search_entry = ttk.Entry(search_frame)
        self.account_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(search_frame, text="搜索", command=self.search_account).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="显示全部", command=self.refresh_account_list).pack(side=tk.LEFT)

        # 创建表格（增加用户名字段）
        columns = ("网站/描述", "用户名", "账号", "密码")
        self.account_tree = ttk.Treeview(self.account_tab, columns=columns, show="headings")

        # 设置列标题和宽度
        for col in columns:
            self.account_tree.heading(col, text=col)
            self.account_tree.column(col, width=150, anchor=tk.CENTER)

        # 调整列宽
        self.account_tree.column("网站/描述", width=200)
        self.account_tree.column("用户名", width=150)
        self.account_tree.column("账号", width=150)
        self.account_tree.column("密码", width=150)

        # 创建包含表格和滚动条的框架
        tree_frame = ttk.Frame(self.account_tab)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加滚动条
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.account_tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.account_tree.xview)
        self.account_tree.configure(yscroll=y_scrollbar.set, xscroll=x_scrollbar.set)

        # 放置表格和滚动条
        self.account_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建按钮框架，使用网格布局更灵活
        button_frame = ttk.Frame(self.account_tab, padding="10")
        button_frame.pack(fill=tk.Y, side=tk.RIGHT, padx=5)

        # 按钮使用网格布局，避免超出窗口
        buttons = [
            ("添加", self.add_account),
            ("编辑", self.edit_account),
            ("删除", self.delete_account),
            ("复制密码", self.copy_password),
            ("生成密码", self.generate_password)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.grid(row=i, column=0, padx=2, pady=5, sticky=tk.EW)

        # 让按钮框架的列自适应按钮大小
        button_frame.columnconfigure(0, weight=1)

        # 填充表格数据
        self.refresh_account_list()

    def init_url_tab(self):
        """初始化网址选项卡内容"""
        # 创建搜索框
        search_frame = ttk.Frame(self.url_tab)
        search_frame.pack(fill=tk.X, pady=(0, 10), padx=5)

        ttk.Label(search_frame, text="搜索: ", font=("SimHei", 10)).pack(side=tk.LEFT)
        self.url_search_entry = ttk.Entry(search_frame)
        self.url_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(search_frame, text="搜索", command=self.search_url).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="显示全部", command=self.refresh_url_list).pack(side=tk.LEFT)

        # 创建表格
        columns = ("网站名称", "网址链接")
        self.url_tree = ttk.Treeview(self.url_tab, columns=columns, show="headings")

        # 设置列标题
        for col in columns:
            self.url_tree.heading(col, text=col)
            self.url_tree.column(col, width=250, anchor=tk.CENTER)

        # 调整列宽
        self.url_tree.column("网址链接", width=400)

        # 创建包含表格和滚动条的框架
        tree_frame = ttk.Frame(self.url_tab)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加滚动条
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.url_tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.url_tree.xview)
        self.url_tree.configure(yscroll=y_scrollbar.set, xscroll=x_scrollbar.set)

        # 放置表格和滚动条
        self.url_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建按钮框架
        button_frame = ttk.Frame(self.url_tab, padding="10")
        button_frame.pack(fill=tk.Y, side=tk.RIGHT, padx=5)

        # 按钮使用网格布局
        buttons = [
            ("添加网址", self.add_url),
            ("编辑网址", self.edit_url),
            ("删除网址", self.delete_url),
            ("复制链接", self.copy_url)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.grid(row=i, column=0, padx=2, pady=5, sticky=tk.EW)

        # 让按钮框架的列自适应按钮大小
        button_frame.columnconfigure(0, weight=1)

        # 填充表格数据
        self.refresh_url_list()

    # 账号密码相关方法
    def load_password_data(self):
        """从TXT文件加载账号密码数据（适配新的用户名字段）"""
        entries = []
        if os.path.exists(self.password_file):
            try:
                with open(self.password_file, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]

                # 每四行组成一个条目（网站描述、用户名、账号、密码）
                for i in range(0, len(lines), 4):
                    description = lines[i] if i < len(lines) else ""
                    username = lines[i + 1] if i + 1 < len(lines) else ""
                    account = lines[i + 2] if i + 2 < len(lines) else ""
                    password = lines[i + 3] if i + 3 < len(lines) else ""
                    entries.append({
                        "description": description,
                        "username": username,
                        "account": account,
                        "password": password
                    })
            except Exception as e:
                messagebox.showerror("错误", f"加载账号数据失败: {str(e)}")
        return entries

    def save_password_data(self):
        """保存账号密码数据到TXT文件（适配新的用户名字段）"""
        try:
            with open(self.password_file, "w", encoding="utf-8") as f:
                for entry in self.password_entries:
                    f.write(f"{entry['description']}\n")
                    f.write(f"{entry['username']}\n")
                    f.write(f"{entry['account']}\n")
                    f.write(f"{entry['password']}\n")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存账号数据失败: {str(e)}")
            return False

    def refresh_account_list(self):
        """刷新账号表格数据"""
        # 清空现有数据
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)

        # 添加所有数据
        for entry in self.password_entries:
            self.account_tree.insert("", tk.END, values=(
                entry["description"],
                entry["username"],
                entry["account"],
                entry["password"]
            ))

    def search_account(self):
        """搜索账号"""
        search_term = self.account_search_entry.get().lower()
        if not search_term:
            self.refresh_account_list()
            return

        # 清空现有数据
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)

        # 添加匹配的数据
        for entry in self.password_entries:
            if (search_term in entry["description"].lower() or
                    search_term in entry["username"].lower() or
                    search_term in entry["account"].lower()):
                self.account_tree.insert("", tk.END, values=(
                    entry["description"],
                    entry["username"],
                    entry["account"],
                    entry["password"]
                ))

    def add_account(self):
        """添加新账号（包含用户名字段）"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加新账号")
        dialog.geometry("500x350")  # 适当加大对话框
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 创建输入框
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="网站/描述:").grid(row=0, column=0, sticky=tk.W, pady=5)
        desc_entry = ttk.Entry(frame, width=40)
        desc_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="用户名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        user_entry = ttk.Entry(frame, width=40)
        user_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="账号:").grid(row=2, column=0, sticky=tk.W, pady=5)
        account_entry = ttk.Entry(frame, width=40)
        account_entry.grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="密码:").grid(row=3, column=0, sticky=tk.W, pady=5)
        pass_entry = ttk.Entry(frame, width=40, show="*")
        pass_entry.grid(row=3, column=1, pady=5)

        # 生成密码按钮
        def gen_pass():
            pass_entry.delete(0, tk.END)
            pass_entry.insert(0, self.generate_password(True))

        ttk.Button(frame, text="生成密码", command=gen_pass).grid(row=3, column=2, padx=5)

        # 确认按钮
        def confirm():
            description = desc_entry.get().strip()
            username = user_entry.get().strip()
            account = account_entry.get().strip()
            password = pass_entry.get().strip()

            if not description or not username or not account or not password:
                messagebox.showerror("错误", "所有字段都不能为空!")
                return

            self.password_entries.append({
                "description": description,
                "username": username,
                "account": account,
                "password": password
            })

            if self.save_password_data():
                self.refresh_account_list()
                dialog.destroy()

        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10, padx=20)

        ttk.Button(btn_frame, text="确认", command=confirm).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)

    def edit_account(self):
        """编辑选中的账号（包含用户名字段）"""
        selected = self.account_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个账号")
            return

        # 获取选中条目的索引
        index = self.account_tree.index(selected[0])
        entry = self.password_entries[index]

        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑账号")
        dialog.geometry("500x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 创建输入框并填充现有数据
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="网站/描述:").grid(row=0, column=0, sticky=tk.W, pady=5)
        desc_entry = ttk.Entry(frame, width=40)
        desc_entry.grid(row=0, column=1, pady=5)
        desc_entry.insert(0, entry["description"])

        ttk.Label(frame, text="用户名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        user_entry = ttk.Entry(frame, width=40)
        user_entry.grid(row=1, column=1, pady=5)
        user_entry.insert(0, entry["username"])

        ttk.Label(frame, text="账号:").grid(row=2, column=0, sticky=tk.W, pady=5)
        account_entry = ttk.Entry(frame, width=40)
        account_entry.grid(row=2, column=1, pady=5)
        account_entry.insert(0, entry["account"])

        ttk.Label(frame, text="密码:").grid(row=3, column=0, sticky=tk.W, pady=5)
        pass_entry = ttk.Entry(frame, width=40, show="*")
        pass_entry.grid(row=3, column=1, pady=5)
        pass_entry.insert(0, entry["password"])

        # 生成密码按钮
        def gen_pass():
            pass_entry.delete(0, tk.END)
            pass_entry.insert(0, self.generate_password(True))

        ttk.Button(frame, text="生成密码", command=gen_pass).grid(row=3, column=2, padx=5)

        # 确认按钮
        def confirm():
            description = desc_entry.get().strip()
            username = user_entry.get().strip()
            account = account_entry.get().strip()
            password = pass_entry.get().strip()

            if not description or not username or not account or not password:
                messagebox.showerror("错误", "所有字段都不能为空!")
                return

            self.password_entries[index] = {
                "description": description,
                "username": username,
                "account": account,
                "password": password
            }

            if self.save_password_data():
                self.refresh_account_list()
                dialog.destroy()

        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10, padx=20)

        ttk.Button(btn_frame, text="确认", command=confirm).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)

    def delete_account(self):
        """删除选中的账号"""
        selected = self.account_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个账号")
            return

        if messagebox.askyesno("确认", "确定要删除这个账号吗?"):
            # 获取选中条目的索引
            index = self.account_tree.index(selected[0])
            # 删除条目
            del self.password_entries[index]
            # 保存并刷新
            if self.save_password_data():
                self.refresh_account_list()

    def copy_password(self):
        """复制选中条目的密码到剪贴板"""
        selected = self.account_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个账号")
            return

        # 获取选中条目的索引
        index = self.account_tree.index(selected[0])
        password = self.password_entries[index]["password"]

        # 复制到剪贴板
        pyperclip.copy(password)
        messagebox.showinfo("提示", "密码已复制到剪贴板")

    # 网址相关方法
    def load_url_data(self):
        """从TXT文件加载网址数据"""
        entries = []
        if os.path.exists(self.url_file):
            try:
                with open(self.url_file, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]

                # 每两行组成一个条目（网站名称、网址链接）
                for i in range(0, len(lines), 2):
                    name = lines[i] if i < len(lines) else ""
                    url = lines[i + 1] if i + 1 < len(lines) else ""
                    entries.append({
                        "name": name,
                        "url": url
                    })
            except Exception as e:
                messagebox.showerror("错误", f"加载网址数据失败: {str(e)}")
        return entries

    def save_url_data(self):
        """保存网址数据到TXT文件"""
        try:
            with open(self.url_file, "w", encoding="utf-8") as f:
                for entry in self.url_entries:
                    f.write(f"{entry['name']}\n")
                    f.write(f"{entry['url']}\n")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存网址数据失败: {str(e)}")
            return False

    def refresh_url_list(self):
        """刷新网址表格数据"""
        # 清空现有数据
        for item in self.url_tree.get_children():
            self.url_tree.delete(item)

        # 添加所有数据
        for entry in self.url_entries:
            self.url_tree.insert("", tk.END, values=(
                entry["name"],
                entry["url"]
            ))

    def search_url(self):
        """搜索网址"""
        search_term = self.url_search_entry.get().lower()
        if not search_term:
            self.refresh_url_list()
            return

        # 清空现有数据
        for item in self.url_tree.get_children():
            self.url_tree.delete(item)

        # 添加匹配的数据
        for entry in self.url_entries:
            if (search_term in entry["name"].lower() or
                    search_term in entry["url"].lower()):
                self.url_tree.insert("", tk.END, values=(
                    entry["name"],
                    entry["url"]
                ))

    def add_url(self):
        """添加新网址"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加新网址")
        dialog.geometry("500x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 创建输入框
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="网站名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(frame, width=40)
        name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="网址链接:").grid(row=1, column=0, sticky=tk.W, pady=5)
        url_entry = ttk.Entry(frame, width=40)
        url_entry.grid(row=1, column=1, pady=5)
        url_entry.insert(0, "https://")  # 默认添加网址前缀

        # 确认按钮
        def confirm():
            name = name_entry.get().strip()
            url = url_entry.get().strip()

            if not name or not url:
                messagebox.showerror("错误", "所有字段都不能为空!")
                return

            self.url_entries.append({
                "name": name,
                "url": url
            })

            if self.save_url_data():
                self.refresh_url_list()
                dialog.destroy()

        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10, padx=20)

        ttk.Button(btn_frame, text="确认", command=confirm).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)

    def edit_url(self):
        """编辑选中的网址"""
        selected = self.url_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个网址")
            return

        # 获取选中条目的索引
        index = self.url_tree.index(selected[0])
        entry = self.url_entries[index]

        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑网址")
        dialog.geometry("500x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 创建输入框并填充现有数据
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="网站名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(frame, width=40)
        name_entry.grid(row=0, column=1, pady=5)
        name_entry.insert(0, entry["name"])

        ttk.Label(frame, text="网址链接:").grid(row=1, column=0, sticky=tk.W, pady=5)
        url_entry = ttk.Entry(frame, width=40)
        url_entry.grid(row=1, column=1, pady=5)
        url_entry.insert(0, entry["url"])

        # 确认按钮
        def confirm():
            name = name_entry.get().strip()
            url = url_entry.get().strip()

            if not name or not url:
                messagebox.showerror("错误", "所有字段都不能为空!")
                return

            self.url_entries[index] = {
                "name": name,
                "url": url
            }

            if self.save_url_data():
                self.refresh_url_list()
                dialog.destroy()

        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10, padx=20)

        ttk.Button(btn_frame, text="确认", command=confirm).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)

    def delete_url(self):
        """删除选中的网址"""
        selected = self.url_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个网址")
            return

        if messagebox.askyesno("确认", "确定要删除这个网址吗?"):
            # 获取选中条目的索引
            index = self.url_tree.index(selected[0])
            # 删除条目
            del self.url_entries[index]
            # 保存并刷新
            if self.save_url_data():
                self.refresh_url_list()

    def copy_url(self):
        """复制选中的网址到剪贴板"""
        selected = self.url_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个网址")
            return

        # 获取选中条目的索引
        index = self.url_tree.index(selected[0])
        url = self.url_entries[index]["url"]

        # 复制到剪贴板
        pyperclip.copy(url)
        messagebox.showinfo("提示", "网址已复制到剪贴板")

    def generate_password(self, return_only=False):
        """生成随机密码"""
        # 密码字符集
        letters = string.ascii_letters
        digits = string.digits
        symbols = string.punctuation

        # 组合字符集
        all_chars = letters + digits + symbols

        # 生成12位随机密码
        password = ''.join(random.choice(all_chars) for _ in range(12))

        if return_only:
            return password

        # 显示生成的密码
        dialog = tk.Toplevel(self.root)
        dialog.title("生成密码")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="生成的密码:").pack(anchor=tk.W, pady=(0, 5))
        pass_entry = ttk.Entry(frame, width=30, font=("SimHei", 12))
        pass_entry.pack(fill=tk.X, pady=(0, 10))
        pass_entry.insert(0, password)

        # 复制按钮
        def copy_to_clipboard():
            pyperclip.copy(password)
            messagebox.showinfo("提示", "密码已复制到剪贴板")
            dialog.destroy()

        ttk.Button(frame, text="复制到剪贴板", command=copy_to_clipboard).pack(fill=tk.X)

        return password


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManager(root)
    root.mainloop()
