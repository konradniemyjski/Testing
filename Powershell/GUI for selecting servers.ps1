[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing.Size")

Function OpenFile {
     $OpenFileDialog = New-Object System.Windows.Forms.OpenFileDialog
    $OpenFileDialog.Filter = "All files (*.*)|*.*"
    If($OpenFileDialog.ShowDialog() -eq "OK"){
         $OpenFileDialog.FileName
    }
 }
Remove-Variable File_path -ErrorAction:SilentlyContinue
Remove-Variable domain -ErrorAction:SilentlyContinue
Remove-Variable Next_window -ErrorAction:SilentlyContinue
$Y = 48
$labelSize = New-Object System.Drawing.Size(168,20)
$buttonSize = New-Object System.Drawing.Size(96,23)
$textboxSize = New-Object System.Drawing.Size(240,20)
$Form_SHA1_hasher = New-Object System.Windows.Forms.Form    
    $Form_SHA1_hasher.Size =  New-Object System.Drawing.Size(576,208)
    $Form_SHA1_hasher.text ="Select source" 
    $Form_SHA1_hasher.AutoScale = $True
    $Form_SHA1_hasher.AutoScroll = $True
$button_OpenFile = New-Object System.Windows.Forms.Button
    $button_OpenFile.Location = New-Object System.Drawing.Size(8,$Y)
    $button_OpenFile.Size = $buttonSize
    $button_OpenFile.Text = "Browse for file"
    $button_OpenFile.Add_Click({
    Remove-Variable File_path -ErrorAction:SilentlyContinue
    New-Variable File_path -Scope global -Value (OpenFile)
    $Form_SHA1_hasher.Close()
    })
        $Form_SHA1_hasher.Controls.Add($button_OpenFile)
$label = New-Object  System.Windows.Forms.Label
    $label.Text = "Please select file from which you want to import computers or select AD for all computers, file must contain "
    $label.Location = New-Object System.Drawing.Size(8,10)
    $label.AutoSize = $True
    $Form_SHA1_hasher.Controls.Add($label)
$label = New-Object  System.Windows.Forms.Label
    $label.Text = "ONLY server name. After choosing, you need to wait for a second for another window to pop up."
    $label.Location = New-Object System.Drawing.Size(8,28)
    $label.AutoSize = $True
    $Form_SHA1_hasher.Controls.Add($label)
$button_exit = New-Object System.Windows.Forms.Button
    $button_exit.Location = New-Object System.Drawing.Size(208,$Y)
    $button_exit.Size = $buttonSize
    $button_exit.Text = "Exit"
    $button_exit.Add_Click({
        $Form_SHA1_hasher.Close()
        New-Variable Next_window -Scope global -Value $false   
    })
        $Form_SHA1_hasher.Controls.Add($button_exit)
$button_AD = New-Object System.Windows.Forms.Button
    $button_AD.Location = New-Object System.Drawing.Size(108,$Y)
    $button_AD.Size = $buttonSize
    $button_AD.Text = "Search in AD"
    $button_AD.Add_Click({
        New-Variable domain -value (Get-ADComputer -Filter {OperatingSystem -like "Windows server*"} | select name) -Scope global
        $Form_SHA1_hasher.Close()
    })
        $Form_SHA1_hasher.Controls.Add($button_AD)
$Form_SHA1_hasher.ShowDialog() | Out-Null
if ($Next_window -ne $false){
    Remove-Variable done -ErrorAction:SilentlyContinue
    $Form = New-Object System.Windows.Forms.Form    
    $Form.text ="Select items" 
    $Form.AutoScale = $True
    $Form.AutoScroll = $True
    $Checkboxes += New-Object System.Windows.Forms.CheckBox
    $Checkboxes = @()
    $y = 40
    if ( (($domain | select -First 1 name ).name -ne $null )-and( ($domain | select -First 1 name ).name -cmatch "^[a-z|A-Z]*$" ) ) {
        $use_name = $True
    } else {
        $use_name = $false
        $domain =gc $File_path
    }
    foreach ($a in $domain)
    {    
        $Checkbox = New-Object System.Windows.Forms.CheckBox
        if( $use_name){
            $Checkbox.Text = $a.Name}
        else{
            $Checkbox.Text = $a
        }
        $Checkbox.Location = New-Object System.Drawing.Size(40,$y) 
        $Checkbox.AutoSize = $True
        $Form.Controls.Add($Checkbox) 
        $Checkboxes += $Checkbox
        $y += 30
    }
    $button1 = New-Object system.windows.Forms.Button
    $button1.Text = "Done"
    $button1.TextAlign = "MiddleCenter"
    $button1.Width = 60
    $button1.Height = 30
    $button1.location = new-object system.drawing.point(40,$y)
    $button1.Font = "Microsoft Sans Serif,10"
    $button1.Add_Click({
        New-Variable -Name Done -Scope script -Value $True
        $Form.Close()
    })
    $Form.Controls.Add($button1)
    $button2 = New-Object system.windows.Forms.Button
        $button2.Text = "Exit"
        $button2.TextAlign = "MiddleCenter"
        $button2.Width = 60
        $button2.Height = 30
        $button2.location = new-object system.drawing.point(380,$y)
        $button2.Font = "Microsoft Sans Serif,10"
        $button2.Add_Click({
        $Form.Close()
        })
        $Form.Controls.Add($button2)
    $form.ShowDialog() | Out-Null
    if ($Done){
        $array = @()
    foreach ($boxs in $Checkboxes){
        if ($boxs.Checked -eq 'True'  ){
            $array  += $boxs.Text
        }
    }
    $array}
}
