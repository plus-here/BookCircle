param(
    [string]$HostName = "127.0.0.1",
    [switch]$Https
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$UserFrontend = Join-Path $Root "frontend-user"
$AdminFrontend = Join-Path $Root "frontend-admin"
$Python = Join-Path $Backend ".venv-win\Scripts\python.exe"
$Daphne = Join-Path $Backend ".venv-win\Scripts\daphne.exe"

$EnvFile = Join-Path $Root ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            return
        }
        $parts = $line.Split("=", 2)
        $name = $parts[0].Trim()
        $value = $parts[1].Trim().Trim('"').Trim("'")
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

function Get-LanIp {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -notlike "127.*" -and $_.PrefixOrigin -ne "WellKnown" -and $_.InterfaceAlias -notlike "*VPN*" } |
        Select-Object -First 1 -ExpandProperty IPAddress)
    if (-not $ip) {
        $ip = (Get-NetIPAddress -AddressFamily IPv4 |
            Where-Object { $_.IPAddress -notlike "127.*" -and $_.PrefixOrigin -ne "WellKnown" } |
            Select-Object -First 1 -ExpandProperty IPAddress)
    }
    return $ip
}

function Ensure-DevHttpsCertificate {
    param(
        [string]$CertDirectory,
        [string]$LanIp
    )

    if (-not (Test-Path $CertDirectory)) {
        New-Item -ItemType Directory -Path $CertDirectory | Out-Null
    }

    $pfxPath = Join-Path $CertDirectory "bookcircle-local.pfx"
    $cerPath = Join-Path $CertDirectory "bookcircle-local.cer"
    $password = "bookcircle-dev"
    if (Test-Path $pfxPath) {
        if (-not (Test-Path $cerPath)) {
            $existingCert = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($pfxPath, $password)
            [System.IO.File]::WriteAllBytes(
                $cerPath,
                $existingCert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
            )
        }
        return @{ Pfx = $pfxPath; Password = $password }
    }

    $rsa = [System.Security.Cryptography.RSA]::Create(2048)
    $dn = New-Object System.Security.Cryptography.X509Certificates.X500DistinguishedName("CN=BookCircle Local Dev")
    $req = [System.Security.Cryptography.X509Certificates.CertificateRequest]::new(
        $dn,
        $rsa,
        [System.Security.Cryptography.HashAlgorithmName]::SHA256,
        [System.Security.Cryptography.RSASignaturePadding]::Pkcs1
    )

    $san = [System.Security.Cryptography.X509Certificates.SubjectAlternativeNameBuilder]::new()
    $san.AddDnsName("localhost")
    $san.AddIpAddress([System.Net.IPAddress]::Parse("127.0.0.1"))
    if ($LanIp) {
        $san.AddIpAddress([System.Net.IPAddress]::Parse($LanIp))
    }
    $req.CertificateExtensions.Add($san.Build())
    $req.CertificateExtensions.Add(
        [System.Security.Cryptography.X509Certificates.X509BasicConstraintsExtension]::new($false, $false, 0, $true)
    )
    $req.CertificateExtensions.Add(
        [System.Security.Cryptography.X509Certificates.X509KeyUsageExtension]::new(
            [System.Security.Cryptography.X509Certificates.X509KeyUsageFlags]::DigitalSignature -bor
            [System.Security.Cryptography.X509Certificates.X509KeyUsageFlags]::KeyEncipherment,
            $true
        )
    )

    $oids = [System.Security.Cryptography.OidCollection]::new()
    $oids.Add([System.Security.Cryptography.Oid]::new("1.3.6.1.5.5.7.3.1")) | Out-Null
    $req.CertificateExtensions.Add(
        [System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension]::new($oids, $false)
    )

    $cert = $req.CreateSelfSigned([DateTimeOffset]::Now.AddDays(-1), [DateTimeOffset]::Now.AddYears(2))
    $bytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Pfx, $password)
    [System.IO.File]::WriteAllBytes($pfxPath, $bytes)
    [System.IO.File]::WriteAllBytes(
        $cerPath,
        $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
    )

    return @{ Pfx = $pfxPath; Password = $password }
}

function Test-PortListening {
    param([int]$Port)
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $conn
}

