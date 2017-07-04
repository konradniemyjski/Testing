
#Powershell Snippit to recive data to HipChat Room read it ad add pop up
#Variables for the json post

[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
$objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon 


function ShowMeSome {
 [CmdletBinding()]
   param(
      [Parameter(Mandatory=$true)][string]$message,
      [ValidateSet("None", "Info", "Warning", "Error")][string]$Type= "Info",
      [string]$Title


   )
   try {
    $objNotifyIcon.Icon = "C:\Windows\Icons\icons8-Reflektor Filled-50.ico"
    $objNotifyIcon.BalloonTipIcon =$type 
    $objNotifyIcon.BalloonTipText = $message 
    $objNotifyIcon.BalloonTipTitle = "Tytul"
    $objNotifyIcon.Visible = $True 
    $objNotifyIcon.ShowBalloonTip(5000)
    }

    catch {
    
    
    [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
    $objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon 
    $objNotifyIcon.Icon = "C:\Windows\Icons\icons8-Reflektor Filled-50.ico"
    $objNotifyIcon.BalloonTipIcon =$type 
    $objNotifyIcon.BalloonTipText = $message 
    $objNotifyIcon.BalloonTipTitle = "Tytul"
    $objNotifyIcon.Visible = $True 
    $objNotifyIcon.ShowBalloonTip(5000)

    
    }


   }



$APIKey = ''

$Room1 = ''# room id is on web available 

$Room2 = ''

$apiuri_Room1 = "http://api.hipchat.com/v2/room/$Room1/history?auth_token=$APIKey”

$apiuri_Room2 = "http://api.hipchat.com/v2/room/$Room2/history?auth_token=$APIKey”


#add Speech assembley so it ca read messages

Add-Type -AssemblyName System.speech 
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer 
$speak.SelectVoice('Microsoft Paulina Desktop')
$arrTime = @('1','2','3')


$start = $false

Do { 
       Start-Sleep -Seconds 3
       

       $cludo = Invoke-RestMethod -Method get -Uri $apiuri_Room1
       $cludo = $cludo.items| select -Last 1


       $platforma = Invoke-RestMethod -Method get -Uri $apiuri_Room2
       $platforma = $platforma.items | select -Last 1
       if ($start) {
       
           if ($cludo.id -ne $old_cludo.id){
       
            $speak.Speak($cludo.message)
            ShowMeSome -message ($cludo.message) -Title ("{0} napisa : " -f $cludo.from.name)   -Type Info
            
           }


       
           if ($platforma.id -ne $old_platforma.id){
       
            $speak.Speak($platforma.message)
           }
       
       }else {
       
       $start = $true
       }
       
       $godzina = $true

       if ( (0 -eq (Get-Date -Format mm)% 15)  ){

       if ($godzina -and ($arrTime -contains (Get-Date -Format ss)% 1 )){
            
           $godzina = $false
           $speak.Speak("Jest teraz   $((Get-Date).ToShortTimeString())")

       }
       }Else {
       $godzina = $true
       }




   } while($true) 


#End of Hipchat Post


