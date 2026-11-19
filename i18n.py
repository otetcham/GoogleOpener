from __future__ import annotations

from typing import Any, Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "ja": {
        "app_title": "OpenInGoogle Apocrypha",
        "menu_open_file": "Officeファイルを選択して開く",
        "tab_general": "基本・アカウント",
        "tab_upload": "アップロード・重複設定",
        "tab_windows": "Windows連携・履歴",
        "account_section": "Google アカウント連携",
        "cred_status_ok": "credentials.json: 設定済み",
        "cred_status_missing": "credentials.json: 未設定（下のガイドから設定してください）",
        "token_status_ok": "ログイン状態: 認証済み (token.json あり)",
        "token_status_missing": "ログイン状態: 未認証（ファイルを開く際にブラウザで認証します）",
        "btn_open_file": "ファイルを選んでGoogleで開く...",
        "btn_auth_now": "今すぐGoogle認証を実行",
        "btn_logout": "ログアウト (認証解除)",
        "btn_setup_guide": "セットアップ手順を表示",
        "btn_open_appdata": "設定フォルダを開く",
        "btn_open_gcloud": "Google Cloud Consoleを開く",
        "lang_label": "表示言語:",
        "lang_ja": "日本語",
        "lang_en": "English",
        "drive_folder_label": "Googleドライブ保存先フォルダ名 (空欄でマイドライブ直下):",
        "dup_mode_label": "重複ファイル検出時の動作:",
        "dup_mode_open_or_update": "未変更なら既存を開く / 変更されていれば上書き更新 (推奨)",
        "dup_mode_open_or_new": "未変更なら既存を開く / 変更されていれば新規作成",
        "dup_mode_ask": "既存が見つかったら毎回確認する",
        "dup_mode_always_new": "重複チェックせず常に新規作成する",
        "match_hash_label": "別パスにある同一内容ファイル（SHA-256一致）も重複とみなす",
        "convert_format_label": "Google ドキュメント / スプレッドシート / スライド形式に変換して開く",
        "confirm_upload_label": "アップロード前に毎回確認ダイアログを表示する（誤送信防止）",
        "show_dup_notice_label": "既存ファイルを開いたときに通知・情報ログを保持する",
        "excluded_folders_label": "自動アップロードを禁止する除外フォルダ (1行に1パス):",
        "btn_add_excluded": "フォルダを追加...",
        "btn_save_settings": "設定を保存",
        "settings_saved_title": "設定保存",
        "settings_saved_msg": "設定を保存しました。",
        "win_integration_section": "Windows エクスプローラー連携",
        "context_menu_status_on": "右クリックメニュー「Google で開く」: 登録済み",
        "context_menu_status_off": "右クリックメニュー「Google で開く」: 未登録",
        "btn_register_ctx": "右クリックメニューを登録",
        "btn_unregister_ctx": "右クリックメニューを解除",
        "btn_apply_icons": "ファイル種別アイコンを適用 (Docs/Sheets/Slides)",
        "icons_applied_msg": "Word / Excel / PowerPoint 用の Google アイコンを適用しました。\n（※ エクスプローラーのアイコン更新に数秒かかる場合があります）",
        "btn_open_default_apps": "Windows「既定のアプリ」設定を開く",
        "version_label": "現在のバージョン: v{version}",
        "btn_check_update": "アップデートを確認",
        "update_checking_msg": "GitHub で最新リリースを確認中...",
        "update_up_to_date": "現在お使いのバージョン (v{version}) は最新です。",
        "update_available_msg": "新しいバージョン ({latest}) が公開されています（現在: v{current}）。\n\n今すぐダウンロードしてアップデートしますか？",
        "update_started_msg": "アップデータを起動しました。アプリを終了して更新を適用します。",
        "update_downloaded_source_msg": "最新版をダウンロードしました:\n{path}\n\nフォルダを開きますので実行してください。",
        "update_error_msg": "アップデートの確認中にエラーが発生しました:\n{err}",
        "extensions_section": "対応拡張子（ダブルクリック / 右クリック対象）:",
        "history_section": "最近のアップロード / 重複キャッシュ履歴:",
        "col_file": "ファイル名",
        "col_status": "最終更新日時",
        "col_path": "ローカルパス",
        "btn_open_selected_history": "選択項目をGoogleで開く",
        "btn_clear_history": "キャッシュ履歴をすべてクリア",
        "history_cleared_msg": "重複チェック用のキャッシュ履歴をクリアしました。",
        "ctx_registered_msg": "右クリックメニュー「Google で開く」を登録しました。",
        "ctx_unregistered_msg": "右クリックメニュー「Google で開く」を解除しました。",
        "auth_success_msg": "Google アカウントの認証が完了しました。",
        "logout_confirm": "Google アカウントの認証情報 (token.json) を削除してログアウトしますか？",
        "logout_done": "ログアウトしました。",
        "choose_file_title": "Googleで開くOfficeファイルを選択",
        "supported_files_filter": "対応Officeファイル",
        "all_files_filter": "すべてのファイル",
        "err_file_not_found": "ファイルが見つかりません:\n{path}",
        "err_unsupported_ext": "未対応または設定で無効化されている拡張子です: {ext}\n\n設定画面から対応拡張子を確認してください。",
        "err_excluded_folder": "このファイルは除外フォルダ内にあります:\n{path}\n\nセキュリティ設定により自動アップロードを中止しました。",
        "confirm_upload_msg": "次のファイルを Google ドライブにアップロードして開きますか？\n\nファイル: {name}\nパス: {path}",
        "confirm_update_msg": "同じパスのファイルが以前アップロードされています。\nローカルファイルが変更されているため、どう処理しますか？\n\n[はい] 既存のGoogleファイルを上書き更新して開く\n[いいえ] 新規ファイルとしてアップロードする\n[キャンセル] 中止",
        "confirm_existing_msg": "同一のファイルがすでに Google ドライブに存在します。\n\nファイル: {name}\n\n[はい] 既存のGoogleファイルを開く（おすすめ）\n[いいえ] 新規ファイルとしてアップロードする\n[キャンセル] 中止",
        "err_no_link": "アップロードは成功しましたが、GoogleからWebリンクが返されませんでした。",
        "setup_prompt_msg": (
            "OpenInGoogle を使用するには、Google OAuth デスクトップアプリの認証ファイルが必要です。\n\n"
            "保存先フォルダと日本語のセットアップ手順書を開きました。\n\n"
            "必要なファイル名: credentials.json\n"
            "保存先フォルダ:\n{app_dir}\n\n"
            "ブラウザで Google Cloud Console の設定ページを開きますか？"
        ),
        "setup_prompt_title": "OpenInGoogle 初期設定",
        "err_credentials_missing": (
            "Google 認証情報 (credentials.json) がまだ設定されていません。\n\n"
            "次のフォルダに credentials.json を配置してから、もう一度ファイルを開いてください:\n{cred_file}"
        ),
        "help_text": (
            "Google OAuth 認証ファイル (credentials.json) の取得・配置手順\n"
            "================================================================\n\n"
            "必要なファイル名: credentials.json\n"
            "保存先フォルダ:\n    {app_dir}\n\n"
            "【手順】\n"
            "1. Google Cloud Console にアクセスします:\n"
            "   {console_url}\n\n"
            "2. プロジェクトを新規作成または選択します（例: OpenInGoogle Personal）。\n\n"
            "3. Google Drive API を有効化します:\n"
            "   {api_url}\n\n"
            "4. OAuth 同意画面を設定します:\n"
            "   - User Type: 外部 (External)\n"
            "   - アプリ名: OpenInGoogle Personal\n"
            "   - テストユーザーに自分の Google アカウントを追加してください。\n\n"
            "5. OAuth クライアント ID を作成します:\n"
            "   {cred_url}\n"
            "   「認証情報を作成」>「OAuth クライアント ID」> アプリケーションの種類「デスクトップ アプリ」\n\n"
            "6. 作成された JSON ファイルをダウンロードし、ファイル名を\n"
            "   credentials.json に変更して次のフォルダへ移動してください:\n"
            "   {app_dir}\n\n"
            "7. OpenInGoogle からファイルを開くと、初回のみブラウザでログイン画面が開きます。\n"
            "※ credentials.json と token.json は他人と共有しないでください。\n"
        ),
    },
    "en": {
        "app_title": "OpenInGoogle Apocrypha",
        "menu_open_file": "Choose Office File to Open",
        "tab_general": "General & Account",
        "tab_upload": "Upload & Duplicates",
        "tab_windows": "Windows & History",
        "account_section": "Google Account Connection",
        "cred_status_ok": "credentials.json: Found",
        "cred_status_missing": "credentials.json: Missing (follow setup guide below)",
        "token_status_ok": "Sign-in Status: Authenticated (token.json exists)",
        "token_status_missing": "Sign-in Status: Not signed in (will prompt on first upload)",
        "btn_open_file": "Choose File & Open in Google...",
        "btn_auth_now": "Authenticate with Google Now",
        "btn_logout": "Sign Out (Remove token.json)",
        "btn_setup_guide": "Open Setup Guide",
        "btn_open_appdata": "Open Config Folder",
        "btn_open_gcloud": "Open Google Cloud Console",
        "lang_label": "Language:",
        "lang_ja": "日本語",
        "lang_en": "English",
        "drive_folder_label": "Google Drive Target Folder Name (blank for My Drive root):",
        "dup_mode_label": "Duplicate File Handling:",
        "dup_mode_open_or_update": "Open existing if unchanged / Update existing if modified (Recommended)",
        "dup_mode_open_or_new": "Open existing if unchanged / Create new if modified",
        "dup_mode_ask": "Always ask when existing file is found",
        "dup_mode_always_new": "Always create a new file (disable duplicate check)",
        "match_hash_label": "Also detect duplicates by content hash (SHA-256) across different paths",
        "convert_format_label": "Convert to Google Docs / Sheets / Slides format",
        "confirm_upload_label": "Ask for confirmation before every upload",
        "show_dup_notice_label": "Keep duplicate / cache activity history",
        "excluded_folders_label": "Excluded Folders (never auto-upload, 1 path per line):",
        "btn_add_excluded": "Add Folder...",
        "btn_save_settings": "Save Settings",
        "settings_saved_title": "Settings Saved",
        "settings_saved_msg": "Settings have been saved.",
        "win_integration_section": "Windows Explorer Integration",
        "context_menu_status_on": "Context Menu 'Open in Google': Registered",
        "context_menu_status_off": "Context Menu 'Open in Google': Not registered",
        "btn_register_ctx": "Register Context Menu",
        "btn_unregister_ctx": "Unregister Context Menu",
        "btn_apply_icons": "Apply File Type Icons (Docs/Sheets/Slides)",
        "icons_applied_msg": "Applied Google-style icons for Word / Excel / PowerPoint files.",
        "btn_open_default_apps": "Open Windows Default Apps Settings",
        "version_label": "Current version: v{version}",
        "btn_check_update": "Check for Updates",
        "update_checking_msg": "Checking GitHub Releases...",
        "update_up_to_date": "You are running the latest version (v{version}).",
        "update_available_msg": "A new version ({latest}) is available (current: v{current}).\n\nDownload and update now?",
        "update_started_msg": "Updater launched. The app will close to apply the update.",
        "update_downloaded_source_msg": "Downloaded the latest release to:\n{path}",
        "update_error_msg": "Failed to check for updates:\n{err}",
        "extensions_section": "Supported Extensions:",
        "history_section": "Recent Upload & Duplicate Cache History:",
        "col_file": "File Name",
        "col_status": "Updated At",
        "col_path": "Local Path",
        "btn_open_selected_history": "Open Selected in Google",
        "btn_clear_history": "Clear All Cache History",
        "history_cleared_msg": "Duplicate cache history cleared.",
        "ctx_registered_msg": "Registered 'Open in Google' context menu.",
        "ctx_unregistered_msg": "Unregistered 'Open in Google' context menu.",
        "auth_success_msg": "Google account authentication succeeded.",
        "logout_confirm": "Remove token.json and sign out from Google?",
        "logout_done": "Signed out successfully.",
        "choose_file_title": "Choose an Office file to open in Google",
        "supported_files_filter": "Supported Office files",
        "all_files_filter": "All files",
        "err_file_not_found": "File not found:\n{path}",
        "err_unsupported_ext": "Unsupported or disabled file extension: {ext}",
        "err_excluded_folder": "This file is inside an excluded folder:\n{path}\n\nAuto-upload blocked by security settings.",
        "confirm_upload_msg": "Upload and open this file in Google Drive?\n\nFile: {name}\nPath: {path}",
        "confirm_update_msg": "This file was previously uploaded, and the local file has changed.\n\n[Yes] Update the existing Google file\n[No] Upload as a new file\n[Cancel] Abort",
        "confirm_existing_msg": "An identical file already exists in Google Drive.\n\nFile: {name}\n\n[Yes] Open existing Google file (Recommended)\n[No] Upload as a new file\n[Cancel] Abort",
        "err_no_link": "Upload succeeded, but Google did not return a web link.",
        "setup_prompt_msg": (
            "OpenInGoogle needs a Google OAuth Desktop App credential file.\n\n"
            "Required file name: credentials.json\n"
            "Required folder:\n{app_dir}\n\n"
            "Open Google Cloud setup pages in your browser?"
        ),
        "setup_prompt_title": "OpenInGoogle Setup",
        "err_credentials_missing": (
            "Google credentials (credentials.json) are not set up yet.\n\n"
            "Save credentials.json here:\n{cred_file}\n\nThen try again."
        ),
        "help_text": (
            "SAVE YOUR GOOGLE CREDENTIALS HERE\n\n"
            "Required file name: credentials.json\n"
            "Required folder:\n    {app_dir}\n\n"
            "1. Go to Google Cloud Console: {console_url}\n"
            "2. Create or select a project.\n"
            "3. Enable Google Drive API: {api_url}\n"
            "4. Configure OAuth consent screen & add yourself as a test user.\n"
            "5. Create OAuth client ID (Desktop app): {cred_url}\n"
            "6. Download JSON, rename to credentials.json, and place in:\n    {app_dir}\n"
        ),
    },
}


def t(key: str, lang: str = "ja", **kwargs: Any) -> str:
    table = TRANSLATIONS.get(lang, TRANSLATIONS["ja"])
    template = table.get(key) or TRANSLATIONS["en"].get(key) or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template
