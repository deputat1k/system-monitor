import tkinter as tk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

class SystemMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("System monitor")
        self.configure(bg="#121212")

        self.cpu_usage = []
        self.mem_usage = []
        self.max_len = 60

        plt.style.use('dark_background')
        self.fig, (self.ax_cpu, self.ax_mem) = plt.subplots(2, 1, figsize=(7, 6))
        self.fig.tight_layout(pad=3)

        for ax in (self.ax_cpu, self.ax_mem):
            ax.set_facecolor('#121212')
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.yaxis.label.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.title.set_color('white')

        self.ax_cpu.set_title("CPU Usage (%)")
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.set_xlim(0, self.max_len)

        self.ax_mem.set_title("RAM Usage (%)")
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.set_xlim(0, self.max_len)

        self.line_cpu, = self.ax_cpu.plot([], [], 'cyan', linewidth=2)
        self.line_mem, = self.ax_mem.plot([], [], 'magenta', linewidth=2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(pady=10)

        self.label_cpu = tk.Label(self, text="CPU: 0%", font=("Segoe UI", 14), bg="#121212", fg="cyan")
        self.label_cpu.pack()
        self.label_cpu_freq = tk.Label(self, text="CPU speed: 0 MHz", font=("Segoe UI", 12), bg="#121212", fg="cyan")
        self.label_cpu_freq.pack()

        self.label_battery = tk.Label(self, text="Battery: N/A", font=("Segoe UI", 12), bg="#121212", fg="orange")
        self.label_battery.pack()

        self.label_mem = tk.Label(self, text="RAM: 0%", font=("Segoe UI", 14), bg="#121212", fg="magenta")
        self.label_mem.pack()
        self.label_mem_info = tk.Label(self, text="Memory: 0 MB / 0 MB", font=("Segoe UI", 12), bg="#121212", fg="magenta")
        self.label_mem_info.pack()

        self.ani = animation.FuncAnimation(self.fig, self.update_plot, interval=1000, cache_frame_data=False)

    def get_battery_status(self):
        battery = psutil.sensors_battery()
        if battery is None:
            return "Battery: N/A"
        percent = battery.percent
        charging = battery.power_plugged
        status = "on charging" if charging else "not on charge"
        return f"Battery: {percent:.0f}% ({status})"

    def update_plot(self, frame):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        freq = psutil.cpu_freq()
        cpu_freq = freq.current if freq else 0

        self.cpu_usage.append(cpu)
        self.mem_usage.append(mem.percent)

        if len(self.cpu_usage) > self.max_len:
            self.cpu_usage.pop(0)
            self.mem_usage.pop(0)

        x = list(range(len(self.cpu_usage)))

        self.line_cpu.set_data(x, self.cpu_usage)
        self.line_mem.set_data(x, self.mem_usage)

        self.ax_cpu.set_xlim(0, self.max_len)
        self.ax_mem.set_xlim(0, self.max_len)

        self.label_cpu.config(text=f"CPU: {cpu:.1f}%")
        self.label_cpu_freq.config(text=f"CPU speed: {cpu_freq:.1f} MHz")
        self.label_battery.config(text=self.get_battery_status())
        self.label_mem.config(text=f"RAM: {mem.percent:.1f}%")
        self.label_mem_info.config(text=f"Memory: {mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB")

        self.canvas.draw_idle()

if __name__ == "__main__":
    app = SystemMonitorApp()
    app.mainloop()
