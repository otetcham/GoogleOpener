# OpenInGoogle-V2-Apocrypha

Windows で Microsoft Office ファイル（`.docx`, `.xlsx`, `.pptx` など）を**ダブルクリック**または**右クリックメニュー（「Google で開く」）**からワンタップで Google ドキュメント / スプレッドシート / スライド で開くユーティリティです。

本リポジトリは [drandall70-max/OpenInGoogle-V2](https://github.com/drandall70-max/OpenInGoogle-V2) をフォークし、以下の機能強化を行った拡張版（Apocrypha）です。

---

## 主な追加・強化機能

1. **重複チェック＆自動更新（ローカルキャッシュ DB）**
   - 同じファイルを何度も開いた際に Google ドライブへ同一ファイルが量産される問題を解消しました。
   - ファイルパスおよび SHA-256 ハッシュを `%APPDATA%\OpenInGoogle\cache.db` に記録し、Google ドライブ上にファイルが存在するか確認した上で再利用します。
   - 重複時の動作を4パターンから選択可能：
     - 未変更なら既存を開く / 変更されていれば上書き更新（推奨）
     - 未変更なら既存を開く / 変更されていれば新規作成
     - 毎回確認ダイアログを表示
     - 重複チェックせず常に新規作成
2. **完全日本語対応（日本語 / English 切り替え可）**
   - GUI 設定画面・確認ダイアログ・セットアップ手順・Inno Setup インストーラーを日本語化しました。
3. **豊富な設定画面（GUI）**
   - 引数なしで `OpenInGoogle` を起動すると 3 タブ構成の設定画面が開きます：
     - **基本・アカウント**: ファイル選択起動、Google 認証実行・ログアウト、セットアップガイド、言語切替
     - **アップロード・重複設定**: 保存先ドライブフォルダ名指定、重複チェック方式、Google形式への変換 ON/OFF、アップロード前確認ダイアログ（誤送信防止）、除外フォルダ設定
     - **Windows連携・履歴**: 右クリックメニュー「Google で開く」のワンクリック登録/解除、Windows「既定のアプリ」設定の呼び出し、対応拡張子の個別 ON/OFF、最近の履歴一覧
4. **対応拡張子の拡充**
   - `.docx`, `.doc`, `.rtf`, `.odt` → Google ドキュメント
   - `.xlsx`, `.xls`, `.xlsm`, `.ods`, `.csv` → Google スプレッドシート
   - `.pptx`, `.ppt`, `.odp` → Google スライド

---

## セットアップ方法（ユーザー向け）

1. Google Cloud Console で自分のデスクトップアプリ用 OAuth クライアント ID (`credentials.json`) を作成し、`%APPDATA%\OpenInGoogle\credentials.json` に配置します（アプリ内の「セットアップ手順を表示」ボタンから詳細ガイドが開けます）。
2. `OpenInGoogle.exe`（または `python OpenInGoogle.py`）を起動し、初回のみブラウザで Google アカウント認証を行います。
3. 「Windows連携・履歴」タブから**右クリックメニュー「Google で開く」を登録**するか、Windows の「既定のアプリ」設定で `.docx` 等の既定アプリに `OpenInGoogle` を指定します。

---

## 開発・ビルド方法

### 必要な環境
- Python 3.12+
- 依存パッケージのインストール：
  ```powershell
  pip install -r requirements.txt
  ```

### ユニットテストの実行
```powershell
python -m unittest discover -s tests -v
```

### Windows 用 `.exe` およびインストーラーのビルド
```powershell
pyinstaller OpenInGoogle.spec --clean --noconfirm
iscc .\installer\OpenInGoogle.iss
```
または GitHub Actions の **Build Windows Installer** ワークフローを手動実行（`workflow_dispatch`）することでもインストーラーを自動生成できます。

---

## ライセンス / クレジット

- Original project: [drandall70-max/OpenInGoogle-V2](https://github.com/drandall70-max/OpenInGoogle-V2)
- License: See [LICENSE.txt](LICENSE.txt)
