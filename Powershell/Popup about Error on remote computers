[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
if (-not (Test-Path C:\ProgramData\512.ico)){
    Invoke-WebRequest https://www.iconfinder.com/icons/512541/download/ico/512 -OutFile $env:ALLUSERSPROFILE\512.ico
}

function PopUp(


    [Parameter(Mandatory=$true)]
    [string]$message,
    [Parameter(Mandatory=$true)]
    [string]$server_name
    
    )

{
$objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon 
$objNotifyIcon.Icon = "$env:ALLUSERSPROFILE\512.ico"
$objNotifyIcon.BalloonTipIcon = "Error" 
$objNotifyIcon.BalloonTipText = $message
$objNotifyIcon.BalloonTipTitle = $server_name
$objNotifyIcon.Visible = $True 
$objNotifyIcon.ShowBalloonTip(5000)
}
$domain =Get-ADComputer -Filter {OperatingSystem -like "Windows server*"} | select name

foreach ($server in $domain) {

    foreach ($event in  (Get-EventLog System -EntryType Error  -After (Get-Date).AddMinutes(-10) -ComputerName $server)){
    
        PopUp -message ($event.Message.ToString()) -server_name $Script:server        
    
    }

}
