#Powershell script to recive data to HipChat Room
#Variables for the json post

$APIKey = ''
$Room1 = '' 
$Room2 = ''

$apiuri_Room1 = "http://api.hipchat.com/v2/room/$Room1/history?auth_token=$APIKey”
$apiuri_Room2 = "http://api.hipchat.com/v2/room/$Room2/history?auth_token=$APIKey”

Add-Type -AssemblyName System.speech 
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer 

$start = $false

Do { 
       Start-Sleep -Seconds 3     

       $Chat1 = Invoke-RestMethod -Method get -Uri $apiuri_Room1
       $Chat1_one = $Chat1.items| select -Last 1
       $arrChat1 = @($Chat1.items)
       $arrChat1.IndexOf($Chat1_one)

       $Chat2 = Invoke-RestMethod -Method get -Uri $apiuri_Room2
       $Chat2_one = $Chat2.items | select -Last 1
       $arrChat2 = @($Chat2.items)
              
       if ($start) {
       
           if ($arrChat1.IndexOf($Chat1_one) -ne $old_Chat1.IndexOf($Chat1_one)){
            
                foreach ($index in ($arrChat1.IndexOf($Chat1_one)..99)) {

                    $speak.Speak($arrChat1[$index].message)
           
                }
           }



           if ($arrChat2.IndexOf($Chat2_one) -ne $old_Chat2.IndexOf($Chat2_one)){
            
                foreach ($index in ($arrChat2.IndexOf($Chat2_one)..99)) {

                    $speak.Speak($arrChat2[$index].message)
           
                }
           }
       
           if ($Chat2.id -ne $old_Chat2.id){
       
            $speak.Speak($Chat2.message)
           }
       
       }else {
       
       $start = $true
       }


       $old_Chat1 = $arrChat1

       $old_Chat2 = $arrChat2
       

   } while($true) 
