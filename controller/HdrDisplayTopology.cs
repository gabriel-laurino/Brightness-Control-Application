// Read-only display discovery. Brightness is deliberately applied by the
// existing PowerShell/DWM routine, not by this class.
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Runtime.InteropServices;

public sealed class HdrDisplay
{
    public string DeviceName { get; internal set; }
    public string FriendlyName { get; internal set; }
    public IntPtr Handle { get; internal set; }
    public uint TargetId { get; internal set; }
    public bool HdrSupported { get; internal set; }
    public bool HdrActive { get; internal set; }
    public string ColorState { get; internal set; }
    public uint SdrWhiteLevel { get; internal set; }
}

public static class HdrDisplayTopology
{
    private const uint QdcOnlyActivePaths = 0x00000002;
    private const uint GetSourceName = 1;
    private const uint GetTargetName = 2;
    private const uint GetAdvancedColorInfo2 = 15;
    private const uint GetSdrWhiteLevel = 11;
    private const int ErrorInsufficientBuffer = 122;

    [StructLayout(LayoutKind.Sequential)]
    private struct Luid { public uint LowPart; public int HighPart; }

    [StructLayout(LayoutKind.Sequential)]
    private struct Rect { public int Left; public int Top; public int Right; public int Bottom; }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct MonitorInfoEx
    {
        public uint Size;
        public Rect Monitor;
        public Rect Work;
        public uint Flags;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
        public string DeviceName;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct PathSourceInfo
    {
        public Luid AdapterId;
        public uint Id;
        public uint ModeInfoIndex;
        public uint StatusFlags;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct Rational { public uint Numerator; public uint Denominator; }

    [StructLayout(LayoutKind.Sequential)]
    private struct PathTargetInfo
    {
        public Luid AdapterId;
        public uint Id;
        public uint ModeInfoIndex;
        public uint OutputTechnology;
        public uint Rotation;
        public uint Scaling;
        public Rational RefreshRate;
        public uint ScanlineOrdering;
        [MarshalAs(UnmanagedType.Bool)] public bool Available;
        public uint StatusFlags;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct PathInfo
    {
        public PathSourceInfo Source;
        public PathTargetInfo Target;
        public uint Flags;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct DeviceInfoHeader
    {
        public uint Type;
        public uint Size;
        public Luid AdapterId;
        public uint Id;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct SourceDeviceName
    {
        public DeviceInfoHeader Header;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
        public string Name;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct TargetDeviceName
    {
        public DeviceInfoHeader Header;
        public uint Flags;
        public uint OutputTechnology;
        public ushort EdidManufactureId;
        public ushort EdidProductCodeId;
        public uint ConnectorInstance;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 64)]
        public string FriendlyName;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
        public string DevicePath;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct AdvancedColorInfo2
    {
        public DeviceInfoHeader Header;
        public uint Flags;
        public uint ColorEncoding;
        public uint BitsPerColorChannel;
        public uint ActiveColorMode;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct SdrWhiteLevelInfo
    {
        public DeviceInfoHeader Header;
        public uint Level;
    }

    private delegate bool MonitorEnumProc(IntPtr monitor, IntPtr deviceContext, IntPtr rectangle, IntPtr data);

    [DllImport("user32.dll")]
    private static extern bool EnumDisplayMonitors(IntPtr deviceContext, IntPtr clip, MonitorEnumProc callback, IntPtr data);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    private static extern bool GetMonitorInfo(IntPtr monitor, ref MonitorInfoEx info);

    [DllImport("user32.dll")]
    private static extern int GetDisplayConfigBufferSizes(uint flags, out uint pathCount, out uint modeCount);

    [DllImport("user32.dll")]
    private static extern int QueryDisplayConfig(uint flags, ref uint pathCount, [Out] PathInfo[] paths,
        ref uint modeCount, IntPtr modes, IntPtr topology);

    [DllImport("user32.dll", EntryPoint = "DisplayConfigGetDeviceInfo")]
    private static extern int GetSourceDeviceName(ref SourceDeviceName packet);

    [DllImport("user32.dll", EntryPoint = "DisplayConfigGetDeviceInfo")]
    private static extern int GetTargetDeviceName(ref TargetDeviceName packet);

    [DllImport("user32.dll", EntryPoint = "DisplayConfigGetDeviceInfo")]
    private static extern int GetColorInfo(ref AdvancedColorInfo2 packet);

    [DllImport("user32.dll", EntryPoint = "DisplayConfigGetDeviceInfo")]
    private static extern int GetSdrLevel(ref SdrWhiteLevelInfo packet);

    public static HdrDisplay[] GetActiveDisplays()
    {
        if (Marshal.SizeOf(typeof(PathInfo)) != 72 || Marshal.SizeOf(typeof(AdvancedColorInfo2)) != 36)
            throw new InvalidOperationException("Unexpected Windows display interop structure size.");

        var monitors = new Dictionary<string, IntPtr>(StringComparer.OrdinalIgnoreCase);
        MonitorEnumProc callback = delegate(IntPtr handle, IntPtr dc, IntPtr rect, IntPtr data)
        {
            var info = new MonitorInfoEx();
            info.Size = (uint)Marshal.SizeOf(typeof(MonitorInfoEx));
            if (GetMonitorInfo(handle, ref info) && !string.IsNullOrEmpty(info.DeviceName))
                monitors[info.DeviceName] = handle;
            return true;
        };
        if (!EnumDisplayMonitors(IntPtr.Zero, IntPtr.Zero, callback, IntPtr.Zero))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "EnumDisplayMonitors failed.");

        for (int attempt = 0; attempt < 3; attempt++)
        {
            uint pathCount, modeCount;
            int error = GetDisplayConfigBufferSizes(QdcOnlyActivePaths, out pathCount, out modeCount);
            if (error != 0) throw new Win32Exception(error, "GetDisplayConfigBufferSizes failed.");
            var paths = new PathInfo[pathCount];
            // DISPLAYCONFIG_MODE_INFO is 64 bytes; only path information is read.
            IntPtr modes = Marshal.AllocHGlobal(checked((int)modeCount * 64));
            try
            {
                error = QueryDisplayConfig(QdcOnlyActivePaths, ref pathCount, paths,
                    ref modeCount, modes, IntPtr.Zero);
                if (error == ErrorInsufficientBuffer) continue;
                if (error != 0) throw new Win32Exception(error, "QueryDisplayConfig failed.");

                var result = new List<HdrDisplay>();
                for (int i = 0; i < pathCount; i++)
                {
                    var path = paths[i];
                    var source = new SourceDeviceName();
                    source.Header.Type = GetSourceName;
                    source.Header.Size = (uint)Marshal.SizeOf(typeof(SourceDeviceName));
                    source.Header.AdapterId = path.Source.AdapterId;
                    source.Header.Id = path.Source.Id;
                    error = GetSourceDeviceName(ref source);
                    if (error != 0) throw new Win32Exception(error, "DisplayConfigGetDeviceInfo(source) failed.");

                    IntPtr handle;
                    if (!monitors.TryGetValue(source.Name, out handle))
                        continue; // Never adjust an unverified or non-desktop target.

                    var targetName = new TargetDeviceName();
                    targetName.Header.Type = GetTargetName;
                    targetName.Header.Size = (uint)Marshal.SizeOf(typeof(TargetDeviceName));
                    targetName.Header.AdapterId = path.Target.AdapterId;
                    targetName.Header.Id = path.Target.Id;
                    string friendlyName = source.Name;
                    if (GetTargetDeviceName(ref targetName) == 0 &&
                        !string.IsNullOrWhiteSpace(targetName.FriendlyName))
                        friendlyName = targetName.FriendlyName;

                    var color = new AdvancedColorInfo2();
                    color.Header.Type = GetAdvancedColorInfo2;
                    color.Header.Size = (uint)Marshal.SizeOf(typeof(AdvancedColorInfo2));
                    color.Header.AdapterId = path.Target.AdapterId;
                    color.Header.Id = path.Target.Id;
                    error = GetColorInfo(ref color);
                    if (error != 0) throw new Win32Exception(error, "DisplayConfigGetDeviceInfo(advanced color) failed.");

                    bool supported = (color.Flags & 0x10) != 0;
                    bool active = (color.Flags & 0x02) != 0 && color.ActiveColorMode == 2;
                    uint sdrLevel = 0;
                    if (active)
                    {
                        var white = new SdrWhiteLevelInfo();
                        white.Header.Type = GetSdrWhiteLevel;
                        white.Header.Size = (uint)Marshal.SizeOf(typeof(SdrWhiteLevelInfo));
                        white.Header.AdapterId = path.Target.AdapterId;
                        white.Header.Id = path.Target.Id;
                        if (GetSdrLevel(ref white) == 0) sdrLevel = white.Level;
                    }
                    result.Add(new HdrDisplay {
                        DeviceName = source.Name,
                        FriendlyName = friendlyName,
                        Handle = handle,
                        TargetId = path.Target.Id,
                        HdrSupported = supported,
                        HdrActive = active,
                        SdrWhiteLevel = sdrLevel,
                        ColorState = color.ActiveColorMode == 2 ? "HDR" :
                            color.ActiveColorMode == 1 ? "WCG" : "SDR"
                    });
                }
                return result.ToArray();
            }
            finally { Marshal.FreeHGlobal(modes); }
        }
        throw new InvalidOperationException("Display topology changed during inspection.");
    }
}
