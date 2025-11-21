import random
import tkinter as tk
from tkinter import font
from tkinter import ttk
import sys
# 自定义开关控件
class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, variable: tk.BooleanVar, command=None,
                 width=72, height=32, on_color=None, off_color="#444",
                 knob_color="#ffffff", **kwargs):
        # ttk.Frame不支持 cget('bg'); 使用全局背景色
        super().__init__(parent, width=width, height=height, background=BG_COLOR, highlightthickness=0, bd=0, **kwargs)
        self.variable = variable
        self.command = command
        if on_color is None:
            # 延迟使用全局常量避免定义顺序问题
            try:
                self.on_color = SUCCESS_COLOR
            except NameError:
                self.on_color = "#3fcf8e"
        else:
            self.on_color = on_color
        self.off_color = off_color
        self.knob_color = knob_color
        self.radius = height / 2 - 2
        self.padding = 2
        self.width = width
        self.height = height
        self.bind("<Button-1>", self.toggle)
        self.bind("<Enter>", lambda e: self.configure(cursor="hand2"))
        self.draw()

    def toggle(self, _=None):
        self.variable.set(not self.variable.get())
        self.draw()
        if self.command:
            self.command()

    def draw(self):
        self.delete("all")
        state_on = self.variable.get()
        track_color = self.on_color if state_on else self.off_color
        # 画背景轨道（圆角矩形）
        self.create_round_rect(self.padding, self.padding,
                               self.width - self.padding, self.height - self.padding,
                               r=self.radius, fill=track_color, outline="")
        # 画圆形滑块
        knob_x = (self.width - self.padding - self.radius) if state_on else (self.padding + self.radius)
        self.create_oval(knob_x - self.radius, self.height / 2 - self.radius,
                         knob_x + self.radius, self.height / 2 + self.radius,
                         fill=self.knob_color, outline="")
        # 文本（ON/OFF）
        text = "ON" if state_on else "OFF"
        self.create_text(self.width / 2, self.height / 2, text=text, fill="#000" if state_on else "#ddd",
                         font=("Helvetica", 10, "bold"))

    def create_round_rect(self, x1, y1, x2, y2, r=8, **kwargs):
        # 通过四个圆角 + 四条边实现圆角矩形
        self.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, style=tk.PIESLICE, **kwargs)
        self.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, style=tk.PIESLICE, **kwargs)
        self.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, style=tk.PIESLICE, **kwargs)
        self.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, style=tk.PIESLICE, **kwargs)
        self.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs)
        self.create_rectangle(x1, y1 + r, x2, y2 - r, **kwargs)


# 统一配色与样式常量
BG_COLOR = "#1e1e24"
PANEL_BG = "#25252b"
ACCENT_COLOR = "#61dafb"
NUMBER_COLOR = "#ffcc00"
WINNER_COLOR = "#8affc1"
DANGER_COLOR = "#ff5f56"
SUCCESS_COLOR = "#3fcf8e"
NEUTRAL_COLOR = "#888"  # 次要文字

class LotteryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("幸运抽奖 · 豪华版")
        self.root.configure(bg=BG_COLOR)

        # 字体设置（ttk不直接支持Font对象应用到style中时，可单独用于非ttk组件）
        self.title_font = font.Font(family="Helvetica", size=28, weight="bold")
        self.number_font = font.Font(family="Helvetica", size=90, weight="bold")
        self.winner_font = font.Font(family="Helvetica", size=48, weight="bold")
        self.history_font = font.Font(family="Consolas", size=12)
        self.button_font = font.Font(family="Helvetica", size=16, weight="bold")

        # 动态参数
        self.min_number = 1
        self.max_number = 500
        self.running = False
        self.animation_id = None
        self.winner = None
        self.lottery_count = 0
        self.winner_history = []
        self.unique_mode_var = tk.BooleanVar(value=False)
        self.available_numbers = None  # 去重模式下的剩余号码池
        self.current_prize = tk.StringVar(value="一等奖")
        self.decelerating = False
        self.deceleration_phase = 0
        self.deceleration_delays = [120, 180, 260, 360, 500, 700, 950]
        self.fullscreen = False
        # 老虎机动画相关
        self.digit_labels = []
        self.digit_frame = None
        self.slot_mode = True  # Phase2: 使用按位滚动展示
        self.digits_count = len(str(self.max_number))
        self.slot_deceleration_index = 0
        self.slot_final_digits = []
        self.slot_stop_schedule = []
        # 主题相关
        self.theme_var = tk.StringVar(value="暗色")
        self.themes = {
            "暗色": {
                "bg": BG_COLOR, "panel": PANEL_BG, "accent": ACCENT_COLOR,
                "number": NUMBER_COLOR, "winner": WINNER_COLOR, "success": SUCCESS_COLOR,
                "danger": DANGER_COLOR, "neutral": NEUTRAL_COLOR
            },
            "金色": {
                "bg": "#161510", "panel": "#201f1a", "accent": "#d4af37",
                "number": "#ffd700", "winner": "#ffec8b", "success": "#bfa100",
                "danger": "#ff5f56", "neutral": "#998c6a"
            },
            "荧光": {
                "bg": "#0b0f17", "panel": "#111826", "accent": "#39ffdc",
                "number": "#7fff00", "winner": "#ff6fff", "success": "#00ffa2",
                "danger": "#ff4d67", "neutral": "#5d6a73"
            },
            "简洁": {
                "bg": "#f5f5f5", "panel": "#ffffff", "accent": "#007acc",
                "number": "#333333", "winner": "#d6336c", "success": "#2b9348",
                "danger": "#d1495b", "neutral": "#6c757d"
            }
        }
        # 聚光灯已移除，仅保留彩带动画

        # ttk主题与样式
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Main.TFrame', background=BG_COLOR)
        style.configure('Panel.TFrame', background=PANEL_BG, borderwidth=0)
        style.configure('Title.TLabel', background=BG_COLOR, foreground=ACCENT_COLOR, font=("Helvetica", 28, "bold"))
        style.configure('Number.TLabel', background=BG_COLOR, foreground=NUMBER_COLOR, font=("Helvetica", 90, "bold"))
        style.configure('Winner.TLabel', background=BG_COLOR, foreground=WINNER_COLOR, font=("Helvetica", 48, "bold"))
        style.configure('Info.TLabel', background=PANEL_BG, foreground=NEUTRAL_COLOR, font=("Helvetica", 11))
        style.configure('Accent.TButton', font=("Helvetica", 16, "bold"), foreground=BG_COLOR, padding=10)
        style.map('Accent.TButton', background=[('!disabled', ACCENT_COLOR), ('disabled', '#3a4a52')])
        style.configure('Danger.TButton', font=("Helvetica", 16, "bold"), foreground=BG_COLOR, padding=10)
        style.map('Danger.TButton', background=[('!disabled', DANGER_COLOR), ('disabled', '#5a3a3a')])
        style.configure('Neutral.TButton', font=("Helvetica", 16, "bold"), foreground=BG_COLOR, padding=10)
        style.map('Neutral.TButton', background=[('!disabled', '#444'), ('active', '#555')])
        style.configure('Success.TButton', font=("Helvetica", 16, "bold"), foreground=BG_COLOR, padding=10)
        style.map('Success.TButton', background=[('!disabled', SUCCESS_COLOR), ('disabled', '#2d6d55')])

        # 主布局框架
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部标题区域
        self.header_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        self.header_frame.pack(fill=tk.X, pady=(20, 10))
        self.title_label = ttk.Label(self.header_frame, text="幸运抽奖", style='Title.TLabel')
        self.title_label.pack()
        self.subtitle_label = ttk.Label(self.header_frame, text="祝你好运 · Fortune Awaits", style='Info.TLabel')
        self.subtitle_label.pack(pady=(4, 0))

        # 中间分区：左侧控制 + 中央显示 + 右侧历史
        self.center_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        self.center_frame.pack(fill=tk.BOTH, expand=True, padx=30)

        # 左侧控制面板
        self.control_panel = ttk.Frame(self.center_frame, style='Panel.TFrame')
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20), pady=10)

        # 最大值设置
        ttk.Label(self.control_panel, text="最大随机数", style='Info.TLabel').pack(anchor='w', padx=12, pady=(12, 4))
        self.max_var = tk.IntVar(value=self.max_number)
        self.max_spin = ttk.Spinbox(self.control_panel, from_=10, to=9999, textvariable=self.max_var, width=10)
        self.max_spin.pack(padx=12, pady=(0, 16), anchor='w')

        # 奖项选择
        ttk.Label(self.control_panel, text="当前奖项", style='Info.TLabel').pack(anchor='w', padx=12, pady=(0, 4))
        self.prize_box = ttk.Combobox(self.control_panel, values=["特等奖","一等奖","二等奖","三等奖","幸运奖"], textvariable=self.current_prize, state="readonly")
        self.prize_box.pack(padx=12, pady=(0, 16), anchor='w')

        # 不重复模式开关（更显眼）
        unique_frame = ttk.Frame(self.control_panel, style='Panel.TFrame')
        unique_frame.pack(padx=12, pady=(0, 18), anchor='w')
        ttk.Label(unique_frame, text="不重复号码", style='Info.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.unique_switch = ToggleSwitch(unique_frame, self.unique_mode_var, command=self.toggle_unique_mode,
                          on_color=SUCCESS_COLOR, off_color="#555", knob_color="#fff")
        self.unique_switch.pack(side=tk.LEFT)

        # 主题选择
        ttk.Label(self.control_panel, text="主题", style='Info.TLabel').pack(anchor='w', padx=12, pady=(0, 4))
        self.theme_box = ttk.Combobox(self.control_panel, values=list(self.themes.keys()), textvariable=self.theme_var, state='readonly')
        self.theme_box.pack(padx=12, pady=(0, 16), anchor='w')
        self.theme_box.bind('<<ComboboxSelected>>', lambda e: self.apply_theme(self.theme_var.get()))

        # 按钮组
        self.start_button = ttk.Button(self.control_panel, text="开始", command=self.start_animation, style='Success.TButton')
        self.start_button.pack(fill=tk.X, padx=12, pady=(0, 10))
        self.stop_button = ttk.Button(self.control_panel, text="停止", command=self.stop_animation, style='Danger.TButton')
        self.stop_button.pack(fill=tk.X, padx=12, pady=(0, 10))
        self.reset_button = ttk.Button(self.control_panel, text="重置", command=self.reset_history, style='Neutral.TButton')
        self.reset_button.pack(fill=tk.X, padx=12, pady=(0, 10))
        self.export_button = ttk.Button(self.control_panel, text="导出历史", command=self.export_history, style='Accent.TButton')
        self.export_button.pack(fill=tk.X, padx=12, pady=(0, 10))
        self.fullscreen_button = ttk.Button(self.control_panel, text="全屏", command=self.toggle_fullscreen, style='Neutral.TButton')
        self.fullscreen_button.pack(fill=tk.X, padx=12, pady=(0, 10))
        self.exit_button = ttk.Button(self.control_panel, text="退出", command=self.exit_app, style='Neutral.TButton')
        self.exit_button.pack(fill=tk.X, padx=12, pady=(0, 10))

        # 控制信息标签
        self.info_label = ttk.Label(self.control_panel, text="未开始", style='Info.TLabel')
        self.info_label.pack(anchor='w', padx=12, pady=(20, 4))

        # 中央数字显示区
        self.display_frame = ttk.Frame(self.center_frame, style='Panel.TFrame')
        self.display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        # 数字显示：将单标签扩展为老虎机按位模式
        self.number_label = ttk.Label(self.display_frame, text="0", style='Number.TLabel', anchor='center')  # 备用隐藏标签
        self.build_digit_frame()
        self.number_label.pack_forget()
        self.winner_label = ttk.Label(self.display_frame, text="", style='Winner.TLabel', anchor='center')
        self.winner_label.pack(pady=(10, 10))

        # 彩带动画画布
        self.confetti_canvas = tk.Canvas(self.display_frame, bg=BG_COLOR, highlightthickness=0, bd=0)
        self.confetti_canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.confetti_items = []

        # 右侧历史记录面板（Treeview表格替换）
        self.history_panel = ttk.Frame(self.center_frame, style='Panel.TFrame')
        self.history_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0), pady=10)
        ttk.Label(self.history_panel, text="抽奖历史", style='Info.TLabel').pack(anchor='center', pady=(12, 6))
        self.tree = ttk.Treeview(self.history_panel, columns=("idx","prize","number"), show='headings', height=22)
        self.tree.heading("idx", text="序号")
        self.tree.heading("prize", text="奖项")
        self.tree.heading("number", text="号码")
        self.tree.column("idx", width=60, anchor='center')
        self.tree.column("prize", width=90, anchor='center')
        self.tree.column("number", width=90, anchor='center')
        self.tree.pack(fill=tk.Y, expand=False, padx=10)
        self.tree_scroll = ttk.Scrollbar(self.history_panel, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 初始按钮状态
        self.set_running_state(False)

        # 自适应窗口大小
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.72)
        window_height = int(screen_height * 0.75)
        self.root.geometry(f"{window_width}x{window_height}+60+40")

    # 状态切换统一处理
    def set_running_state(self, running: bool):
        self.running = running
        if running:
            self.start_button.state(['disabled'])
            self.stop_button.state(['!disabled'])
            self.info_label.config(text="运行中…")
        else:
            self.start_button.state(['!disabled'])
            self.stop_button.state(['disabled'])
            self.info_label.config(text="已停止")
        # 在减速阶段禁用Stop避免重复触发
        if self.decelerating:
            self.stop_button.state(['disabled'])

    def toggle_unique_mode(self):
        if self.unique_mode_var.get():
            # 初始化号码池
            self.available_numbers = list(range(self.min_number, self.max_number + 1))
            random.shuffle(self.available_numbers)
            self.info_label.config(text="去重模式已开启")
        else:
            self.available_numbers = None
            self.info_label.config(text="去重模式关闭")

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        self.fullscreen_button.config(text="退出全屏" if self.fullscreen else "全屏")

    def draw_number(self):
        if self.running:
            number = self.generate_random_number()
            if number is None:
                # 无剩余号码
                self.stop_animation(force=True)
                return
            self.number_label.config(text=str(number))
            self.animation_id = self.root.after(60, self.draw_number)
            if self.slot_mode:
                self.update_slot_digits(number)

    def generate_random_number(self):
        if self.unique_mode_var.get():
            if not self.available_numbers:
                self.info_label.config(text="号码已全部抽完")
                return None
            # 不移除，这只是滚动显示
            return random.choice(self.available_numbers)
        else:
            return random.randint(self.min_number, self.max_number)

    def start_animation(self):
        # 更新最大随机数
        try:
            self.max_number = int(self.max_var.get())
        except Exception:
            self.max_number = 500
            self.max_var.set(500)
        if self.unique_mode_var.get():
            # 重新生成号码池，剔除已中奖号码
            used = set(self.winner_history)
            self.available_numbers = [n for n in range(self.min_number, self.max_number + 1) if n not in used]
            random.shuffle(self.available_numbers)
            if not self.available_numbers:
                self.info_label.config(text="已无可抽取号码")
                return
        self.lottery_count += 1
        self.winner_label.config(text="")
        self.number_label.config(text="0")
        self.set_running_state(True)
        self.digits_count = len(str(self.max_number))
        if self.slot_mode:
            self.rebuild_slot_if_needed()
        # 音效已移除
        self.draw_number()

    def stop_animation(self, force=False):
        if not self.running and not force:
            return
        if force:
            # 强制立即停止（例如号码耗尽）
            self.set_running_state(False)
            if self.animation_id is not None:
                self.root.after_cancel(self.animation_id)
                self.animation_id = None
            current_number = self.number_label.cget("text")
            if current_number:
                self.finalize_winner(int(current_number))
            return
        # 减速模式启动
        self.decelerating = True
        self.deceleration_phase = 0
        self.info_label.config(text="正在减速…")
        if self.animation_id is not None:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        if self.slot_mode:
            self.prepare_slot_deceleration()
        else:
            self.deceleration_step()

    def deceleration_step(self):
        if self.deceleration_phase < len(self.deceleration_delays):
            number = self.generate_final_candidate()
            if number is None:
                self.decelerating = False
                self.set_running_state(False)
                return
            self.number_label.config(text=str(number))
            delay = self.deceleration_delays[self.deceleration_phase]
            self.deceleration_phase += 1
            self.root.after(delay, self.deceleration_step)
        else:
            # 完成减速
            final_number = int(self.number_label.cget("text"))
            self.decelerating = False
            self.set_running_state(False)
            self.finalize_winner(final_number)

    def generate_final_candidate(self):
        if self.unique_mode_var.get():
            if not self.available_numbers:
                return None
            # 抽取最终候选：每次减速阶段都随机挑一个
            return random.choice(self.available_numbers)
        else:
            return random.randint(self.min_number, self.max_number)

    def finalize_winner(self, number):
        self.winner = number
        if self.unique_mode_var.get() and number in self.available_numbers:
            # 移除最终中奖号
            try:
                self.available_numbers.remove(number)
            except ValueError:
                pass
        prize = self.current_prize.get()
        self.winner_label.config(text=f"🎉 {prize} 号码: {self.winner}")
        self.append_history(self.winner, prize)
        self.info_label.config(text="中奖产生！")
        self.launch_confetti()
        # 聚光灯与音效已停用，仅保留彩带

    def append_history(self, winner, prize):
        self.winner_history.append(winner)
        idx = len(self.winner_history)
        self.tree.insert('', tk.END, values=(idx, prize, winner))
        self.tree.yview_moveto(1)

    def reset_history(self):
        self.winner_history = []
        self.lottery_count = 0
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.number_label.config(text="0")
        self.winner_label.config(text="")
        self.info_label.config(text="已重置")
        self.set_running_state(False)
        if self.unique_mode_var.get():
            self.toggle_unique_mode()  # 重建号码池
        # 聚光灯已移除无需清理

    def export_history(self):
        if not self.winner_history:
            self.info_label.config(text="无历史可导出")
            return
        try:
            with open("winner_history.txt", "w", encoding="utf-8") as f:
                for idx, item in enumerate(self.tree.get_children(), start=1):
                    vals = self.tree.item(item, 'values')
                    f.write(f"{vals[0]},{vals[1]},{vals[2]}\n")
            self.info_label.config(text="已导出 winner_history.txt")
        except Exception:
            self.info_label.config(text="导出失败")

    # 彩带动画
    def launch_confetti(self):
        self.clear_confetti()
        width = self.confetti_canvas.winfo_width()
        height = self.confetti_canvas.winfo_height()
        colors = [ACCENT_COLOR, NUMBER_COLOR, WINNER_COLOR, SUCCESS_COLOR, DANGER_COLOR, '#ff8c00', '#c34fff']
        for _ in range(70):
            x = random.randint(0, max(10, width - 10))
            size = random.randint(6, 14)
            y = random.randint(-height, 0)
            color = random.choice(colors)
            shape_type = random.choice(['oval','rect'])
            if shape_type == 'oval':
                item = self.confetti_canvas.create_oval(x, y, x+size, y+size, fill=color, outline="")
            else:
                item = self.confetti_canvas.create_rectangle(x, y, x+size, y+size, fill=color, outline="")
            self.confetti_items.append((item, random.uniform(1.5, 4.5)))
        self.animate_confetti()

    def animate_confetti(self):
        to_remove = []
        height = self.confetti_canvas.winfo_height()
        for idx, (item, speed) in enumerate(self.confetti_items):
            self.confetti_canvas.move(item, 0, speed)
            coords = self.confetti_canvas.coords(item)
            if coords and coords[1] > height + 30:
                to_remove.append((idx, item))
        # 清理落出
        for idx, item in reversed(to_remove):
            try:
                self.confetti_canvas.delete(item)
            except Exception:
                pass
            del self.confetti_items[idx]
        if self.confetti_items:
            self.root.after(30, self.animate_confetti)
        else:
            self.clear_confetti()

    def clear_confetti(self):
        for item, _ in self.confetti_items:
            try:
                self.confetti_canvas.delete(item)
            except Exception:
                pass
        self.confetti_items = []
    # ---------- 老虎机按位动画相关 ----------
    def build_digit_frame(self):
        if self.digit_frame:
            self.digit_frame.destroy()
        self.digit_frame = ttk.Frame(self.display_frame, style='Panel.TFrame')
        self.digit_frame.pack(pady=(30, 10))
        self.digit_labels = []
        for i in range(self.digits_count):
            lbl = ttk.Label(self.digit_frame, text='0', style='Number.TLabel', anchor='center')
            lbl.pack(side=tk.LEFT, padx=4)
            self.digit_labels.append(lbl)

    def rebuild_slot_if_needed(self):
        if len(self.digit_labels) != self.digits_count:
            self.build_digit_frame()

    def update_slot_digits(self, number):
        num_str = str(number).rjust(self.digits_count, '0')
        for i, d in enumerate(num_str):
            self.digit_labels[i].config(text=d)

    def prepare_slot_deceleration(self):
        # 为每一位安排停止顺序，模拟从左到右或右到左停下
        final_number = int(self.number_label.cget('text'))
        self.slot_final_digits = list(str(final_number).rjust(self.digits_count, '0'))
        self.slot_stop_schedule = []
        base_delay = 250
        for idx in range(self.digits_count):
            self.slot_stop_schedule.append(base_delay * (idx + 1))
        self.slot_deceleration_index = 0
        self.root.after(80, self.slot_spin_step)

    def slot_spin_step(self):
        if self.slot_deceleration_index < self.digits_count:
            # 未锁定的位继续随机
            for i in range(self.slot_deceleration_index, self.digits_count):
                self.digit_labels[i].config(text=str(random.randint(0, 9)))
            # 检查是否该锁定当前位
            current_delay = self.slot_stop_schedule[self.slot_deceleration_index]
            self.slot_stop_schedule[self.slot_deceleration_index] = 0  # 标记处理
            self.root.after(current_delay, self.lock_current_digit)
        else:
            # 全部锁定后生成最终winner
            final_value = int(''.join(self.slot_final_digits))
            self.decelerating = False
            self.set_running_state(False)
            self.finalize_winner(final_value)

    def lock_current_digit(self):
        if self.slot_deceleration_index < self.digits_count:
            self.digit_labels[self.slot_deceleration_index].config(text=self.slot_final_digits[self.slot_deceleration_index])
            self.slot_deceleration_index += 1
            self.root.after(80, self.slot_spin_step)

    # ---------- 主题切换 ----------
    def apply_theme(self, name):
        theme = self.themes.get(name)
        if not theme:
            return
        style = ttk.Style()
        style.configure('Main.TFrame', background=theme['bg'])
        style.configure('Panel.TFrame', background=theme['panel'])
        style.configure('Title.TLabel', background=theme['bg'], foreground=theme['accent'])
        style.configure('Number.TLabel', background=theme['bg'], foreground=theme['number'])
        style.configure('Winner.TLabel', background=theme['bg'], foreground=theme['winner'])
        style.configure('Info.TLabel', background=theme['panel'], foreground=theme['neutral'])
        self.root.configure(bg=theme['bg'])
        # 更新彩带画布底色
        self.confetti_canvas.config(bg=theme['bg'])
        # 聚光灯层需要重建
        # 聚光灯已移除
    # 聚光灯与脉冲效果已彻底移除

    def exit_app(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LotteryApp(root)
    root.mainloop()
