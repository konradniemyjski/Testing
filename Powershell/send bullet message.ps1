function Send-bullet {

param(

    [Parameter(Mandatory=$True)]
    [string]$title, 

    [Parameter(Mandatory=$True)]
    [string]$msg


)

    
begin{

$apikey = $null
$PushURL = "https://api.pushbullet.com/v2/pushes"

if ($apikey -eq $null ){Write-warning "Please put API KEY. You can  create it on https://www.pushbullet.com/#settings/account"
        BREAK}


$cred = New-Object System.Management.Automation.PSCredential ($apikey,(ConvertTo-SecureString $apikey -AsPlainText -Force))

}


process{
    $body_reqest = @{
    type = "note"
    title = $title
    body = $msg
    }

    Invoke-WebRequest -Uri $PushURL -Credential $cred -Method Post -Body $body_reqest 

    }

}


Send-bullet
