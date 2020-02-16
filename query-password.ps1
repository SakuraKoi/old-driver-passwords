<#
  使用 . query-password.ps1 初始化函数，然后使用

  * Query-Cjtecc: 查询解压全能王存储的密码
#>

function Query-Cjtecc {
  param([System.IO.FileInfo]$file)
  $md5 = (Get-FileHash -Algorithm MD5 $file).Hash
  $url = "http://app.cjtecc.cn/compress/yun.php?md5=$md5"
  $resp = (Invoke-WebRe	quest $url).Content
  if ($resp -eq "no") {
    echo "未找到密码"
  } else {
    $info = (ConvertFrom-Json -InputObject $resp.Content)
    echo "#$($info.password)#"
  }
}
