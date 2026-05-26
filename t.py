import ctypes
import json
import os
import subprocess
import threading
import time
import tkinter as tk
import sys

import matplotlib
import psutil

matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        master,
        text,
        command,
        palette,
        width=76,
        height=34,
        radius=17,
        fill=None,
        hover_fill=None,
        text_color=None,
        canvas_bg=None,
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=canvas_bg or palette["bg"],
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self.command = command
        self.palette = palette
        self.text = text
        self.radius = radius
        self.fill = fill or palette["card_alt"]
        self.hover_fill = hover_fill or palette["border"]
        self.text_color = text_color or palette["text"]
        self.current_fill = self.fill
        self.is_pressed = False

        self.bind("<Configure>", lambda _event: self.draw())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.draw()

    def draw(self):
        self.delete("all")
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        radius = min(self.radius, width // 2, height // 2)
        fill = self.palette["track"] if self.is_pressed else self.current_fill

        points = [
            radius,
            0,
            width - radius,
            0,
            width,
            0,
            width,
            radius,
            width,
            height - radius,
            width,
            height,
            width - radius,
            height,
            radius,
            height,
            0,
            height,
            0,
            height - radius,
            0,
            radius,
            0,
            0,
        ]
        self.create_polygon(points, smooth=True, fill=fill, outline=self.palette["border"])
        self.create_text(
            width / 2,
            height / 2,
            text=self.text,
            fill=self.text_color,
            font=("Segoe UI", 9, "bold"),
        )

    def set_text(self, text):
        self.text = text
        self.draw()

    def on_enter(self, _event):
        self.current_fill = self.hover_fill
        self.draw()

    def on_leave(self, _event):
        self.current_fill = self.fill
        self.is_pressed = False
        self.draw()

    def on_press(self, _event):
        self.is_pressed = True
        self.draw()

    def on_release(self, event):
        was_pressed = self.is_pressed
        self.is_pressed = False
        self.draw()
        if was_pressed and 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
            self.command()


class TextPill(tk.Canvas):
    def __init__(
        self,
        master,
        text,
        palette,
        width=86,
        height=30,
        fill=None,
        canvas_bg=None,
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=canvas_bg or palette["bg"],
            bd=0,
            highlightthickness=0,
        )
        self.palette = palette
        self.text = text
        self.fill = fill or palette["panel"]
        self.bind("<Configure>", lambda _event: self.draw())
        self.draw()

    def set_text(self, text):
        self.text = text
        self.draw()

    def draw(self):
        self.delete("all")
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        radius = min(height // 2, width // 2)
        self.create_rounded_rect(0, 0, width, height, radius, self.fill, self.palette["border"])
        self.create_text(
            width / 2,
            height / 2,
            text=self.text,
            fill=self.palette["text"],
            font=("Segoe UI", 9, "bold"),
        )

    def create_rounded_rect(self, x1, y1, x2, y2, radius, fill, outline):
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        self.create_polygon(points, smooth=True, fill=fill, outline=outline)


class ToggleSwitch(tk.Canvas):
    def __init__(self, master, text, variable, command, palette, width=118, height=34):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=palette["bg"],
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self.text = text
        self.variable = variable
        self.command = command
        self.palette = palette
        self.hovered = False
        self.bind("<Configure>", lambda _event: self.draw())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonRelease-1>", self.toggle)
        self.draw()

    def draw(self):
        self.delete("all")
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        active = bool(self.variable.get())
        shell = self.palette["card_alt"] if self.hovered else self.palette["panel"]
        track = self.palette["blue"] if active else self.palette["track"]
        knob_x = width - 23 if active else width - 43

        self.create_rounded_rect(0, 0, width, height, height // 2, shell, self.palette["border"])
        self.create_text(
            12,
            height / 2,
            text=self.text,
            fill=self.palette["text"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        self.create_rounded_rect(width - 48, 7, width - 10, height - 7, 10, track, track)
        self.create_oval(
            knob_x,
            10,
            knob_x + 14,
            height - 10,
            fill=self.palette["text"],
            outline=self.palette["text"],
        )

    def create_rounded_rect(self, x1, y1, x2, y2, radius, fill, outline):
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        self.create_polygon(points, smooth=True, fill=fill, outline=outline)

    def on_enter(self, _event):
        self.hovered = True
        self.draw()

    def on_leave(self, _event):
        self.hovered = False
        self.draw()

    def toggle(self, _event):
        self.variable.set(not self.variable.get())
        self.draw()
        self.command()


class MetricCard(tk.Frame):
    def __init__(self, master, title, accent, palette):
        super().__init__(
            master,
            bg=palette["card"],
            highlightbackground=palette["border"],
            highlightthickness=1,
            bd=0,
        )
        self.palette = palette
        self.accent = accent
        self.percent = None

        self.columnconfigure(0, weight=1)

        self.title_label = tk.Label(
            self,
            text=title.upper(),
            bg=palette["card"],
            fg=palette["muted"],
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))

        self.value_label = tk.Label(
            self,
            text="--",
            bg=palette["card"],
            fg=accent,
            font=("Segoe UI", 17, "bold"),
            anchor="w",
        )
        self.value_label.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 0))

        self.subtitle_label = tk.Label(
            self,
            text="",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 8),
            anchor="w",
            justify="left",
            wraplength=220,
        )
        self.subtitle_label.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 6))

        self.bar = tk.Canvas(
            self,
            height=5,
            bg=palette["card"],
            highlightthickness=0,
            bd=0,
        )
        self.bar.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 9))
        self.bar.bind("<Configure>", lambda _event: self.draw_bar())

    def update(self, value, subtitle="", percent=None, accent=None):
        if accent is not None:
            self.accent = accent
            self.value_label.config(fg=accent)
        self.percent = percent
        self.value_label.config(text=value)
        self.subtitle_label.config(text=subtitle)
        self.draw_bar()

    def draw_bar(self):
        self.bar.delete("all")
        width = max(1, self.bar.winfo_width())
        height = max(1, self.bar.winfo_height())
        self.bar.create_rectangle(0, 0, width, height, fill=self.palette["track"], width=0)

        if self.percent is None:
            fill_width = width
            fill = self.palette["border"]
        else:
            fill_width = int(width * min(max(self.percent, 0), 100) / 100)
            fill = self.accent

        self.bar.create_rectangle(0, 0, fill_width, height, fill=fill, width=0)


class SystemMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.palette = {
            "bg": "#0B0F14",
            "panel": "#111822",
            "card": "#17212B",
            "card_alt": "#1E2A35",
            "border": "#2A3948",
            "track": "#253241",
            "text": "#EEF4FA",
            "muted": "#91A0AE",
            "blue": "#38BDF8",
            "violet": "#C084FC",
            "green": "#34D399",
            "amber": "#FBBF24",
            "red": "#F87171",
        }

        self.title("System Monitor")
        self.geometry("1120x720")
        self.minsize(900, 600)
        self.configure(bg=self.palette["bg"])
        self.attributes("-topmost", True)

        self.max_len = 60
        self.cpu_usage = []
        self.mem_usage = []
        self.paused = False
        self.compact = False
        self.micro_mode = False
        self.normal_geometry = "1120x720"
        self.micro_width = 190
        self.micro_height = 94
        self.micro_metric_keys = [
            "gpu",
            "temperature",
            "cpu",
            "ram",
            "disk",
            "network",
            "battery",
            "system",
        ]
        self.micro_metric_index = 0
        self.micro_drag_offset = (0, 0)
        self.update_job = None
        self.last_net = psutil.net_io_counters()
        self.last_net_time = time.monotonic()
        self.is_admin = self.check_admin()
        self.gpu_cache = {
            "title": "GPU LOAD",
            "value": "N/A",
            "subtitle": "Waiting for GPU telemetry",
            "percent": None,
            "accent": self.palette["green"],
            "temperature": None,
        }
        self.gpu_cache_time = 0
        self.gpu_query_running = False
        self.gpu_poll_interval = 3.0
        self.gpu_lock = threading.Lock()
        self.temperature_cache = self.get_empty_temperature_cache("Checking sensors")
        self.temperature_cache_time = 0
        self.temperature_query_running = False
        self.temperature_poll_interval = 5.0
        self.temperature_lock = threading.Lock()
        self.latest_metrics = {}

        self.topmost_var = tk.BooleanVar(value=True)
        self.interval_var = tk.StringVar(value="1000")

        psutil.cpu_percent(interval=None)
        self.build_layout()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_dashboard()

    def build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_shell = tk.Frame(self, bg=self.palette["bg"])
        self.main_shell.grid(row=0, column=0, sticky="nsew")
        self.main_shell.grid_columnconfigure(0, weight=1)
        self.main_shell.grid_rowconfigure(1, weight=1)

        header = tk.Frame(self.main_shell, bg=self.palette["bg"])
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 12))
        header.grid_columnconfigure(0, weight=1)

        title = tk.Label(
            header,
            text="System Monitor",
            bg=self.palette["bg"],
            fg=self.palette["text"],
            font=("Segoe UI", 24, "bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="w")

        self.status_label = tk.Label(
            header,
            text="Live desktop telemetry",
            bg=self.palette["bg"],
            fg=self.palette["muted"],
            font=("Segoe UI", 10),
            anchor="w",
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(1, 0))

        controls = tk.Frame(header, bg=self.palette["bg"])
        controls.grid(row=0, column=1, rowspan=2, sticky="e")

        self.topmost_toggle = ToggleSwitch(
            controls,
            text="Topmost",
            variable=self.topmost_var,
            command=self.toggle_topmost,
            palette=self.palette,
        )
        self.topmost_toggle.grid(row=0, column=0, padx=(0, 10))

        refresh_group = tk.Frame(controls, bg=self.palette["bg"])
        refresh_group.grid(row=0, column=1, padx=(0, 10))

        tk.Label(
            refresh_group,
            text="Refresh",
            bg=self.palette["bg"],
            fg=self.palette["muted"],
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=0, columnspan=3, pady=(0, 2))

        self.refresh_down_button = RoundedButton(
            refresh_group,
            text="-",
            command=lambda: self.adjust_refresh_interval(-250),
            palette=self.palette,
            width=28,
            height=28,
            radius=14,
        )
        self.refresh_down_button.grid(row=1, column=0, padx=(0, 5))

        self.interval_pill = TextPill(
            refresh_group,
            text=f"{self.get_refresh_interval()} ms",
            palette=self.palette,
            width=78,
            height=28,
        )
        self.interval_pill.grid(row=1, column=1)

        self.refresh_up_button = RoundedButton(
            refresh_group,
            text="+",
            command=lambda: self.adjust_refresh_interval(250),
            palette=self.palette,
            width=28,
            height=28,
            radius=14,
        )
        self.refresh_up_button.grid(row=1, column=2, padx=(5, 0))

        actions = tk.Frame(controls, bg=self.palette["bg"])
        actions.grid(row=0, column=2)

        self.pause_button = self.make_button(actions, "Pause", self.toggle_pause)
        self.pause_button.grid(row=0, column=0, padx=(0, 8))

        clear_button = self.make_button(actions, "Clear", self.clear_history)
        clear_button.grid(row=0, column=1, padx=(0, 8))

        self.compact_button = self.make_button(actions, "Compact", self.toggle_compact, width=82)
        self.compact_button.grid(row=0, column=2, padx=(0, 8))

        self.micro_button = self.make_button(actions, "Micro", self.enter_micro_mode, width=72)
        self.micro_button.grid(row=0, column=3)

        self.temp_badge = tk.Label(
            controls,
            text="Temp: --",
            bg=self.palette["bg"],
            fg=self.palette["muted"],
            font=("Segoe UI", 9, "bold"),
        )
        self.temp_badge.grid(row=1, column=2, sticky="e", pady=(4, 0))

        body = tk.Frame(self.main_shell, bg=self.palette["bg"])
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 22))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        chart_panel = tk.Frame(
            body,
            bg=self.palette["panel"],
            highlightbackground=self.palette["border"],
            highlightthickness=1,
            bd=0,
        )
        chart_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        chart_panel.grid_columnconfigure(0, weight=1)
        chart_panel.grid_rowconfigure(1, weight=1)

        chart_header = tk.Frame(chart_panel, bg=self.palette["panel"])
        chart_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 0))
        chart_header.grid_columnconfigure(0, weight=1)

        tk.Label(
            chart_header,
            text="Performance Timeline",
            bg=self.palette["panel"],
            fg=self.palette["text"],
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.chart_hint = tk.Label(
            chart_header,
            text="Last 60 samples",
            bg=self.palette["panel"],
            fg=self.palette["muted"],
            font=("Segoe UI", 9),
            anchor="e",
        )
        self.chart_hint.grid(row=0, column=1, sticky="e")

        self.build_chart(chart_panel)

        self.metrics_panel = tk.Frame(body, bg=self.palette["bg"])
        self.metrics_panel.grid(row=0, column=1, sticky="nsew")
        self.metrics_panel.grid_columnconfigure(0, weight=1)

        self.cards = {
            "gpu": MetricCard(self.metrics_panel, "GPU", self.palette["green"], self.palette),
            "temperature": MetricCard(
                self.metrics_panel, "Temperature", self.palette["amber"], self.palette
            ),
            "cpu": MetricCard(self.metrics_panel, "CPU", self.palette["blue"], self.palette),
            "ram": MetricCard(self.metrics_panel, "Memory", self.palette["violet"], self.palette),
            "disk": MetricCard(self.metrics_panel, "Disk", self.palette["green"], self.palette),
            "network": MetricCard(self.metrics_panel, "Network", self.palette["amber"], self.palette),
            "battery": MetricCard(self.metrics_panel, "Battery", self.palette["green"], self.palette),
            "system": MetricCard(self.metrics_panel, "System", self.palette["blue"], self.palette),
        }

        for index, card in enumerate(self.cards.values()):
            card.grid(row=index, column=0, sticky="ew", pady=(0, 10))

        self.build_micro_layout()

    def build_micro_layout(self):
        self.micro_shell = tk.Frame(self, bg=self.palette["bg"])
        self.micro_shell.grid(row=0, column=0, sticky="nsew")
        self.micro_shell.grid_columnconfigure(0, weight=1)
        self.micro_shell.grid_rowconfigure(0, weight=1)
        self.micro_shell.grid_remove()

        self.micro_panel = tk.Frame(
            self.micro_shell,
            bg=self.palette["card"],
            highlightbackground=self.palette["border"],
            highlightthickness=1,
            bd=0,
        )
        self.micro_panel.grid(row=0, column=0, sticky="nsew")
        self.micro_panel.grid_columnconfigure(0, weight=1)

        self.micro_title = tk.Label(
            self.micro_panel,
            text="GPU LOAD",
            bg=self.palette["card"],
            fg=self.palette["muted"],
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        )
        self.micro_title.grid(row=0, column=0, sticky="ew", padx=(12, 4), pady=(8, 0))

        self.micro_exit_button = RoundedButton(
            self.micro_panel,
            text="Full",
            command=self.exit_micro_mode,
            palette=self.palette,
            width=44,
            height=24,
            radius=12,
            fill=self.palette["card_alt"],
            hover_fill=self.palette["border"],
            canvas_bg=self.palette["card"],
        )
        self.micro_exit_button.grid(row=0, column=1, sticky="ne", padx=(0, 8), pady=(7, 0))

        self.micro_value = tk.Label(
            self.micro_panel,
            text="N/A",
            bg=self.palette["card"],
            fg=self.palette["green"],
            font=("Segoe UI", 22, "bold"),
            anchor="w",
        )
        self.micro_value.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 0))

        self.micro_subtitle = tk.Label(
            self.micro_panel,
            text="Waiting for GPU telemetry",
            bg=self.palette["card"],
            fg=self.palette["text"],
            font=("Segoe UI", 8),
            anchor="w",
        )
        self.micro_subtitle.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 4))

        self.micro_bar = tk.Canvas(
            self.micro_panel,
            height=5,
            bg=self.palette["card"],
            highlightthickness=0,
            bd=0,
        )
        self.micro_bar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 9))

        for widget in (
            self.micro_shell,
            self.micro_panel,
            self.micro_title,
            self.micro_value,
            self.micro_subtitle,
            self.micro_bar,
        ):
            widget.bind("<MouseWheel>", self.on_micro_mouse_wheel)
            widget.bind("<Button-4>", self.on_micro_mouse_wheel)
            widget.bind("<Button-5>", self.on_micro_mouse_wheel)
            widget.bind("<ButtonPress-1>", self.start_micro_drag)
            widget.bind("<B1-Motion>", self.drag_micro_window)

        for event_name in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.micro_exit_button.bind(event_name, self.on_micro_mouse_wheel)

    def build_chart(self, master):
        self.fig = Figure(figsize=(7.2, 5.2), dpi=100, facecolor=self.palette["panel"])
        self.ax_cpu = self.fig.add_subplot(211)
        self.ax_mem = self.fig.add_subplot(212)
        self.fig.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.08, hspace=0.42)

        for ax, title in ((self.ax_cpu, "CPU usage (%)"), (self.ax_mem, "Memory usage (%)")):
            ax.set_facecolor(self.palette["panel"])
            ax.set_title(title, loc="left", color=self.palette["text"], fontsize=11, pad=10)
            ax.set_ylim(0, 100)
            ax.set_xlim(0, self.max_len - 1)
            ax.grid(True, color=self.palette["border"], linewidth=0.8, alpha=0.65)
            ax.tick_params(colors=self.palette["muted"], labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(self.palette["border"])

        self.line_cpu, = self.ax_cpu.plot([], [], color=self.palette["blue"], linewidth=2.5)
        self.line_mem, = self.ax_mem.plot([], [], color=self.palette["violet"], linewidth=2.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().configure(bg=self.palette["panel"], highlightthickness=0)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=14, pady=14)

    def make_button(self, master, text, command, width=76, height=34):
        return RoundedButton(
            master,
            text=text,
            command=command,
            palette=self.palette,
            width=width,
            height=height,
            radius=height // 2,
        )

    def toggle_topmost(self):
        self.attributes("-topmost", True if self.micro_mode else bool(self.topmost_var.get()))
        if hasattr(self, "topmost_toggle"):
            self.topmost_toggle.draw()

    def enter_micro_mode(self):
        if self.micro_mode:
            return

        self.micro_mode = True
        self.normal_geometry = self.geometry()
        x = max(0, self.winfo_x() + self.winfo_width() - self.micro_width - 24)
        y = max(0, self.winfo_y() + 42)

        self.main_shell.grid_remove()
        self.micro_shell.grid()
        self.minsize(1, 1)
        self.resizable(False, False)
        self.geometry(f"{self.micro_width}x{self.micro_height}+{x}+{y}")
        self.update_idletasks()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.lift()
        self.update_micro_display()

    def exit_micro_mode(self):
        if not self.micro_mode:
            return

        self.micro_mode = False
        self.overrideredirect(False)
        self.micro_shell.grid_remove()
        self.main_shell.grid()
        self.resizable(True, True)
        self.minsize(900, 600)
        self.geometry(self.normal_geometry)
        self.attributes("-topmost", bool(self.topmost_var.get()))
        self.after(10, self.lift)

    def start_micro_drag(self, event):
        self.micro_drag_offset = (
            event.x_root - self.winfo_x(),
            event.y_root - self.winfo_y(),
        )

    def drag_micro_window(self, event):
        x = event.x_root - self.micro_drag_offset[0]
        y = event.y_root - self.micro_drag_offset[1]
        self.geometry(f"+{x}+{y}")

    def on_micro_mouse_wheel(self, event):
        if not self.micro_mode:
            return

        if getattr(event, "num", None) == 4 or getattr(event, "delta", 0) > 0:
            self.cycle_micro_metric(-1)
        else:
            self.cycle_micro_metric(1)

    def cycle_micro_metric(self, step):
        self.micro_metric_index = (self.micro_metric_index + step) % len(self.micro_metric_keys)
        self.update_micro_display()

    def update_micro_display(self):
        if not hasattr(self, "micro_title"):
            return

        metrics = self.latest_metrics or {"gpu": self.gpu_cache}
        key = self.micro_metric_keys[self.micro_metric_index]
        metric = metrics.get(key, self.gpu_cache)

        self.micro_title.config(text=metric["title"].upper(), fg=self.palette["muted"])
        self.micro_value.config(text=metric["value"], fg=metric["accent"])
        self.micro_subtitle.config(text=self.shorten(metric["subtitle"], 30))
        self.draw_micro_bar(metric.get("percent"), metric["accent"])

    def draw_micro_bar(self, percent, accent):
        self.micro_bar.delete("all")
        width = max(1, self.micro_bar.winfo_width())
        height = max(1, self.micro_bar.winfo_height())
        self.micro_bar.create_rectangle(0, 0, width, height, fill=self.palette["track"], width=0)

        if percent is None:
            fill_width = width
            fill = self.palette["border"]
        else:
            fill_width = int(width * min(max(percent, 0), 100) / 100)
            fill = accent

        self.micro_bar.create_rectangle(0, 0, fill_width, height, fill=fill, width=0)

    def shorten(self, text, max_length):
        if len(text) <= max_length:
            return text
        return text[: max_length - 3].rstrip() + "..."

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.set_text("Resume" if self.paused else "Pause")
        self.status_label.config(
            text="Updates paused" if self.paused else "Live desktop telemetry"
        )

    def toggle_compact(self):
        self.compact = not self.compact
        if self.compact:
            self.metrics_panel.grid_remove()
            self.compact_button.set_text("Full")
            self.geometry("900x600")
        else:
            self.metrics_panel.grid()
            self.compact_button.set_text("Compact")
            self.geometry("1120x720")

    def clear_history(self):
        self.cpu_usage.clear()
        self.mem_usage.clear()
        self.refresh_chart()

    def adjust_refresh_interval(self, delta):
        interval = self.get_refresh_interval() + delta
        interval = min(max(interval, 500), 5000)
        self.interval_var.set(str(interval))
        self.update_interval_pill()

    def update_interval_pill(self):
        if hasattr(self, "interval_pill"):
            self.interval_pill.set_text(f"{self.get_refresh_interval()} ms")

    def get_refresh_interval(self):
        try:
            interval = int(self.interval_var.get())
        except ValueError:
            interval = 1000
            self.interval_var.set(str(interval))
        interval = min(max(interval, 500), 5000)
        self.interval_var.set(str(interval))
        return interval

    def get_root_disk_path(self):
        if os.name == "nt":
            return os.environ.get("SystemDrive", "C:") + "\\"
        return "/"

    def get_subprocess_creationflags(self):
        if hasattr(subprocess, "CREATE_NO_WINDOW"):
            return subprocess.CREATE_NO_WINDOW
        return 0

    def check_admin(self):
        if os.name != "nt":
            return True

        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except (AttributeError, OSError):
            return False

    def get_app_base_path(self):
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))

    def get_sensor_helper_path(self):
        app_base = self.get_app_base_path()
        project_base = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(app_base, "SensorProbe.exe"),
            os.path.join(project_base, "sensor-helper", "publish", "SensorProbe.exe"),
            os.path.join(
                project_base,
                "sensor-helper",
                "bin",
                "Release",
                "net8.0",
                "win-x64",
                "publish",
                "SensorProbe.exe",
            ),
        ]

        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def get_gpu_details(self):
        now = time.monotonic()
        with self.gpu_lock:
            cache = self.gpu_cache.copy()
            should_refresh = (
                now - self.gpu_cache_time > self.gpu_poll_interval
                and not self.gpu_query_running
            )
            if should_refresh:
                self.gpu_query_running = True

        if should_refresh:
            thread = threading.Thread(target=self.refresh_gpu_cache, daemon=True)
            thread.start()

        return cache

    def refresh_gpu_cache(self):
        try:
            details = self.query_nvidia_gpu() or self.query_windows_gpu()
            if details is None:
                details = {
                    "title": "GPU LOAD",
                    "value": "N/A",
                    "subtitle": "No GPU telemetry",
                    "percent": None,
                    "accent": self.palette["green"],
                    "temperature": None,
                }
        finally:
            if "details" not in locals():
                details = {
                    "title": "GPU LOAD",
                    "value": "N/A",
                    "subtitle": "No GPU telemetry",
                    "percent": None,
                    "accent": self.palette["green"],
                    "temperature": None,
                }
            with self.gpu_lock:
                self.gpu_cache = details
                self.gpu_cache_time = time.monotonic()
                self.gpu_query_running = False

    def query_nvidia_gpu(self):
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=self.get_subprocess_creationflags(),
            )
        except (FileNotFoundError, OSError, subprocess.SubprocessError):
            return None

        if result.returncode != 0 or not result.stdout.strip():
            return None

        line = result.stdout.strip().splitlines()[0]
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 5:
            return None

        name, load, mem_used, mem_total, temp = parts[:5]
        try:
            load_percent = float(load)
            temp_value = float(temp)
        except ValueError:
            return None

        return {
            "title": "GPU LOAD",
            "value": f"{load_percent:.0f}%",
            "subtitle": f"{self.shorten(name, 18)} | {mem_used}/{mem_total} MB | {temp_value:.0f} deg C",
            "percent": load_percent,
            "accent": self.palette["green"],
            "temperature": temp_value,
            "name": name,
        }

    def query_windows_gpu(self):
        if os.name != "nt":
            return None

        command = (
            "$samples = (Get-Counter '\\GPU Engine(*)\\Utilization Percentage').CounterSamples "
            "| Where-Object { $_.InstanceName -match 'engtype_3d' }; "
            "$sum = ($samples | Measure-Object -Property CookedValue -Sum).Sum; "
            "if ($null -eq $sum) { $sum = 0 }; "
            "[math]::Round([math]::Min([double]$sum, 100), 1)"
        )

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    command,
                ],
                capture_output=True,
                text=True,
                timeout=4,
                creationflags=self.get_subprocess_creationflags(),
            )
        except (FileNotFoundError, OSError, subprocess.SubprocessError):
            return None

        if result.returncode != 0 or not result.stdout.strip():
            return None

        try:
            load_percent = float(result.stdout.strip().splitlines()[-1].replace(",", "."))
        except ValueError:
            return None

        return {
            "title": "GPU LOAD",
            "value": f"{load_percent:.0f}%",
            "subtitle": "Windows 3D engine",
            "percent": load_percent,
            "accent": self.palette["green"],
            "temperature": None,
        }

    def get_cpu_temperature(self):
        text, _value = self.get_cpu_temperature_details()
        return text

    def get_cpu_temperature_details(self):
        details = self.get_temperature_details()
        return details["cpu_text"], details["cpu_value"]

    def get_empty_temperature_cache(self, status):
        return {
            "cpu_text": "N/A",
            "cpu_value": None,
            "gpu_text": "N/A",
            "gpu_value": None,
            "primary_text": "N/A",
            "primary_value": None,
            "source": status,
            "status": status,
        }

    def get_temperature_details(self, gpu=None):
        now = time.monotonic()
        with self.temperature_lock:
            cache = self.temperature_cache.copy()
            should_refresh = (
                now - self.temperature_cache_time > self.temperature_poll_interval
                and not self.temperature_query_running
            )
            if should_refresh:
                self.temperature_query_running = True

        if gpu and cache["gpu_value"] is None and gpu.get("temperature") is not None:
            cache["gpu_value"] = gpu["temperature"]
            cache["gpu_text"] = self.format_temperature(gpu["temperature"])
            if cache["primary_value"] is None:
                cache["primary_value"] = gpu["temperature"]
                cache["primary_text"] = cache["gpu_text"]
                cache["source"] = "NVIDIA"
                cache["status"] = "GPU temperature from NVIDIA driver"

        if should_refresh:
            thread = threading.Thread(target=self.refresh_temperature_cache, daemon=True)
            thread.start()

        return cache

    def refresh_temperature_cache(self):
        try:
            details = self.get_empty_temperature_cache("No supported temperature sensor")
            helper_details = self.query_sensor_helper_temperatures()
            psutil_cpu = self.query_psutil_cpu_temperature()
            windows_zone = self.query_windows_thermal_zone()
            nvidia_gpu = self.query_nvidia_temperature()

            if helper_details:
                details.update(helper_details)

            if details["cpu_value"] is None and psutil_cpu:
                details["cpu_value"] = psutil_cpu["value"]
                details["cpu_text"] = self.format_temperature(psutil_cpu["value"])
                details["source"] = psutil_cpu["source"]

            if details["cpu_value"] is None and windows_zone:
                details["cpu_value"] = windows_zone["value"]
                details["cpu_text"] = self.format_temperature(windows_zone["value"])
                details["source"] = windows_zone["source"]

            if details["gpu_value"] is None and nvidia_gpu:
                details["gpu_value"] = nvidia_gpu["value"]
                details["gpu_text"] = self.format_temperature(nvidia_gpu["value"])
                details["source"] = nvidia_gpu["source"]

            primary_value = details["cpu_value"] if details["cpu_value"] is not None else details["gpu_value"]
            details["primary_value"] = primary_value
            details["primary_text"] = self.format_temperature(primary_value)

            if primary_value is not None:
                if details["source"] == "No supported temperature sensor":
                    details["source"] = "Hardware sensor"
                details["status"] = details["source"]
            elif os.name == "nt" and not self.is_admin:
                details["status"] = "Run as administrator for hardware temperatures"
                details["source"] = "Permission required"
            elif self.get_sensor_helper_path() is None:
                details["status"] = "Sensor helper is missing"
                details["source"] = "Helper missing"
        except Exception as exc:
            details = self.get_empty_temperature_cache(f"Temperature read failed: {exc.__class__.__name__}")
        finally:
            with self.temperature_lock:
                self.temperature_cache = details
                self.temperature_cache_time = time.monotonic()
                self.temperature_query_running = False

    def query_sensor_helper_temperatures(self):
        helper_path = self.get_sensor_helper_path()
        if helper_path is None:
            return None

        try:
            result = subprocess.run(
                [helper_path],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=self.get_subprocess_creationflags(),
            )
        except (OSError, subprocess.SubprocessError):
            return None

        if result.returncode != 0 or not result.stdout.strip():
            return None

        try:
            payload = json.loads(result.stdout.strip().splitlines()[-1])
        except (json.JSONDecodeError, IndexError):
            return None

        cpu = payload.get("cpu") or {}
        gpu = payload.get("gpu") or {}
        cpu_value = self.clean_temperature_value(cpu.get("value"))
        gpu_value = self.clean_temperature_value(gpu.get("value"))

        if cpu_value is None and gpu_value is None:
            return None

        source = payload.get("source") or "LibreHardwareMonitor"
        return {
            "cpu_text": self.format_temperature(cpu_value),
            "cpu_value": cpu_value,
            "gpu_text": self.format_temperature(gpu_value),
            "gpu_value": gpu_value,
            "primary_text": self.format_temperature(cpu_value or gpu_value),
            "primary_value": cpu_value if cpu_value is not None else gpu_value,
            "source": source,
            "status": source,
        }

    def query_psutil_cpu_temperature(self):
        try:
            temps = psutil.sensors_temperatures()
        except (AttributeError, OSError):
            return None

        for entries in temps.values():
            for entry in entries:
                label = (entry.label or "").lower()
                if "cpu" in label or "core" in label or not label:
                    value = self.clean_temperature_value(entry.current)
                    if value is not None:
                        return {"value": value, "source": "psutil"}
        return None

    def query_windows_thermal_zone(self):
        if os.name != "nt":
            return None

        command = (
            "$zones = Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature "
            "-ErrorAction SilentlyContinue; "
            "$values = @($zones | ForEach-Object { [math]::Round(($_.CurrentTemperature / 10) - 273.15, 1) } "
            "| Where-Object { $_ -gt 0 -and $_ -lt 125 }); "
            "if ($values.Count -gt 0) { ($values | Measure-Object -Average).Average }"
        )

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    command,
                ],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=self.get_subprocess_creationflags(),
            )
        except (FileNotFoundError, OSError, subprocess.SubprocessError):
            return None

        if result.returncode != 0 or not result.stdout.strip():
            return None

        value = self.clean_temperature_value(result.stdout.strip().splitlines()[-1].replace(",", "."))
        if value is None:
            return None
        return {"value": value, "source": "Windows thermal zone"}

    def query_nvidia_temperature(self):
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=temperature.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=3,
                creationflags=self.get_subprocess_creationflags(),
            )
        except (FileNotFoundError, OSError, subprocess.SubprocessError):
            return None

        if result.returncode != 0 or not result.stdout.strip():
            return None

        value = self.clean_temperature_value(result.stdout.strip().splitlines()[0].replace(",", "."))
        if value is None:
            return None
        return {"value": value, "source": "NVIDIA"}

    def clean_temperature_value(self, value):
        if value is None:
            return None
        try:
            temperature = float(value)
        except (TypeError, ValueError):
            return None
        if temperature <= 0 or temperature >= 125:
            return None
        return temperature

    def format_temperature(self, value):
        value = self.clean_temperature_value(value)
        if value is None:
            return "N/A"
        return f"{value:.1f} deg C"

    def get_temperature_accent(self, value):
        if value is None:
            return self.palette["muted"]
        if value >= 85:
            return self.palette["red"]
        if value >= 70:
            return self.palette["amber"]
        return self.palette["green"]

    def get_temperature_percent(self, value):
        if value is None:
            return None
        return min(max((value / 100) * 100, 0), 100)

    def get_battery_details(self):
        try:
            battery = psutil.sensors_battery()
        except (AttributeError, OSError):
            battery = None

        if battery is None:
            return "N/A", "No battery sensor detected", None

        status = "charging" if battery.power_plugged else "on battery"
        if battery.secsleft == psutil.POWER_TIME_UNLIMITED:
            remaining = "plugged in"
        elif battery.secsleft == psutil.POWER_TIME_UNKNOWN:
            remaining = "time unknown"
        else:
            hours, remainder = divmod(int(battery.secsleft), 3600)
            minutes = remainder // 60
            remaining = f"{hours}h {minutes}m left"

        return f"{battery.percent:.0f}%", f"{status} | {remaining}", battery.percent

    def format_bytes(self, value, suffix="B"):
        value = float(value)
        for unit in ("", "K", "M", "G", "T"):
            if abs(value) < 1024:
                return f"{value:.1f} {unit}{suffix}"
            value /= 1024
        return f"{value:.1f} P{suffix}"

    def format_uptime(self):
        uptime = int(time.time() - psutil.boot_time())
        days, remainder = divmod(uptime, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes = remainder // 60
        if days:
            return f"{days}d {hours}h {minutes}m"
        return f"{hours}h {minutes}m"

    def update_dashboard(self):
        if not self.paused:
            self.capture_metrics()

        self.update_job = self.after(self.get_refresh_interval(), self.update_dashboard)

    def capture_metrics(self):
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(self.get_root_disk_path())
        freq = psutil.cpu_freq()
        net = psutil.net_io_counters()
        now = time.monotonic()
        gpu = self.get_gpu_details()

        elapsed = max(now - self.last_net_time, 0.001)
        download_speed = (net.bytes_recv - self.last_net.bytes_recv) / elapsed
        upload_speed = (net.bytes_sent - self.last_net.bytes_sent) / elapsed
        self.last_net = net
        self.last_net_time = now

        self.cpu_usage.append(cpu)
        self.mem_usage.append(mem.percent)
        if len(self.cpu_usage) > self.max_len:
            self.cpu_usage.pop(0)
            self.mem_usage.pop(0)

        current_freq = (freq.current / 1000) if freq and freq.current else 0
        max_freq = (freq.max / 1000) if freq and freq.max else 0
        temp_details = self.get_temperature_details(gpu)
        temp = temp_details["cpu_text"]
        cpu_temp_value = temp_details["cpu_value"]
        gpu_temp_value = temp_details["gpu_value"]
        gpu_temp_text = temp_details["gpu_text"]
        primary_temp_value = cpu_temp_value if cpu_temp_value is not None else gpu_temp_value
        primary_temp_text = temp_details["primary_text"]
        temp_accent = self.get_temperature_accent(primary_temp_value)
        physical_cores = psutil.cpu_count(logical=False) or "N/A"
        logical_cores = psutil.cpu_count(logical=True) or "N/A"
        battery_value, battery_subtitle, battery_percent = self.get_battery_details()
        uptime_value = self.format_uptime()
        current_time = time.strftime("%H:%M:%S")
        download_value = self.format_bytes(download_speed, "B/s")
        upload_value = self.format_bytes(upload_speed, "B/s")

        self.latest_metrics = {
            "gpu": gpu,
            "temperature": {
                "title": "TEMPERATURE",
                "value": primary_temp_text,
                "subtitle": f"{temp_details['status']} | CPU {temp} | GPU {gpu_temp_text}",
                "percent": self.get_temperature_percent(primary_temp_value),
                "accent": temp_accent,
            },
            "cpu": {
                "title": "CPU LOAD",
                "value": f"{cpu:.1f}%",
                "subtitle": f"{physical_cores}/{logical_cores} cores | {current_freq:.2f} GHz | {temp}",
                "percent": cpu,
                "accent": self.palette["blue"],
            },
            "ram": {
                "title": "RAM",
                "value": f"{mem.percent:.1f}%",
                "subtitle": f"{self.format_bytes(mem.used)} / {self.format_bytes(mem.total)}",
                "percent": mem.percent,
                "accent": self.palette["violet"],
            },
            "disk": {
                "title": "DISK",
                "value": f"{disk.percent:.1f}%",
                "subtitle": f"{self.format_bytes(disk.used)} / {self.format_bytes(disk.total)}",
                "percent": disk.percent,
                "accent": self.palette["green"],
            },
            "network": {
                "title": "NET DOWN",
                "value": download_value,
                "subtitle": f"Up {upload_value}",
                "percent": None,
                "accent": self.palette["amber"],
            },
            "battery": {
                "title": "BATTERY",
                "value": battery_value,
                "subtitle": battery_subtitle,
                "percent": battery_percent,
                "accent": self.palette["green"],
            },
            "system": {
                "title": "UPTIME",
                "value": uptime_value,
                "subtitle": current_time,
                "percent": None,
                "accent": self.palette["blue"],
            },
        }

        self.cards["gpu"].update(
            gpu["value"],
            gpu["subtitle"],
            gpu["percent"],
            gpu["accent"],
        )
        self.cards["temperature"].update(
            primary_temp_text,
            f"{temp_details['status']} | CPU {temp} | GPU {gpu_temp_text}",
            self.get_temperature_percent(primary_temp_value),
            temp_accent,
        )
        self.cards["cpu"].update(
            f"{cpu:.1f}%",
            f"{physical_cores} physical / {logical_cores} logical | {current_freq:.2f} GHz of {max_freq:.2f} GHz | {temp}",
            cpu,
        )
        self.cards["ram"].update(
            f"{mem.percent:.1f}%",
            f"{self.format_bytes(mem.used)} used of {self.format_bytes(mem.total)}",
            mem.percent,
        )
        self.cards["disk"].update(
            f"{disk.percent:.1f}%",
            f"{self.format_bytes(disk.used)} used of {self.format_bytes(disk.total)}",
            disk.percent,
        )
        self.cards["network"].update(
            download_value,
            f"Down | Up {upload_value}",
            None,
        )

        self.cards["battery"].update(battery_value, battery_subtitle, battery_percent)
        self.cards["system"].update(
            uptime_value,
            f"Uptime | {current_time}",
            None,
        )
        if hasattr(self, "temp_badge"):
            self.temp_badge.config(text=f"Temp: {primary_temp_text}", fg=temp_accent)

        self.refresh_chart()
        if self.micro_mode:
            self.update_micro_display()

    def refresh_chart(self):
        x_values = list(range(len(self.cpu_usage)))
        self.line_cpu.set_data(x_values, self.cpu_usage)
        self.line_mem.set_data(x_values, self.mem_usage)
        self.ax_cpu.set_xlim(0, max(self.max_len - 1, len(self.cpu_usage) - 1))
        self.ax_mem.set_xlim(0, max(self.max_len - 1, len(self.mem_usage) - 1))
        self.canvas.draw_idle()

    def on_close(self):
        if self.update_job is not None:
            self.after_cancel(self.update_job)
        self.destroy()


if __name__ == "__main__":
    app = SystemMonitorApp()
    app.mainloop()
