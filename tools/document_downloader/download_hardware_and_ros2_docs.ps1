$ErrorActionPreference = 'Stop'

# Run this script from the ROOT of Local_RAG_Robotics_Assistant.
# Example:
# D:\Sourabh\Python_Projects\ML_EtoE_Projects\Local_RAG_Robotics_Assistant

$ProjectRoot = (Get-Location).Path
$Raw = Join-Path $ProjectRoot 'data\raw'

$Folders = @(
    'sensors\rplidar_c1',
    'sensors\imx219_120',
    'jetson',
    'esp32_c3',
    'motor_driver\bts7960',
    'ros2',
    'audio'
)

foreach ($folder in $Folders) {
    New-Item -ItemType Directory -Force -Path (Join-Path $Raw $folder) | Out-Null
}

function Test-GoodFile {
    param([string]$Path)
    return (Test-Path $Path) -and ((Get-Item $Path).Length -gt 1000)
}

function Download-File {
    param(
        [Parameter(Mandatory=$true)][string]$Url,
        [Parameter(Mandatory=$true)][string]$OutFile,
        [Parameter(Mandatory=$true)][string]$Name,
        [string]$Referer = ''
    )

    if (Test-GoodFile $OutFile) {
        Write-Host "Already present: $Name" -ForegroundColor DarkGreen
        Write-Host "  $OutFile" -ForegroundColor DarkGray
        return
    }

    # Remove an incomplete file left by a previous failed attempt.
    if (Test-Path $OutFile) {
        Remove-Item $OutFile -Force -ErrorAction SilentlyContinue
    }

    Write-Host "Downloading: $Name" -ForegroundColor Cyan

    # First choice on Windows: curl.exe. It handles redirects and vendor CDNs well.
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if ($curl) {
        try {
            $args = @(
                '-L', '--fail', '--silent', '--show-error',
                '--retry', '2', '--retry-delay', '1',
                '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
            )
            if ($Referer) {
                $args += @('-e', $Referer)
            }
            $args += @('-o', $OutFile, $Url)

            & curl.exe @args

            if (($LASTEXITCODE -eq 0) -and (Test-GoodFile $OutFile)) {
                Write-Host "  Saved: $OutFile" -ForegroundColor Green
                return
            }
        }
        catch {
            # Continue to Invoke-WebRequest fallback.
        }
    }

    if (Test-Path $OutFile) {
        Remove-Item $OutFile -Force -ErrorAction SilentlyContinue
    }

    # Fallback: PowerShell request with browser-like headers.
    try {
        $headers = @{
            'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'
            'Accept' = 'text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.8,*/*;q=0.7'
        }
        if ($Referer) {
            $headers['Referer'] = $Referer
        }

        Invoke-WebRequest -Uri $Url -OutFile $OutFile -MaximumRedirection 10 -Headers $headers -UseBasicParsing

        if (Test-GoodFile $OutFile) {
            Write-Host "  Saved: $OutFile" -ForegroundColor Green
            return
        }
        throw 'Downloaded file is empty or unexpectedly small.'
    }
    catch {
        if (Test-Path $OutFile) {
            Remove-Item $OutFile -Force -ErrorAction SilentlyContinue
        }
        Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "  Manual URL: $Url" -ForegroundColor DarkYellow
    }
}

Write-Host "`nRobotics RAG - Hardware + ROS 2 Documentation Downloader v3" -ForegroundColor Magenta
Write-Host "Project root: $ProjectRoot`n"

# ---------------------------------------------------------------------------
# SLAMTEC RPLIDAR C1 / C1M1
# Current official files resolved from SLAMTEC's support/download page.
# ---------------------------------------------------------------------------
$rplidarDir = Join-Path $Raw 'sensors\rplidar_c1'
$slamtecReferer = 'https://www.slamtec.com/en/support'

Download-File `
    'https://bucket-download.slamtec.com/9fd56b14eb46b11ffb38d861db4a7771c70e3095/SLAMTEC_rplidar_datasheet_C1_v1.2_en.pdf' `
    (Join-Path $rplidarDir 'SLAMTEC_RPLIDAR_C1_Datasheet.pdf') `
    'SLAMTEC RPLIDAR C1 Datasheet v1.2' `
    $slamtecReferer

Download-File `
    'https://bucket-download.slamtec.com/d8f3a6cc7e9bfebf07669172d1122043f8a12dc4/SLAMTEC_rplidarkit_usermanual_C1_v1.2_en.pdf' `
    (Join-Path $rplidarDir 'SLAMTEC_RPLIDAR_C1M1_DevKit_User_Manual.pdf') `
    'SLAMTEC RPLIDAR C1/C1M1 User Manual v1.2' `
    $slamtecReferer

# ---------------------------------------------------------------------------
# NVIDIA Jetson Orin Nano / Super Developer Kit
# ---------------------------------------------------------------------------
$jetsonDir = Join-Path $Raw 'jetson'

Download-File `
    'https://developer.nvidia.com/downloads/assets/embedded/secure/jetson/orin_nano/docs/jetson_orin_nano_devkit_carrier_board_specification_sp.pdf' `
    (Join-Path $jetsonDir 'NVIDIA_Jetson_Orin_Nano_Developer_Kit_Carrier_Board_Specification.pdf') `
    'NVIDIA Jetson Orin Nano Developer Kit Carrier Board Specification'

Download-File `
    'https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/' `
    (Join-Path $jetsonDir 'NVIDIA_Jetson_Orin_Nano_Super_User_Guide.html') `
    'NVIDIA Jetson Orin Nano Super Developer Kit User Guide (HTML)'

# ---------------------------------------------------------------------------
# ESP32-C3
# Espressif moved the datasheet from /documentation/ to documentation.espressif.com.
# ---------------------------------------------------------------------------
$espDir = Join-Path $Raw 'esp32_c3'

