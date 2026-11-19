# GoogleOpener (OpenInGoogle-V2-Apocrypha)

> **注意 / Disclaimer（非公式ツール）**  
> **GoogleOpener** は個人開発による **Google 非公式のオープンソースユーティリティ** です。Google LLC によって提供・承認・サポートされているものではありません。  
> **GoogleOpener** is an **unofficial open-source utility** and is **not** affiliated with, endorsed by, or supported by Google LLC.

[English](#english) | [日本語](#日本語)

---

## 日本語

**GoogleOpener** は、Windows 上の Microsoft Office ファイル（`.docx`, `.xlsx`, `.pptx` など）を**ダブルクリック**または**右クリックメニュー（「Google で開く」）**からワンタップで Google ドキュメント / スプレッドシート / スライド で開くユーティリティです。

本リポジトリ（`OpenInGoogle-V2-Apocrypha`）は [drandall70-max/OpenInGoogle-V2](https://github.com/drandall70-max/OpenInGoogle-V2) をフォークし、実用性を大幅に強化した拡張版です。

### 主な追加・強化機能

1. **重複チェック＆自動更新（ローカルキャッシュ DB）**
   - 同じファイルを何度も開いた際に Google ドライブへ同一ファイルが量産される問題を解消しました。
   - ファイルパスおよび SHA-256 ハッシュを `%APPDATA%\OpenInGoogle\cache.db` に記録し、Google ドライブ上にファイルが実在するか（ゴミ箱に入っていないか）を検証した上で再利用します。
   - 重複時の動作を4パターンから選択可能：
     - 未変更なら既存を開く / 変更されていれば上書き更新（推奨）
     - 未変更なら既存を開く / 変更されていれば新規作成
     - 毎回確認ダイアログを表示
     - 重複チェックせず常に新規作成
2. **Word / Excel / PowerPoint ごとの専用アイコン**
   - 拡張子グループごとに Google ドキュメント（青）・スプレッドシート（緑）・スライド（黄）風の専用 `.ico` アイコンを同梱し、Windows のファイル関連付け（`DefaultIcon`）および右クリックメニューに自動適用できます。
3. **GitHub Releases からの自動アップデート機能**
   - 設定画面の「基本・アカウント」タブにある「**アップデートを確認**」から、GitHub Releases の最新バージョンを確認・ダウンロードし、自動で実行ファイルを更新・再起動できます。
4. **完全日本語対応（日本語 / English リアルタイム切替）**
   - GUI 設定画面・確認ダイアログ・セットアップ手順・Inno Setup インストーラーを日本語化（設定画面から英語へ即座に切り替え可能）。
5. **豊富な設定画面（3タブ構成 GUI）**
   - 引数なしで起動すると設定画面が開きます：
     - **基本・アカウント**: ファイル選択起動、Google 認証・ログアウト、セットアップ手順、言語切替、アップデート確認
     - **アップロード・重複設定**: Google ドライブ保存先フォルダ名指定、重複チェック方式、Google 形式への変換 ON/OFF、アップロード前確認ダイアログ（誤送信防止）、除外フォルダ設定
     - **Windows連携・履歴**: 右クリックメニュー「Google で開く」の一括登録/解除、ファイル種別アイコン適用、Windows「既定のアプリ」設定呼び出し、対応拡張子の個別 ON/OFF、最近の履歴一覧
6. **左下・最前面の進捗ポップアップ＆キャンセル対応**
   - ファイルを開いた直後から、画面左下に常に最前面で進捗ポップアップ（接続 → 重複確認 → アップロード% → ブラウザ起動）を表示し、処理中でも「キャンセル」ボタンで中断できます。
7. **対応拡張子の拡充**
   - `.docx`, `.doc`, `.rtf`, `.odt` → Google ドキュメント
   - `.xlsx`, `.xls`, `.xlsm`, `.ods`, `.csv` → Google スプレッドシート
   - `.pptx`, `.ppt`, `.odp` → Google スライド

### セットアップ方法（ユーザー向け）

1. [Releases](https://github.com/otetcham/OpenInGoogle-V2-Apocrypha/releases) から最新の `OpenInGoogle.exe`（またはインストーラー）をダウンロードして起動します。
2. Google Cloud Console で自分のデスクトップアプリ用 OAuth クライアント ID (`credentials.json`) を作成し、`%APPDATA%\OpenInGoogle\credentials.json` に配置します（設定画面の「セットアップ手順を表示」から詳細を確認できます）。
   - ※ OAuth 同意画面が「テスト」状態の場合は、Google Cloud Console の「対象」ページで自分の Google アカウントをテストユーザーに追加してください。
3. 設定画面の「今すぐGoogle認証を実行」からログインします。
4. 「Windows連携・履歴」タブから**右クリックメニュー登録**や**ファイル種別アイコン適用**を行い、必要に応じて Windows の「既定のアプリ」に設定してください。

---

## English

**GoogleOpener** (repository: `OpenInGoogle-V2-Apocrypha`) is an **unofficial** Windows utility that lets you open local Microsoft Office files (`.docx`, `.xlsx`, `.pptx`, etc.) directly in Google Docs, Sheets, or Slides via **double-click** or the **right-click context menu**.

This repository (`OpenInGoogle-V2-Apocrypha`) is an enhanced fork of [drandall70-max/OpenInGoogle-V2](https://github.com/drandall70-max/OpenInGoogle-V2).

### What's New in Apocrypha

1. **Duplicate Detection & Smart Update (SQLite Cache)**
   - Solves the original limitation where opening the same file created a new Google Drive file every time.
   - Tracks local file paths and SHA-256 hashes in `%APPDATA%\OpenInGoogle\cache.db` and verifies that the remote file still exists (and is not trashed) before opening.
   - Configurable duplicate handling modes:
     - Open existing if unchanged / Update existing if modified *(Recommended)*
     - Open existing if unchanged / Create new if modified
     - Always ask before uploading
     - Always create a new file
2. **Per-Type Google-Style File Icons**
   - Bundles custom `.ico` icons for Word/Docs (blue), Excel/Sheets (green), and PowerPoint/Slides (yellow), with one-click registration to Windows `DefaultIcon` and context menu entries.
3. **Self-Updater via GitHub Releases**
   - Check for new releases directly from the **General & Account** tab and automatically download and replace `OpenInGoogle.exe`.
4. **Bilingual UI (Japanese / English)**
   - Full Japanese and English localization across the 3-tab settings GUI, dialogs, setup guides, and Inno Setup installer.
5. **Rich Configuration & Security Controls**
   - Custom target Google Drive folder name, toggle Google format conversion, confirmation prompt before upload, excluded folders list, per-extension toggles, and recent upload history viewer.
6. **Bottom-Left Topmost Progress Popup & Cancellation**
   - Displays a compact always-on-top progress card at the bottom-left corner of your screen (preparing → connecting → duplicate check → upload % → opening browser) with a **Cancel** button.
7. **Expanded File Support**
   - **Google Docs**: `.docx`, `.doc`, `.rtf`, `.odt`
   - **Google Sheets**: `.xlsx`, `.xls`, `.xlsm`, `.ods`, `.csv`
   - **Google Slides**: `.pptx`, `.ppt`, `.odp`

### Quick Start

1. Download the latest `OpenInGoogle.exe` (or setup installer) from [Releases](https://github.com/otetcham/OpenInGoogle-V2-Apocrypha/releases).
2. Create a Desktop App OAuth client ID in Google Cloud Console and save it as `%APPDATA%\OpenInGoogle\credentials.json` (click **Open Setup Guide** inside the app for instructions; add your Google account under Test Users if the app is in Testing status).
3. Click **Authenticate with Google Now** in the settings window.
4. Use the **Windows & History** tab to register the right-click context menu, apply file-type icons, or open Windows Default Apps settings.

---

## Development & Build

```powershell
# Install dependencies
pip install -r requirements.txt

# Run unit tests
python -m unittest discover -s tests -v

# Build standalone OpenInGoogle.exe
pyinstaller OpenInGoogle.spec --clean --noconfirm

# Build Windows installer (requires Inno Setup)
iscc .\installer\OpenInGoogle.iss
```

Tagging a release (`v*`) automatically triggers GitHub Actions to run tests, build both `OpenInGoogle.exe` and `OpenInGoogleSetup-Apocrypha-v*.exe`, and publish them to GitHub Releases.

## License / Credits

- Original project: [drandall70-max/OpenInGoogle-V2](https://github.com/drandall70-max/OpenInGoogle-V2)
- License: See [LICENSE.txt](LICENSE.txt)
