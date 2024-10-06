python -m venv ../.env
..\.env\Scripts\activate
python -m pip install -r ../requirements.txt
pyinstaller -F --noconsole --icon ../utils/pymodoro_icon.ico ../pymodoro.py
Copy-Item -Path "dist/pymodoro.exe" -Destination "bin" -Force
Remove-Item -Recurse -Force build, dist, pymodoro.spec