Download-File `
    'https://documentation.espressif.com/ESP32-C3_Datasheet_en.pdf' `
    (Join-Path $espDir 'Espressif_ESP32-C3_Series_Datasheet.pdf') `
    'Espressif ESP32-C3 Series Datasheet v2.4'

Download-File `
    'https://documentation.espressif.com/esp-hardware-design-guidelines/en/latest/esp32c3/esp-hardware-design-guidelines-en-master-esp32c3.pdf?title=ESP32-C3+Hardware+Design+Guidelines' `
    (Join-Path $espDir 'Espressif_ESP32-C3_Hardware_Design_Guidelines.pdf') `
    'Espressif ESP32-C3 Hardware Design Guidelines'

# ---------------------------------------------------------------------------
# Waveshare IMX219-120 Camera
# ---------------------------------------------------------------------------
$camDir = Join-Path $Raw 'sensors\imx219_120'

Download-File `
    'https://www.waveshare.com/wiki/IMX219-120_Camera' `
    (Join-Path $camDir 'Waveshare_IMX219-120_Camera_Wiki.html') `
    'Waveshare IMX219-120 Camera documentation (HTML)'

# ---------------------------------------------------------------------------
# Infineon BTS7960
# ---------------------------------------------------------------------------
$btsDir = Join-Path $Raw 'motor_driver\bts7960'

Download-File `
    'https://www.infineon.com/assets/row/public/documents/10/57/infineon-bts7960-ds-en.pdf?fileId=db3a304412b407950112b43945006d5d' `
    (Join-Path $btsDir 'Infineon_BTS7960_Datasheet.pdf') `
    'Infineon BTS7960 Datasheet'


# ---------------------------------------------------------------------------
# ROS 2 Humble
# Official ROS 2 Humble documentation sources from the ros2_documentation repo.
# Raw .rst files are preferred for RAG because they contain the clean source
# text without website menus/navigation.
# ---------------------------------------------------------------------------
$ros2Dir = Join-Path $Raw 'ros2'

Download-File `
    'https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.rst' `
    (Join-Path $ros2Dir 'ROS2_Humble_Understanding_Nodes.rst') `
    'ROS 2 Humble - Understanding Nodes'

Download-File `
    'https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.rst' `
    (Join-Path $ros2Dir 'ROS2_Humble_Understanding_Topics.rst') `
    'ROS 2 Humble - Understanding Topics'

Download-File `
    'https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Services/Understanding-ROS2-Services.rst' `
    (Join-Path $ros2Dir 'ROS2_Humble_Understanding_Services.rst') `
    'ROS 2 Humble - Understanding Services'

Download-File `
    'https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Actions/Understanding-ROS2-Actions.rst' `
    (Join-Path $ros2Dir 'ROS2_Humble_Understanding_Actions.rst') `
    'ROS 2 Humble - Understanding Actions'

Download-File `
    'https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Parameters/Understanding-ROS2-Parameters.rst' `
    (Join-Path $ros2Dir 'ROS2_Humble_Understanding_Parameters.rst') `
    'ROS 2 Humble - Understanding Parameters'

Download-File `
    'https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Concepts/Intermediate/About-Quality-of-Service-Settings.rst' `
    (Join-Path $ros2Dir 'ROS2_Humble_QoS_Settings.rst') `
    'ROS 2 Humble - Quality of Service Settings'

Download-File `
    'https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.rst' `
    (Join-Path $ros2Dir 'ROS2_Humble_Python_Publisher_Subscriber.rst') `
    'ROS 2 Humble - Python Publisher and Subscriber'

Download-File `
    'https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Tutorials/Beginner-CLI-Tools/Launching-Multiple-Nodes/Launching-Multiple-Nodes.rst' `
    (Join-Path $ros2Dir 'ROS2_Humble_Launching_Nodes.rst') `
    'ROS 2 Humble - Launching Nodes'

Download-File `
    'https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Tutorials/Intermediate/Tf2/Introduction-To-Tf2.rst' `
    (Join-Path $ros2Dir 'ROS2_Humble_Introduction_to_tf2.rst') `
    'ROS 2 Humble - Introduction to tf2'

# ---------------------------------------------------------------------------
# Generic audio devices: document what is actually known rather than indexing
# an unrelated branded product manual.
# ---------------------------------------------------------------------------
$audioNote = @'
AUDIO HARDWARE NOTE FOR THE ROBOTICS RAG PROJECT

The AMR uses:
- a low-cost generic USB microphone (approximately INR 200)
- a low-cost Bluetooth speaker (approximately INR 250; Mini Boost 4 style / non-genuine JBL)

There is no trustworthy exact manufacturer/model datasheet for these devices.
Do NOT index a random JBL Mini Boost manual or generic microphone manual as if it
represents the actual hardware.

For the RAG knowledge base, document the actual AMR usage instead:
- USB microphone role and connection
- STT / Whisper pipeline
- wake-word / voice-command flow
- speaker role and Bluetooth/USB audio configuration actually used
- TTS pipeline

If the exact microphone chipset or speaker board is identified later, add its real
manufacturer documentation then.
'@
Set-Content -Path (Join-Path $Raw 'audio\README_AUDIO_HARDWARE.txt') -Value $audioNote -Encoding UTF8

Write-Host "`nFinished." -ForegroundColor Magenta
Write-Host "Documents are under: $Raw" -ForegroundColor White
Write-Host "`nCheck the folders for any item marked FAILED." -ForegroundColor Yellow
Write-Host "NVIDIA Super User Guide and Waveshare camera documentation are HTML. ROS 2 documents are RST source files; our loader will support HTML and RST before indexing." -ForegroundColor Yellow
