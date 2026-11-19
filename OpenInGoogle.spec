block_cipher = None
a = Analysis(
    ['OpenInGoogle.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/icons', 'assets/icons')],
    hiddenimports=['googleapiclient','google_auth_oauthlib','google.oauth2','google.auth.transport.requests','tkinter','sqlite3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='OpenInGoogle',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icons/app.ico',
)
