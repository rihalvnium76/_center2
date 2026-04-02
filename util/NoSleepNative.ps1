# 完全用 C# 处理，避免 PowerShell 类型问题
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class ExecutionStateManager {
    private const uint ES_CONTINUOUS        = 0x80000000;
    private const uint ES_SYSTEM_REQUIRED   = 0x00000001;
    private const uint ES_DISPLAY_REQUIRED  = 0x00000002;
    private const uint ES_AWAYMODE_REQUIRED = 0x00000040;
    
    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    private static extern uint SetThreadExecutionState(uint esFlags);
    
    private static uint originalState = 0;
    
    public static bool EnableKeepAwake() {
        originalState = SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED);
        return originalState != 0;
    }
    
    public static bool EnableDisplayRequired() {
        originalState = SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED | ES_DISPLAY_REQUIRED);
        return originalState != 0;
    }
    
    public static void Restore() {
        SetThreadExecutionState(ES_CONTINUOUS);
    }
}
"@

try {
    if ([ExecutionStateManager]::EnableKeepAwake()) {
        Write-Host "系统防休眠已启用" -ForegroundColor Green
        Write-Host "按 Ctrl+C 退出并恢复原状态" -ForegroundColor Yellow
        
        # 保持运行
        while ($true) {
            Start-Sleep -Seconds 10
        }
    } else {
        Write-Error "启用防休眠失败"
    }
} finally {
    [ExecutionStateManager]::Restore()
    Write-Host "电源设置已恢复" -ForegroundColor Green
}
