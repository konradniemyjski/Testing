function Send-SMS (

    [Parameter(Mandatory=$True)]
    [string]$user = 'Login',
    [Parameter(Mandatory=$True)]
    [string]$password = 'Password',
    [Parameter(Mandatory=$True)]
    [int]$to = "recipient",
    [Parameter(Mandatory=$True)]
    [string]$message = 'message'
)
{
    
    $md5 = new-object -TypeName System.Security.Cryptography.MD5CryptoServiceProvider
    $utf8 = new-object -TypeName System.Text.UTF8Encoding
    $hash = [System.BitConverter]::ToString($md5.ComputeHash($utf8.GetBytes($password)))
    $hash = $hash.ToLower() -replace '-', ''

    $uri = 'https://api.smsapi.pl/sms.do?username='+ $user + '&password=' + $hash + '&from=ECO&to=' + $to + '&message='+$message + '&format=json'
    $resultat = Invoke-WebRequest $uri
    Write-Host $resultat.StatusDescription
}
