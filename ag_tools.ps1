param (
    [string]$action,
    [string]$path
)

$LOG_FILE = "C:\develop\myllm\logs\powershell.log"

function Write-Log {
    param($msg)
    "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $msg" | Out-File -FilePath $LOG_FILE -Append -Encoding utf8
}

Write-Log "Action: $action, Path: $path 시작"

$AG_EXE = "$env:USERPROFILE\AppData\Local\Programs\Antigravity\Antigravity.exe"

if ($action -eq "load") {
    if (Test-Path $AG_EXE) {
        # 1. 현재 실행 중인 Antigravity 프로세스 확인
        $process = Get-Process Antigravity -ErrorAction SilentlyContinue
        
        if ($process) {
            # 2. 이미 실행 중이면 죽이지 않고 창만 활성화 (Focus)
            Write-Log "이미 실행 중인 Antigravity($($process.Id))를 활성화 시도"
            $wshell = New-Object -ComObject WScript.Shell
            # 모든 인스턴스에 대해 AppActivate 시도 (보안 정책에 따라 한계가 있을 수 있음)
            foreach ($p in $process) {
                Write-Log "AppActivate 실행: ID $($p.Id)"
                $wshell.AppActivate($p.Id) | Out-Null
            }
        }
        else {
            # 3. 실행 중이 아닐 때만 새로 시작
            Write-Log "Antigravity 프로세스가 없어 새로 시작함"
            Start-Process $AG_EXE -ArgumentList "`"$path`""
        }
    }
    else {
        Write-Log "에러: Antigravity 설치 경로를 찾을 수 없음: $AG_EXE"
        Write-Error "❌ Antigravity 설치 경로를 찾을 수 없습니다: $AG_EXE"
    }
}
Write-Log "ag_tools.ps1 종료"
