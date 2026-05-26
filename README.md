# System Monitor

A lightweight desktop dashboard for live system telemetry. The app is built with Tkinter, Matplotlib, and psutil, and it stays available above other windows by default.

## Features

- Live CPU and memory charts with the last 60 samples.
- Always-on-top window mode, enabled by default and available as a polished toggle.
- Pause, resume, and clear controls for the live chart history.
- Adjustable refresh interval from 500 ms to 5000 ms with rounded controls.
- Compact mode for keeping the monitor visible while working.
- Micro mode: a tiny always-on-top overlay that displays one metric at a time.
- Mouse wheel switching in Micro mode for GPU, temperature, CPU, memory, disk, network, battery, and uptime.
- Metric cards for GPU, temperature, CPU, memory, disk usage, network speed, battery status, and system uptime.
- Rounded desktop controls and a refined dark interface with clearer spacing and contrast.
- Native C# sensor helper powered by LibreHardwareMonitor for better Windows temperature support.

## Requirements

- Python 3.10 or newer
- Windows, macOS, or Linux
- Python packages listed in `requirements.txt`
- .NET SDK 8 or newer if you want to rebuild the native sensor helper

Some hardware sensors, such as CPU temperature, GPU temperature, GPU usage, or battery status, may be unavailable on certain systems. When that happens, the app displays `N/A` for that metric. NVIDIA GPU usage and temperature are detected through `nvidia-smi` when available; Windows GPU engine counters are used as a usage fallback. The Windows executable requests administrator access because many hardware sensors are blocked for normal user processes.

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
dotnet publish .\sensor-helper\SensorProbe.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o .\sensor-helper\publish
python -m PyInstaller --noconfirm --clean SystemMonitor.spec
```

The generated executable will be placed in `dist/SystemMonitor.exe`. On launch, Windows may show a UAC prompt so the app can read protected hardware sensors.

## Controls

- `Topmost`: keeps the window above other applications.
- `Refresh -/+`: changes how often metrics are updated.
- `Pause` / `Resume`: stops or continues live updates.
- `Clear`: resets the chart history.
- `Compact` / `Full`: switches between the full dashboard and a smaller chart-focused view.
- `Micro`: opens the tiny overlay mode.
- Mouse wheel over the Micro mode window: cycles through the available metrics.
- `Full` inside Micro mode: returns to the full dashboard.

## Technologies

- Tkinter for the desktop UI
- Matplotlib for live charts
- psutil for system metrics
- C# and LibreHardwareMonitor for Windows hardware temperatures
