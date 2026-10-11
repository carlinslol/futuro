' Financas do casal - roda o sincronizar.bat SEM abrir janela.
'
' A tarefa agendada nao chama o .bat direto: todo .bat abre um console, que
' piscaria na tela a cada rodada. O wscript nao tem janela e inicia o .bat
' oculto. O que o .bat escreveria na tela vai para o sincronizar.log.

Option Explicit

Dim sh, fso, pasta, bat, logArq, q, f, codigo

Set sh  = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
q = Chr(34)

pasta  = fso.GetParentFolderName(WScript.ScriptFullName)
bat    = fso.BuildPath(pasta, "sincronizar.bat")
logArq = fso.BuildPath(pasta, "sincronizar.log")

' log passou de 1 MB: guarda o anterior como .old e comeca outro
If fso.FileExists(logArq) Then
  If fso.GetFile(logArq).Size > 1048576 Then
    If fso.FileExists(logArq & ".old") Then fso.DeleteFile logArq & ".old", True
    fso.MoveFile logArq, logArq & ".old"
  End If
End If

If Not fso.FileExists(bat) Then
  Set f = fso.OpenTextFile(logArq, 8, True)
  f.WriteLine "[" & Now & "] [ERRO] sincronizar_oculto.vbs nao achou o sincronizar.bat"
  f.Close
  WScript.Quit 2
End If

sh.CurrentDirectory = pasta

' cmd /c ""bat" /auto >> "log" 2>&1": o cmd tira o primeiro e o ultimo
' par de aspas e sobra o comando com os caminhos entre aspas.
' 0 = janela oculta; True = espera terminar, para o Agendador ver o codigo.
codigo = sh.Run("cmd /c " & q & q & bat & q & " /auto >> " & q & logArq & q & " 2>&1" & q, 0, True)

WScript.Quit codigo
