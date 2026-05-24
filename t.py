import os
import time
import tkinter as tk

import matplotlib
import psutil

matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


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
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 0))

        self.value_label = tk.Label(
            self,
            text="--",
            bg=palette["card"],
            fg=accent,
            font=("Segoe UI", 21, "bold"),
            anchor="w",
        )
        self.value_label.grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 0))

        self.subtitle_label = tk.Label(
            self,
            text="",
            bg=palette["card"],
            fg=palette["text"],
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            wraplength=230,
        )
        self.subtitle_label.grid(row=2, column=0, sticky="ew", padx=14, pady=(2, 10))

        self.bar = tk.Canvas(
            self,
            height=6,
            bg=palette["card"],
            highlightthickness=0,
            bd=0,
        )
        self.bar.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 14))
        self.bar.bind("<Configure>", lambda _event: self.draw_bar())

    def update(self, value, subtitle="", percent=None):
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
        self.geometry("1040x700")
        self.minsize(820, 560)
        self.configure(bg=self.palette["bg"])
        self.attributes("-topmost", True)

        self.max_len = 60
        self.cpu_usage = []
        self.mem_usage = []
        self.paused = False
        self.compact = False
        self.update_job = None
        self.last_net = psutil.net_io_counters()
        self.last_net_time = time.monotonic()

        self.topmost_var = tk.BooleanVar(value=True)
        self.interval_var = tk.StringVar(value="1000")

        psutil.cpu_percent(interval=None)
        self.build_layout()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_dashboard()

    def build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = tk.Frame(self, bg=self.palette["bg"])
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

        self.topmost_check = tk.Checkbutton(
            controls,
            text="Always on top",
            variable=self.topmost_var,
            command=self.toggle_topmost,
            bg=self.palette["bg"],
            fg=self.palette["text"],
            activebackground=self.palette["bg"],
            activeforeground=self.palette["text"],
            selectcolor=self.palette["panel"],
            font=("Segoe UI", 9, "bold"),
        )
        self.topmost_check.grid(row=0, column=0, padx=(0, 10))

        tk.Label(
            controls,
            text="Refresh",
            bg=self.palette["bg"],
            fg=self.palette["muted"],
            font=("Segoe UI", 9),
        ).grid(row=0, column=1, padx=(0, 6))

        self.interval_spin = tk.Spinbox(
            controls,
            from_=500,
            to=5000,
            increment=250,
            textvariable=self.interval_var,
            width=6,
            justify="center",
            bg=self.palette["panel"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            buttonbackground=self.palette["card_alt"],
            relief="flat",
            font=("Segoe UI", 9),
        )
        self.interval_spin.grid(row=0, column=2, padx=(0, 6))

        tk.Label(
            controls,
            text="ms",
            bg=self.palette["bg"],
            fg=self.palette["muted"],
            font=("Segoe UI", 9),
        ).grid(row=0, column=3, padx=(0, 12))

        self.pause_button = self.make_button(controls, "Pause", self.toggle_pause)
        self.pause_button.grid(row=0, column=4, padx=(0, 8))

        clear_button = self.make_button(controls, "Clear", self.clear_history)
        clear_button.grid(row=0, column=5, padx=(0, 8))

        self.compact_button = self.make_button(controls, "Compact", self.toggle_compact)
        self.compact_button.grid(row=0, column=6)

        body = tk.Frame(self, bg=self.palette["bg"])
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
            "cpu": MetricCard(self.metrics_panel, "CPU", self.palette["blue"], self.palette),
            "ram": MetricCard(self.metrics_panel, "Memory", self.palette["violet"], self.palette),
            "disk": MetricCard(self.metrics_panel, "Disk", self.palette["green"], self.palette),
            "network": MetricCard(self.metrics_panel, "Network", self.palette["amber"], self.palette),
            "battery": MetricCard(self.metrics_panel, "Battery", self.palette["green"], self.palette),
            "system": MetricCard(self.metrics_panel, "System", self.palette["blue"], self.palette),
        }

        for index, card in enumerate(self.cards.values()):
            card.grid(row=index, column=0, sticky="ew", pady=(0, 10))

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

    def make_button(self, master, text, command):
        return tk.Button(
            master,
            text=text,
            command=command,
            bg=self.palette["card_alt"],
            fg=self.palette["text"],
            activebackground=self.palette["border"],
            activeforeground=self.palette["text"],
            relief="flat",
            bd=0,
            padx=12,
            pady=7,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )

    def toggle_topmost(self):
        self.attributes("-topmost", bool(self.topmost_var.get()))

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")
        self.status_label.config(
            text="Updates paused" if self.paused else "Live desktop telemetry"
        )

    def toggle_compact(self):
        self.compact = not self.compact
        if self.compact:
            self.metrics_panel.grid_remove()
            self.compact_button.config(text="Full")
            self.geometry("820x560")
        else:
            self.metrics_panel.grid()
            self.compact_button.config(text="Compact")
            self.geometry("1040x700")

    def clear_history(self):
        self.cpu_usage.clear()
        self.mem_usage.clear()
        self.refresh_chart()

    def get_refresh_interval(self):
        try:
            interval = int(self.interval_var.get())
        except ValueError:
            interval = 1000
            self.interval_var.set(str(interval))
        return min(max(interval, 500), 5000)

    def get_root_disk_path(self):
        if os.name == "nt":
            return os.environ.get("SystemDrive", "C:") + "\\"
        return "/"

    def get_cpu_temperature(self):
        try:
            temps = psutil.sensors_temperatures()
        except (AttributeError, OSError):
            return "N/A"

        for entries in temps.values():
            for entry in entries:
                label = (entry.label or "").lower()
                if "cpu" in label or "core" in label or not label:
                    return f"{entry.current:.1f} deg C"
        return "N/A"

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
        temp = self.get_cpu_temperature()
        physical_cores = psutil.cpu_count(logical=False) or "N/A"
        logical_cores = psutil.cpu_count(logical=True) or "N/A"

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
            self.format_bytes(download_speed, "B/s"),
            f"Down | Up {self.format_bytes(upload_speed, 'B/s')}",
            None,
        )

        battery_value, battery_subtitle, battery_percent = self.get_battery_details()
        self.cards["battery"].update(battery_value, battery_subtitle, battery_percent)
        self.cards["system"].update(
            self.format_uptime(),
            f"Uptime | {time.strftime('%H:%M:%S')}",
            None,
        )

        self.refresh_chart()

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
