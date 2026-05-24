# System Monitor

A lightweight desktop dashboard for live system telemetry. The app is built with Tkinter, Matplotlib, and psutil, and it stays available above other windows by default.

## Features

- Live CPU and memory charts with the last 60 samples.
- Always-on-top window mode, enabled by default and available as a toggle.
- Pause, resume, and clear controls for the live chart history.
- Adjustable refresh interval from 500 ms to 5000 ms.
- Compact mode for keeping the monitor visible while working.
- Metric cards for CPU, memory, disk usage, network speed, battery status, and system uptime.
- Dark desktop-friendly interface with clearer spacing and contrast.

## Requirements

- Python 3.10 or newer
- Windows, macOS, or Linux
- Python packages listed in `requirements.txt`

Some hardware sensors, such as CPU temperature or battery status, may be unavailable on certain systems. When that happens, the app displays `N/A` for that metric.

## Installation

Clone the repository:

```bash
git clone https://github.com/deputat1k/system-monitor.git
cd system-monitor
```

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS or Linux, activate it with:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running

```bash
python t.py
```

## Ready-to-Run Build

A ready Windows executable is available at:

```text
dist/SystemMonitor.exe
```

Run this file directly if you do not want to start the app from Python. The first launch can take a few seconds because the executable unpacks its bundled runtime.

## Building the Executable

Install PyInstaller:

```bash
pip install pyinstaller
```

Build from the included spec file:

```bash
python -m PyInstaller --noconfirm --clean SystemMonitor.spec
```

The generated executable will be placed in `dist/SystemMonitor.exe`.

## Controls

- `Always on top`: keeps the window above other applications.
- `Refresh`: changes how often metrics are updated.
- `Pause` / `Resume`: stops or continues live updates.
- `Clear`: resets the chart history.
- `Compact` / `Full`: switches between the full dashboard and a smaller chart-focused view.

## Technologies

- Tkinter for the desktop UI
- Matplotlib for live charts
- psutil for system metrics
