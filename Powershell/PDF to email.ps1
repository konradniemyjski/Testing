#Requires -Version 5.0
#Requires -RunAsAdministrator

$to = 'xx@yy.com'
$from = 'aa@yy.com'
$subject = 'Disable account report for {0}' -f (Get-Date -Format dd/MM/yyyy) 
$smptpserver = '10.x.x.x'
$Attachments = "C:\Disabled accounts-report.pdf"
$body = @("Hello," ,"Please find new report in attachment.","BR, IT Team")
$body = $body -join "`n"
$zipFile = $env:ALLUSERSPROFILE + '\pdf_dll\itextsharp-all-5.5.10.zip'
$zipFolder =$zipFile.Substring(0, ($zipFile.LastIndexOf('\')))

try {
    #try to load assembly
    Add-Type -Path $zipFolder\itextsharp-dll-cor\itextsharp.dll
    
    }
catch {
    #if failed it will download from the internet
    if(-not (Test-Path $zipFolder ) ){
        
        New-Item $zipFolder  -type directory
        
        }
    try {
    
        Invoke-WebRequest  https://10gbps-io.dl.sourceforge.net/project/itextsharp/itextsharp/iTextSharp-5.5.10/itextsharp-all-5.5.10.zip -OutFile $zipFile 
    
    }
    catch {
    
        Write-Error "Cannot download file from internet please check internet connection and try again."
        Read-Host
        Exit
    
    }
    
    Expand-Archive $zipFile  $zipFolder
    New-Item $zipFolder\itextsharp-dll-cor  -type directory
    Expand-Archive $zipFolder\itextsharp-dll-core.zip  $zipFolder\itextsharp-dll-cor 
    ls $zipFolder\itextsharp-dll-cor | Unblock-File
}

Function Create-PDF([iTextSharp.text.Document]$Document, [string]$File, [int32]$TopMargin, [int32]$BottomMargin, [int32]$LeftMargin, [int32]$RightMargin, [string]$Author)
{
    $Document.SetPageSize([iTextSharp.text.PageSize]::A4)
    $Document.SetMargins($LeftMargin, $RightMargin, $TopMargin, $BottomMargin)
    [void][iTextSharp.text.pdf.PdfWriter]::GetInstance($Document, [System.IO.File]::Create($File))
    $Document.AddAuthor($Author)
}

# Add a text paragraph to the document, optionally with a font name, size and color
function Add-Text([iTextSharp.text.Document]$Document, [string]$Text, [string]$FontName = "Arial", [int32]$FontSize = 12, [string]$Color = "BLACK")
{
    $p = New-Object iTextSharp.text.Paragraph
    $p.Font = [iTextSharp.text.FontFactory]::GetFont($FontName, $FontSize, [iTextSharp.text.Font]::NORMAL, [iTextSharp.text.BaseColor]::$Color)
    $p.SpacingBefore = 2
    $p.SpacingAfter = 2
    $p.Add($Text)
    $Document.Add($p)
}

# Add a title to the document, optionally with a font name, size, color and centered
function Add-Title([iTextSharp.text.Document]$Document, [string]$Text, [Switch]$Centered, [string]$FontName = "Arial", [int32]$FontSize = 16, [string]$Color = "BLACK")
{
    $p = New-Object iTextSharp.text.Paragraph
    $p.Font = [iTextSharp.text.FontFactory]::GetFont($FontName, $FontSize, [iTextSharp.text.Font]::BOLD, [iTextSharp.text.BaseColor]::$Color)
    if($Centered) { $p.Alignment = [iTextSharp.text.Element]::ALIGN_CENTER }
    $p.SpacingBefore = 5
    $p.SpacingAfter = 5
    $p.Add($Text)
    $Document.Add($p)
}

# Add an image to the document, optionally scaled
function Add-Image([iTextSharp.text.Document]$Document, [string]$File, [int32]$Scale = 100)
{
    [iTextSharp.text.Image]$img = [iTextSharp.text.Image]::GetInstance($File)
    $img.ScalePercent(50)
    $Document.Add($img)
}

# Add a table to the document with an array as the data, a number of columns, and optionally centered
function Add-Table([iTextSharp.text.Document]$Document, [string[]]$Dataset, [int32]$Cols = 3, [Switch]$Centered)
{
    $t = New-Object iTextSharp.text.pdf.PDFPTable($Cols)
    $t.SpacingBefore = 5
    $t.SpacingAfter = 5
    if(!$Centered) { $t.HorizontalAlignment = 0 }
    foreach($data in $Dataset)
    {
        $t.AddCell($data);
    }
    $Document.Add($t)
}

#Creating report
$pdf = New-Object iTextSharp.text.Document
Create-PDF -Document $pdf -File $Attachments -TopMargin 20 -BottomMargin 20 -LeftMargin 20 -RightMargin 20 -Author $env:USERNAME
$pdf.Open()
Add-Title -Document $pdf -Text "All locked accounts for $(Get-Date)" -Centered
$ADUser = @()
Get-ADUser -Filter 'Enabled -eq $false' | foreach { $ADUser += $_.GivenName; $ADUser += "" + $_.DistinguishedName }
Add-Table -Document $pdf -Dataset $ADUser -Cols 2 -Centered
$pdf.Close()

#sending mail and removing files
Send-MailMessage -Attachments $Attachments -To $to -From $from -SmtpServer $smptpserver -Subject $subject -Body $body
Remove-Item $Attachments -Force -Confirm:$false
