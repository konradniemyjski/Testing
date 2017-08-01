cls

Add-Type -AssemblyName System.speech 
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer 
$arrTIme = @('1','2','3')

#$speak.GetInstalledVoices().VoiceInfo
$start = $false
$url ='https://www.reddit.com/r/PowerShell/'
$time = 'Yes'
$firt_time = $true
Do { 
       Start-Sleep -Seconds 5

       if ( (0 -eq (Get-Date -Format mm)% 15)  ){
               
           if (((0..4) -eq (Get-Date -Format ss )%31) ){
               if (($time  -eq "Yes")){
               $time = $null
               $Script:time  = $null
               $speak.Speak("Now is   $((Get-Date -Format hh:mm).toString())")
               if ($time -eq $null){
               
                    $time = 'Yes'
               }
               
               
               }
         }      

       }        
        $response = Invoke-WebRequest -Uri $url
        $new_reddit_powershell_info = $response.ParsedHtml.body.getElementsByClassName("top-matter") | select -First 1 textContent
        $new_reddit_powershell_info = $new_reddit_powershell_info.textContent.ToString()
        
        $new_reddit_powershell_info =$new_reddit_powershell_info.Substring(0,($new_reddit_powershell_info.LastIndexOf('(')))

       if (($new_reddit_powershell_info -ne $old_reddit_powershell_info ) -and ($firt_time -ne $true ) ){
                 
                  $speak.SelectVoice('Microsoft David Desktop')
                  $speak.Speak( "Powershell on reddit new entry")

                  $speak.Speak( $new_reddit_powershell_info)

                  $firt_time = $false


       }
       
       $old_reddit_powershell_info = $new_reddit_powershell_info 

} while($true)
