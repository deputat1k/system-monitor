using System.Text.Json;
using LibreHardwareMonitor.Hardware;

var readings = new List<TemperatureReading>();

try
{
    var computer = new Computer
    {
        IsCpuEnabled = true,
        IsGpuEnabled = true,
        IsMotherboardEnabled = true,
        IsMemoryEnabled = true,
        IsStorageEnabled = true,
        IsControllerEnabled = true
    };

    computer.Open();

    foreach (var hardware in computer.Hardware)
    {
        VisitHardware(hardware, readings);
    }

    computer.Close();

    var result = new ProbeResult
    {
        Ok = readings.Count > 0,
        Source = "LibreHardwareMonitor",
        Cpu = PickCpu(readings),
        Gpu = PickGpu(readings),
        Temperatures = readings
            .OrderBy(reading => reading.HardwareType)
            .ThenBy(reading => reading.Hardware)
            .ThenBy(reading => reading.Name)
            .ToList()
    };

    WriteJson(result);
}
catch (Exception ex)
{
    WriteJson(new ProbeResult
    {
        Ok = false,
        Source = "LibreHardwareMonitor",
        Error = ex.GetType().Name + ": " + ex.Message,
        Temperatures = readings
    });
}

static void VisitHardware(IHardware hardware, List<TemperatureReading> readings)
{
    hardware.Update();

    foreach (var subHardware in hardware.SubHardware)
    {
        VisitHardware(subHardware, readings);
    }

    foreach (var sensor in hardware.Sensors)
    {
        if (sensor.SensorType != SensorType.Temperature || sensor.Value is null)
        {
            continue;
        }

        readings.Add(new TemperatureReading
        {
            Hardware = hardware.Name,
            HardwareType = hardware.HardwareType.ToString(),
            Name = string.IsNullOrWhiteSpace(sensor.Name) ? "Temperature" : sensor.Name,
            Value = Math.Round(sensor.Value.Value, 1)
        });
    }
}

static TemperatureReading? PickCpu(List<TemperatureReading> readings)
{
    return readings
        .Where(reading => reading.HardwareType.Contains("Cpu", StringComparison.OrdinalIgnoreCase))
        .OrderByDescending(reading => ScoreCpuSensor(reading.Name))
        .ThenByDescending(reading => reading.Value)
        .FirstOrDefault();
}

static TemperatureReading? PickGpu(List<TemperatureReading> readings)
{
    return readings
        .Where(reading => reading.HardwareType.Contains("Gpu", StringComparison.OrdinalIgnoreCase))
        .OrderByDescending(reading => ScoreGpuSensor(reading.Name))
        .ThenByDescending(reading => reading.Value)
        .FirstOrDefault();
}

static int ScoreCpuSensor(string name)
{
    if (name.Contains("package", StringComparison.OrdinalIgnoreCase))
    {
        return 4;
    }

    if (name.Contains("tdie", StringComparison.OrdinalIgnoreCase) ||
        name.Contains("tctl", StringComparison.OrdinalIgnoreCase))
    {
        return 3;
    }

    if (name.Contains("core", StringComparison.OrdinalIgnoreCase))
    {
        return 2;
    }

    return 1;
}

static int ScoreGpuSensor(string name)
{
    if (name.Contains("hot spot", StringComparison.OrdinalIgnoreCase))
    {
        return 2;
    }

    return 1;
}

static void WriteJson(ProbeResult result)
{
    Console.WriteLine(JsonSerializer.Serialize(result, new JsonSerializerOptions
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = false
    }));
}

internal sealed class ProbeResult
{
    public bool Ok { get; set; }
    public string Source { get; set; } = "";
    public string? Error { get; set; }
    public TemperatureReading? Cpu { get; set; }
    public TemperatureReading? Gpu { get; set; }
    public List<TemperatureReading> Temperatures { get; set; } = [];
}

internal sealed class TemperatureReading
{
    public string Hardware { get; set; } = "";
    public string HardwareType { get; set; } = "";
    public string Name { get; set; } = "";
    public double Value { get; set; }
}