function Start-ServiceIfNeeded {
    param(
        [string]$Name,
        [int]$Port,
        [string]$FilePath,
        [string[]]$ArgumentList,
        [string]$WorkingDirectory,
        [string]$StdOut,
        [string]$StdErr
    )

    if (Test-PortListening -Port $Port) {
        Write-Host "$Name already running on port $Port"
        return
    }

    Start-Process `
        -FilePath $FilePath `
        -ArgumentList $ArgumentList `
        -WorkingDirectory $WorkingDirectory `
        -WindowStyle Hidden `
        -RedirectStandardOutput $StdOut `
        -RedirectStandardError $StdErr

    Write-Host "Started $Name on port $Port"
}

if (-not (Test-Path $Python)) {
    Write-Host "Missing backend virtualenv: $Python"
    Write-Host "Create it first with: python -m venv backend\.venv-win"
    exit 1
}

$LanIp = Get-LanIp
if ($Https) {
    $cert = Ensure-DevHttpsCertificate -CertDirectory (Join-Path $Root ".cert") -LanIp $LanIp
    $env:VITE_HTTPS_PFX = $cert.Pfx
    $env:VITE_HTTPS_PFX_PASSPHRASE = $cert.Password
    Write-Host "HTTPS enabled for Vite dev server"
} else {
    Remove-Item Env:\VITE_HTTPS_PFX -ErrorAction SilentlyContinue
    Remove-Item Env:\VITE_HTTPS_PFX_PASSPHRASE -ErrorAction SilentlyContinue
}

if ($HostName -eq "0.0.0.0") {
    Remove-Item Env:\VITE_API_BASE -ErrorAction SilentlyContinue
    Remove-Item Env:\VITE_WS_BASE -ErrorAction SilentlyContinue
}

Start-ServiceIfNeeded `
    -Name "Django API" `
    -Port 8000 `
    -FilePath $Python `
    -ArgumentList @("manage.py", "runserver", "$($HostName):8000", "--noreload") `
    -WorkingDirectory $Backend `
    -StdOut (Join-Path $Backend "runserver-8000.log") `
    -StdErr (Join-Path $Backend "runserver-8000.err.log")

Start-ServiceIfNeeded `
    -Name "Daphne WebSocket" `
    -Port 8001 `
    -FilePath $Daphne `
    -ArgumentList @("-b", $HostName, "-p", "8001", "config.asgi:application") `
    -WorkingDirectory $Backend `
    -StdOut (Join-Path $Backend "daphne-8001.log") `
    -StdErr (Join-Path $Backend "daphne-8001.err.log")

Start-ServiceIfNeeded `
    -Name "User frontend" `
    -Port 5173 `
    -FilePath "npm.cmd" `
    -ArgumentList @("run", "dev", "--", "--host", $HostName, "--port", "5173") `
    -WorkingDirectory $UserFrontend `
    -StdOut (Join-Path $UserFrontend "vite-5173.log") `
    -StdErr (Join-Path $UserFrontend "vite-5173.err.log")

Start-ServiceIfNeeded `
    -Name "Admin frontend" `
    -Port 5174 `
    -FilePath "npm.cmd" `
    -ArgumentList @("run", "dev", "--", "--host", $HostName, "--port", "5174") `
    -WorkingDirectory $AdminFrontend `
    -StdOut (Join-Path $AdminFrontend "vite-5174.log") `
    -StdErr (Join-Path $AdminFrontend "vite-5174.err.log")

Write-Host ""
Write-Host "BookCircle is ready:"
$Scheme = if ($Https) { "https" } else { "http" }
$WsScheme = if ($Https) { "wss" } else { "ws" }
Write-Host "  User:  $($Scheme)://localhost:5173/"
Write-Host "  Admin: $($Scheme)://localhost:5174/login"
Write-Host "  API:   http://$($HostName):8000"
Write-Host "  WS:    ws://$($HostName):8001"
if ($HostName -eq "0.0.0.0") {
    if ($LanIp) {
        Write-Host ""
        Write-Host "LAN preview:"
        Write-Host "  User:  $($Scheme)://$($LanIp):5173/"
        Write-Host "  Admin: $($Scheme)://$($LanIp):5174/login"
        Write-Host "  API:   http://$($LanIp):8000"
        Write-Host "  WS:    $($WsScheme)://$($LanIp):5173/ws"
        if ($Https) {
            Write-Host ""
            Write-Host "If your phone shows a certificate warning, open advanced options and continue."
        }
    }
}
