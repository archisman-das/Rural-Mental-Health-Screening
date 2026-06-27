Set-Location 'D:\Project\Rural Mental Heath Screening AI'

$python = 'C:\Users\dasar\AppData\Local\Programs\Python\Python313\python.exe'
$stdout = 'D:\Project\Rural Mental Heath Screening AI\tmp_dashboard_stdout.log'
$stderr = 'D:\Project\Rural Mental Heath Screening AI\tmp_dashboard_stderr.log'

& $python -u dashboard_server.py 1> $stdout 2> $stderr

