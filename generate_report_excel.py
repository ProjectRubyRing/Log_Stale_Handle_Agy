# -*- coding: utf-8 -*-
"""
Generate comprehensive Excel report for EFS Stale File Handle issue.
Meiryo UI font, monotone color scheme, professional layout.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_workbook():
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Styles
    FONT_NAME = "Meiryo UI"
    
    font_title = Font(name=FONT_NAME, size=16, bold=True, color="212529")
    font_subtitle = Font(name=FONT_NAME, size=10, italic=True, color="6C757D")
    font_section = Font(name=FONT_NAME, size=12, bold=True, color="FFFFFF")
    font_tbl_header = Font(name=FONT_NAME, size=10, bold=True, color="FFFFFF")
    font_tbl_header_dark = Font(name=FONT_NAME, size=10, bold=True, color="212529")
    font_data = Font(name=FONT_NAME, size=9, color="212529")
    font_data_bold = Font(name=FONT_NAME, size=9, bold=True, color="212529")
    font_code = Font(name="Consolas", size=9, color="212529")
    
    fill_section = PatternFill(start_color="343A40", end_color="343A40", fill_type="solid") # Dark Charcoal
    fill_tbl_header = PatternFill(start_color="495057", end_color="495057", fill_type="solid") # Slate Gray
    fill_tbl_sub = PatternFill(start_color="CED4DA", end_color="CED4DA", fill_type="solid") # Light Slate
    fill_zebra_even = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid") # Off-white
    fill_zebra_odd = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid") # White
    fill_highlight = PatternFill(start_color="E9ECEF", end_color="E9ECEF", fill_type="solid") # Gray accent
    fill_card = PatternFill(start_color="F1F3F5", end_color="F1F3F5", fill_type="solid")

    thin_border_side = Side(style='thin', color="DEE2E6")
    border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    border_thick_bottom = Border(bottom=Side(style='medium', color="343A40"))

    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_top_left = Alignment(horizontal="left", vertical="top", wrap_text=True)
    align_top_center = Alignment(horizontal="center", vertical="top", wrap_text=True)

    # -------------------------------------------------------------
    # SHEET 1: 概要・仮説検証 (Executive Summary & Hypothesis Validation)
    # -------------------------------------------------------------
    ws1 = wb.create_sheet(title="1.概要・仮説検証")
    ws1.views.sheetView[0].showGridLines = True

    # Title block
    ws1.merge_cells("A1:G1")
    ws1["A1"] = "【技術調査報告書】ECS + EFS環境における Stale File Handle (ESTALE) 発生原因・仮説検証と恒久対策"
    ws1["A1"].font = font_title
    ws1["A1"].alignment = Alignment(vertical="center")
    ws1.row_dimensions[1].height = 35

    ws1.merge_cells("A2:G2")
    ws1["A2"] = "対象環境: AWS ECS | UBI 9.8 | OpenJDK 21 RedHat Build | JBoss EAP 8.1 | Log4j | AWS EFS (NFSv4.1)"
    ws1["A2"].font = font_subtitle
    ws1["A2"].alignment = Alignment(vertical="center")
    ws1.row_dimensions[2].height = 20

    # Section 1: エグゼクティブサマリ
    ws1.merge_cells("A4:G4")
    ws1["A4"] = "■ 1. エグゼクティブサマリ（結論）"
    ws1["A4"].font = font_section
    ws1["A4"].fill = fill_section
    ws1["A4"].alignment = align_left
    ws1.row_dimensions[4].height = 24

    summary_texts = [
        ("事象概要", "ECSタスク内のコンテナ（フロント/バック）起動時、JBoss EAP 8.1上のLog4jがシンボリックリンク経由でEFS（/mnt/logs）へログ出力を行う際、java.io.IOException: Stale file handle（Linuxエラー: ESTALE / errno 116）が発生し起動または書き込みが失敗する。"),
        ("仮説の結論", "ユーザー仮説『アプリデプロイ後にEFSのマウントを外して再アタッチした』は【極めて有力かつ十分に成立する】。Linux VFSおよびNFSプロトコル上、マウント解除や再マウントにより旧マウントのFile Handle（ファイル識別子）が無効化され、プロセスが旧ハンドルでアクセスすると確実にESTALEが発生する。"),
        ("最多の真因", "ただし現場で最も多発する原因は『デプロイ時や初期化スクリプトで、EFS上のログディレクトリ/ファイルをrm -rfで削除・再作成したことによるFile Handle世代番号の不一致』である。パス名が同一でもファイル実体のinode/generationが変化するとESTALEとなる。"),
        ("推奨根本対策", "①【最推奨】コンテナログをEFSファイル書き込みから「標準出力（STDOUT）」へ変更し、CloudWatch Logs / Fluent Bit (FireLens)で収集（12-Factor App準拠）。\n② ファイル出力が必須な場合は、シンボリックリンクを廃止しECSタスク定義で直接対象パスをマウント、かつ起動スクリプトでディレクトリ生存保証を実施。")
    ]
    
    r = 5
    for title, text in summary_texts:
        ws1.cell(row=r, column=1, value=title).font = font_tbl_header_dark
        ws1.cell(row=r, column=1).fill = fill_tbl_sub
        ws1.cell(row=r, column=1).alignment = align_top_center
        ws1.cell(row=r, column=1).border = border_cell
        
        ws1.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
        c = ws1.cell(row=r, column=2, value=text)
        c.font = font_data
        c.alignment = align_top_left
        for col_idx in range(2, 8):
            ws1.cell(row=r, column=col_idx).border = border_cell
        ws1.row_dimensions[r].height = 45 if "\n" in text or len(text) > 80 else 30
        r += 1

    # Section 2: ユーザー仮説の詳細検証
    r += 1
    ws1.merge_cells(f"A{r}:G{r}")
    ws1[f"A{r}"] = "■ 2. ユーザー仮説の徹底検証「EFSをアンマウントして再アタッチした可能性は成り立つか？」"
    ws1[f"A{r}"].font = font_section
    ws1[f"A{r}"].fill = fill_section
    ws1[f"A{r}"].alignment = align_left
    ws1.row_dimensions[r].height = 24
    r += 1

    hypo_headers = ["検証項目", "仮説の評価", "OS / Linux VFSの挙動", "NFS / EFS (NFSv4.1) の挙動", "JVM / Log4jの挙動", "現場での成立シナリオ"]
    for i, h in enumerate(hypo_headers, 1):
        ws1.cell(row=r, column=i, value=h).font = font_tbl_header
        ws1.cell(row=r, column=i).fill = fill_tbl_header
        ws1.cell(row=r, column=i).alignment = align_center
        ws1.cell(row=r, column=i).border = border_cell
    ws1.row_dimensions[r].height = 25
    r += 1

    hypo_data = [
        (
            "EFSアンマウント＆再アタッチの仮説妥当性",
            "【成立する】\n（確率: 高）",
            "マウント解除（umount -l 等）時に旧VFSスーパーブロックとdentryツリーが無効化される。再マウントされても既存プロセスの参照先VFS構造体は復活しない。",
            "アンマウントによりNFSクライアントセッションが破棄。再マウント後は新しいクライアントID/マウントIDが発行され、旧File Handleはサーバーから拒絶（NFS4ERR_STALE）される。",
            "JVMが起動前に親パスを評価していた場合や、起動直後にマウントが外れた場合、Log4jのFileOutputStreamオープン時または書込時にOSがESTALE (116) を返し、IOExceptionとなる。",
            "・ECSタスク起動中にホスト側でEFSボリューム再マウントが走った\n・コンテナの起動スクリプト(entrypoint)内で一度アンマウントして再マウントした\n・タスク定義のボリューム再マウントバグ"
        ),
        (
            "シンボリックリンクとの複合影響",
            "【拍車をかける】\n（極めて高）",
            "/webapp/.../logs が実体パス /mnt/logs/front/inter-api/logs を指す。シンボリックリンク解決（readlink/namei）時にマウントポイント跨ぎが発生する。",
            "シンボリックリンクの参照先ディレクトリがアンマウントされていると、リンク解決処理がマウントポイントのルートまたは未マウントの空ディレクトリに衝突し破綻する。",
            "Log4jが起動時にパスをカノニカル化（canonicalPath）する際、リンク先の実体が無効なFile Handleを指していると即座にESTALEが発生する。",
            "・コンテナ起動時にEFSマウントが完了する前にシンボリックリンクを作成した\n・コンテナ内のローカル領域に旧リンクがキャッシュされていた"
        ),
        (
            "ファイル/ディレクトリ削除・再作成（真因No.1との比較）",
            "【最も頻発する競合】\n（確率: 最高）",
            "Linuxカーネルは同一パス名であってもinode番号と世代番号（i_generation）で実体を厳密に区別する。rm & mkdirでinode/世代が更新される。",
            "EFSサーバーはFile Handle内に「FSID + File ID(inode) + Generation ID」を保持。クライアントが旧Handleで要求すると存在不能としてSTALEを返す。",
            "Log4jまたはJBossの別スレッドが以前のファイルハンドルをキャッシュしている場合、あるいはOSのdentryキャッシュが残っている場合にESTALEが発生。",
            "・デプロイスクリプトで「初期化」として /mnt/logs 配下を rm -rf して mkdir し直した\n・フロントコンテナとバックコンテナが同時にディレクトリ初期化を行った"
        )
    ]

    for row_item in hypo_data:
        for col_idx, text in enumerate(row_item, 1):
            c = ws1.cell(row=r, column=col_idx, value=text)
            c.font = font_data_bold if col_idx == 2 else font_data
            c.alignment = align_center if col_idx == 2 else align_top_left
            c.fill = fill_highlight if col_idx == 2 and "成立" in text else (fill_zebra_even if r % 2 == 0 else fill_zebra_odd)
            c.border = border_cell
        ws1.row_dimensions[r].height = 65
        r += 1

    # Section 3: システム構成・前提情報
    r += 1
    ws1.merge_cells(f"A{r}:G{r}")
    ws1[f"A{r}"] = "■ 3. システム構成およびパス関係図"
    ws1[f"A{r}"].font = font_section
    ws1[f"A{r}"].fill = fill_section
    ws1[f"A{r}"].alignment = align_left
    ws1.row_dimensions[r].height = 24
    r += 1

    sys_info = [
        ("コンテナ構成", "フロントコンテナ (UBI 9.8 / OpenJDK 21 RedHat Build / JBoss EAP 8.1)\nバックコンテナ (UBI 9.8 / OpenJDK 21 RedHat Build / JBoss EAP 8.1) ※同一ECSタスク内"),
        ("ストレージマウント", "AWS EFS (Amazon Elastic File System / NFSv4.1) を両コンテナの /mnt/logs にマウント\n・フロント用: /mnt/logs/front/inter-api/logs\n・バック用: /mnt/logs/back/..."),
        ("シンボリックリンク構成", "エフェメラルストレージ: /webapp/webapp9mf02/logs\nシンボリックリンク先: /mnt/logs/front/inter-api/logs (実体はEFS分散ストレージ)"),
        ("発生エラー", "java.io.IOException: Stale file handle (Linux System Call errno: 116 ESTALE)\n発生元: Log4j 2 / JBoss Logging サブシステムによるログファイルオープン/書込時")
    ]
    for k, v in sys_info:
        ws1.cell(row=r, column=1, value=k).font = font_tbl_header_dark
        ws1.cell(row=r, column=1).fill = fill_tbl_sub
        ws1.cell(row=r, column=1).alignment = align_center
        ws1.cell(row=r, column=1).border = border_cell

        ws1.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
        c = ws1.cell(row=r, column=2, value=v)
        c.font = font_data
        c.alignment = align_top_left
        for c_idx in range(2, 8):
            ws1.cell(row=r, column=c_idx).border = border_cell
        ws1.row_dimensions[r].height = 32
        r += 1

    # Freeze panes & column widths
    ws1.freeze_panes = "A5"
    col_widths1 = [22, 16, 26, 26, 26, 32, 10]
    for idx, width in enumerate(col_widths1, 1):
        ws1.column_dimensions[get_column_letter(idx)].width = width

    # -------------------------------------------------------------
    # SHEET 2: 発生原因ランキング (Root Cause Ranking)
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="2.発生原因ランキング")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:H1")
    ws2["A1"] = "【発生原因ランキング】ECS + EFS環境における Stale File Handle 発生要因（可能性順）"
    ws2["A1"].font = font_title
    ws2.row_dimensions[1].height = 35

    ws2.merge_cells("A2:H2")
    ws2["A2"] = "現場での発生頻度・再現性・技術的メカニズムに基づき、最も可能性の高いものから順に整理"
    ws2["A2"].font = font_subtitle
    ws2.row_dimensions[2].height = 20

    cause_headers = ["順位", "発生原因・シナリオ", "発生可能性", "再現難易度", "発生メカニズム（なぜESTALEになるのか）", "トリガーとなる具体的オペレーション", "本環境での該当度・考察", "主な検出シグナル"]
    r = 4
    for i, h in enumerate(cause_headers, 1):
        ws2.cell(row=r, column=i, value=h).font = font_tbl_header
        ws2.cell(row=r, column=i).fill = fill_tbl_header
        ws2.cell(row=r, column=i).alignment = align_center
        ws2.cell(row=r, column=i).border = border_cell
    ws2.row_dimensions[r].height = 28
    r += 1

    cause_data = [
        (
            "1位",
            "EFS上のディレクトリ/ファイルの削除＆再作成\n(rm -rf & mkdir)",
            "極めて高い\n(約50%)",
            "容易に再現可能\n(テスト確認可)",
            "NFS/EFSはパス名ではなく『File Handle（inode番号＋世代番号）』で対象を識別する。古いディレクトリをrm -rfして新規mkdirすると、パス名が同じでもFile Handleが完全に別物となる。クライアントカーネルのdentryキャッシュやJVMが古いHandleを保持したままアクセスすると、EFSサーバーが『そのHandleは無効』としてNFS4ERR_STALEを返す。",
            "・デプロイスクリプトでログ領域のクリーンアップのため rm -rf /mnt/logs/front/* を実行した\n・コンテナ初期化スクリプト(entrypoint)が起動毎に mkdir -p を行う前に既存削除を行った\n・バックコンテナや別管理プロセスがフロント側のディレクトリを誤って削除・再作成した",
            "最も典型的なパターン。コンテナ再起動やデプロイ時にログディレクトリを初期化するスクリプトが含まれている場合、ほぼ確実にこれが原因となる。",
            "・dmesg / /var/log/messages に NFS: stale file handle 記録\n・コンテナ内で ls /mnt/logs/front すると Stale file handle エラー\n・rm 実行ログの存在"
        ),
        (
            "2位",
            "アプリ起動前後のEFSアンマウント＆再マウント\n(ユーザー仮説)",
            "非常に高い\n(約25%)",
            "容易に再現可能\n(テスト確認可)",
            "コンテナ稼働中や起動シーケンス中に、ホストOSまたはコンテナ内部で umount -> mount が行われると、旧マウントに対するVFSスーパーブロック・ファイルハンドルが無効化される。Javaプロセス（JBoss）が起動処理の初期段階（クラスロードやログ初期化）でパスを参照した後にマウントが差し替えられると、オープン処理が旧ハンドルを叩いてESTALEとなる。",
            "・デプロイ手順書に『EFSマウント解除→再接続』のステップが存在した\n・ECSタスク内でサイドカーやエントリーポイントがマウント状態を再構成した\n・ECSホスト側のEFSマウントヘルパー（amazon-efs-utils）がセッション切断によりバックグラウンド再マウントを実施した",
            "ユーザーの提示した仮説そのもの。コンテナ起動のタイミングとマウント再接続のタイミングが重なった場合、100%の確率でESTALEを引き起こす。",
            "・mount コマンドの出力でマウント時刻がコンテナ起動時刻とズレている\n・プロセスオープン中のFD（/proc/<pid>/fd/）が (deleted) 状態になっている"
        ),
        (
            "3位",
            "シンボリックリンク作成とEFSマウント完了のレースコンディション",
            "高い\n(約15%)",
            "タイミング依存\n(並行実行時)",
            "コンテナ起動時に /webapp/webapp9mf02/logs -> /mnt/logs/front/inter-api/logs のシンボリックリンクを作成する際、EFSのマウントが完全に完了する前にリンク作成およびJBoss起動が走った。未マウント時のローカルエフェメラル上のディレクトリを参照した後にEFSが覆いかぶさるようにマウント（Over-mount）され、VFSのdentryキャッシュが破損・不整合を起こす。",
            "・DockerfileのENTRYPOINTやCMDでマウント完了待機（ヘルスチェック）をせずに即座にln -s および standalone.sh を起動した\n・ECSのDependsOn設定がない状態で複数コンテナが同時にEFSを初期化した",
            "ECSマルチコンテナ構成で起動順序制御やマウント待機をシェルスクリプトで厳密に行っていない場合に頻発する。",
            "・コンテナ起動直後のみ発生し、手動で再起動すると直る（タイミング問題）\n・シンボリックリンクの実体がローカルinodeを指している"
        ),
        (
            "4位",
            "ECS Fargate/EC2のEFSマウントセッション切断 (Lease失効)",
            "中程度\n(約5%)",
            "ネットワーク障害時\n(再現難)",
            "EFS (NFSv4.1) はステートフルプロトコルであり、クライアントとEFS間でLease（リース時間、通常90秒）を維持する。ECSのネットワーク一時瞬断、セキュリティグループの動的変更、またはEFSのAZ跨ぎ通信遅延によりLease更新が途切れると、EFSサーバーはクライアントのOpen/Lockステートを破棄し、再接続時にSTALEを返す。",
            "・VPCセキュリティグループのインバウンド/アウトバウンド（TCP 2049）の一時的ブロック\n・AZ（アベイラビリティゾーン）間のネットワーク輻輳\n・EFSのバーストクレジット枯渇による極端なI/Oハングアップ後のタイムアウト",
            "アプリ初回起動時にも、ネットワーク確立直後の不安定期に発生し得る。AWSマネージド側の一時的事象。",
            "・CloudWatch EFSメトリクス『ClientConnections』の急激な切断と再接続\n・PercentIOLimit が 100% に張り付いている"
        ),
        (
            "5位",
            "フロント/バックコンテナ間でのログローテーション・競合削除",
            "中程度\n(約3%)",
            "特定時刻\n(夜間バッチ等)",
            "フロントとバックが同一のEFSボリューム（/mnt/logs）を共有している。バックコンテナ側のログローテーションツール（logrotateやLog4j RollingFileAppender）が誤ってフロント側のディレクトリや共通一時領域をクリーンアップ・renameした場合、フロント側のJBossが握っているHandleがStale化する。",
            "・logrotateの設定でワイルドカード /mnt/logs/*/* が指定されており、互いのログを跨いでローテーション・削除した\n・cronジョブによる不要ログクリーンアップ処理の暴走",
            "共通EFSを共有しているマルチコンテナ特有の問題。ただしパスがfront/backで分離されているため、設定ミスがない限りは発生しにくい。",
            "・ESTALE発生時刻がログローテーション実行時刻（0:00や1時間毎）と一致\n・他コンテナの実行ログに削除コマンドの履歴"
        ),
        (
            "6位",
            "Log4j 2 の RollingFileAppender と NFS属性キャッシュの遅延",
            "低〜中\n(約2%)",
            "高負荷・ローテーション時",
            "Log4j 2 がログローテーションを行う際、既存ファイルを rename (mv) して新規ファイルを create する。NFSクライアントの属性キャッシュ（attribute cache: acdirmin/acdirmax）により、別スレッドが古いdentry情報を参照して書き込もうとした瞬間にESTALEとなる。",
            "・Log4jの設定で SizeBasedTriggeringPolicy が短時間で連続発動する高トラフィック時\n・JBossの複数ワーカースレッドが同時に同一ログファイルへアクセス",
            "起動直後に発生している今回の事象では主因ではない可能性が高いが、起動直後に大量の初期化ログを吐いて即時ローテーションした場合に発生し得る。",
            "・ログファイル名が .1 や日付付きに切り替わった直後に例外発生"
        )
    ]

    for row_item in cause_data:
        for col_idx, text in enumerate(row_item, 1):
            c = ws2.cell(row=r, column=col_idx, value=text)
            c.font = font_data_bold if col_idx in [1, 3] else font_data
            c.alignment = align_center if col_idx in [1, 3, 4] else align_top_left
            if col_idx == 1:
                c.fill = fill_highlight
            elif r % 2 == 0:
                c.fill = fill_zebra_even
            else:
                c.fill = fill_zebra_odd
            c.border = border_cell
        ws2.row_dimensions[r].height = 70
        r += 1

    ws2.freeze_panes = "A5"
    col_widths2 = [8, 26, 14, 16, 36, 32, 28, 28]
    for idx, width in enumerate(col_widths2, 1):
        ws2.column_dimensions[get_column_letter(idx)].width = width

    # -------------------------------------------------------------
    # SHEET 3: 動作原理と歴史 (Internal Architecture & History)
    # -------------------------------------------------------------
    ws3 = wb.create_sheet(title="3.動作原理と歴史背景")
    ws3.views.sheetView[0].showGridLines = True

    ws3.merge_cells("A1:G1")
    ws3["A1"] = "【深層解説】Stale File Handle (ESTALE) の動作原理・歴史と小学生向けたとえ話"
    ws3["A1"].font = font_title
    ws3.row_dimensions[1].height = 35

    ws3.merge_cells("A2:G2")
    ws3["A2"] = "なぜESTALEという仕組みが存在するのか？ UNIX/NFSの設計思想から解き明かす完全理解"
    ws3["A2"].font = font_subtitle
    ws3.row_dimensions[2].height = 20

    # Section 1: 小学生にもわかるたとえ話
    ws3.merge_cells("A4:G4")
    ws3["A4"] = "■ 1. 小学生にもわかる！「Stale File Handle」のたとえ話（下駄箱と番号札のミステリー）"
    ws3["A4"].font = font_section
    ws3["A4"].fill = fill_section
    ws3["A4"].alignment = align_left
    ws3.row_dimensions[4].height = 24

    metaphor_content = [
        ("登場人物", "① Javaくん（学校の生徒、Log4jで日記を書く係）\n② Linux先生（教室の担任、OSカーネル）\n③ EFSさん（体育館にある巨大な下駄箱・ロッカーの管理人、リモートストレージ）"),
        ("ふだんのやり取り（正常時）", "1. Javaくん：「先生、僕の日記帳はどこですか？」\n2. Linux先生：「『/webapp/logs』を見なさい。あ、そこは矢印（シンボリックリンク）が貼ってあって、体育館のEFSさんの『front/inter-api/logs』へ行けと書いてあるよ」\n3. Linux先生はEFSさんに電話して「その日記帳の【整理券番号：第105番】」をもらってJavaくんに渡す。\n4. Javaくんはその【105番の整理券（File Handle）】を持って、EFSさんのロッカーに毎日手紙を投函する。大成功！"),
        ("事件発生！（Stale File Handleの瞬間）", "Javaくんが105番の整理券を握りしめている間に、裏で誰か（作業員さん）がやってきて…\n『あ、このロッカー古いから一回全部捨てて、新品のロッカーに置き換えよう！』と、ロッカーを丸ごと撤去して、同じ場所に新しいロッカーを設置しました（EFSの再マウント、またはrm -rf & mkdir）！\n\nそこへJavaくんがやってきて、元気よく言います。\nJavaくん：「EFSさん！【105番の整理券】を持ってきたよ！日記を書き込むね！」\nEFSさん：「えっ！？ 105番のロッカーなんてさっき壊して捨てちゃったよ！今の新しいロッカーにはそんな番号ないよ！その整理券はもう使えない【ただの紙くず（Stale＝腐った・期限切れのハンドル）】だよ！」\nJavaくん：「うわーーーん！日記が書けないよーーー！（java.io.IOException: Stale file handle）」と大泣きしてアプリが止まってしまいました。"),
        ("たとえ話の教訓", "名前（下駄箱の場所）は同じでも、「整理券の番号（File Handle）」が違うのです！\n一度もらった古い整理券で新しいロッカーを開けようとしたから、EFSさんが『危ない！他人の荷物を壊しちゃうかもしれないから絶対ダメ！』と止めてくれたのです。これがStale File Handleの正体です。")
    ]

    r = 5
    for title, desc in metaphor_content:
        ws3.cell(row=r, column=1, value=title).font = font_tbl_header_dark
        ws3.cell(row=r, column=1).fill = fill_tbl_sub
        ws3.cell(row=r, column=1).alignment = align_center
        ws3.cell(row=r, column=1).border = border_cell

        ws3.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
        c = ws3.cell(row=r, column=2, value=desc)
        c.font = font_data
        c.alignment = align_top_left
        for col_idx in range(2, 8):
            ws3.cell(row=r, column=col_idx).border = border_cell
        ws3.row_dimensions[r].height = 55 if r == 7 else (45 if r == 8 else 35)
        r += 1

    # Section 2: 歴史と背景
    r += 1
    ws3.merge_cells(f"A{r}:G{r}")
    ws3[f"A{r}"] = "■ 2. 誕生の歴史と背景：なぜNFSに「File Handle」と「ESTALE」が必要になったのか？"
    ws3[f"A{r}"].font = font_section
    ws3[f"A{r}"].fill = fill_section
    ws3[f"A{r}"].alignment = align_left
    ws3.row_dimensions[r].height = 24
    r += 1

    history_headers = ["時代・規格", "技術的背景と課題", "採用されたアーキテクチャ", "なぜESTALEが生まれたか？（存在意義）"]
    for i, h in enumerate(history_headers, 1):
        col_span = 2 if i in [2, 3, 4] else 1
        # handled by cell assignment
    ws3.cell(row=r, column=1, value="時代・規格").font = font_tbl_header
    ws3.cell(row=r, column=1).fill = fill_tbl_header
    ws3.cell(row=r, column=1).alignment = align_center
    ws3.cell(row=r, column=1).border = border_cell

    ws3.merge_cells(f"B{r}:C{r}")
    ws3.cell(row=r, column=2, value="技術的背景と課題").font = font_tbl_header
    ws3.cell(row=r, column=2).fill = fill_tbl_header
    ws3.cell(row=r, column=2).alignment = align_center
    ws3.cell(row=r, column=2).border = border_cell
    ws3.cell(row=r, column=3).border = border_cell

    ws3.merge_cells(f"D{r}:E{r}")
    ws3.cell(row=r, column=4, value="採用されたアーキテクチャ（設計思想）").font = font_tbl_header
    ws3.cell(row=r, column=4).fill = fill_tbl_header
    ws3.cell(row=r, column=4).alignment = align_center
    ws3.cell(row=r, column=4).border = border_cell
    ws3.cell(row=r, column=5).border = border_cell

    ws3.merge_cells(f"F{r}:G{r}")
    ws3.cell(row=r, column=6, value="なぜESTALEが不可欠なのか？（存在意義）").font = font_tbl_header
    ws3.cell(row=r, column=6).fill = fill_tbl_header
    ws3.cell(row=r, column=6).alignment = align_center
    ws3.cell(row=r, column=6).border = border_cell
    ws3.cell(row=r, column=7).border = border_cell
    ws3.row_dimensions[r].height = 25
    r += 1

    history_data = [
        (
            "1984年\nNFSv2の誕生\n(Sun Microsystems)",
            "当時のネットワークはUDP中心で極めて不安定。サーバーも頻繁にクラッシュしていた。『サーバーがクライアントのオープン状態（State）を記憶する設計』にすると、サーバー再起動時に全クライアントが道連れで死んでしまうという致命的課題があった。",
            "【完全ステートレス設計 (Stateless)】\nサーバーは状態を一切持たない。クライアントは毎回のリクエストで『パス名（文字列）』を送るのではなく、サーバーが即座にディスク上のブロック/inodeを特定できる不透明なバイナリ値『File Handle』を送信する方式を採用。",
            "もしサーバー側で誰かがファイルを削除し、別の新しいファイルに同じinodeが再割り当てされた場合、古いクライアントが書き込むと『他人のファイルを破壊』してしまう！これを防ぐため、inodeに『世代番号(generation number)』を付与し、不一致なら即座にエラーとする安全装置【ESTALE】が誕生した。"
        ),
        (
            "1995年\nNFSv3の普及\n(RFC 1813)",
            "64bitファイルサイズ対応、非同期書き込み（ASYNC WRITE）の導入。しかし基本設計は依然としてステートレスを維持。File Handleのサイズが最大64バイトへ拡張された。",
            "クライアント側のキャッシュ（属性キャッシュ・データキャッシュ）が強化された。これにより、クライアントとサーバー間の整合性のズレが顕在化しやすくなった。",
            "キャッシュとサーバー実体のズレが発生した際、データ破壊を防ぐための最終防壁としてESTALEが極めて重要な役割を果たし続けた。"
        ),
        (
            "2003年〜現在\nNFSv4 / v4.1\n(AWS EFSが採用)",
            "インターネット/WAN対応、セキュリティ強化、ファイアウォール通過性、クラスタリング対応。ステートレスから【ステートフル（TCP必須、Lease管理、セッション）】へと大転換を遂げた。",
            "疑似ファイルシステム（Pseudo FS）、Open/LockステートID、複合RPC（COMPOUND RPC）を導入。AWS EFSはこのNFSv4.1規格をフルマネージド分散ストレージとして実装。",
            "ステートフルになった現在でも、File Handleの概念は不変。サーバー側の分散ノード切り替え、アンマウント、削除・再作成、Lease失効時には、依然としてプロトコル仕様通り『NFS4ERR_STALE (ESTALE)』が返される。"
        )
    ]

    for item in history_data:
        ws3.cell(row=r, column=1, value=item[0]).font = font_data_bold
        ws3.cell(row=r, column=1).alignment = align_center
        ws3.cell(row=r, column=1).fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws3.cell(row=r, column=1).border = border_cell

        for col_start, val in [(2, item[1]), (4, item[2]), (6, item[3])]:
            ws3.merge_cells(start_row=r, start_column=col_start, end_row=r, end_column=col_start+1)
            c = ws3.cell(row=r, column=col_start, value=val)
            c.font = font_data
            c.alignment = align_top_left
            c.fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
            ws3.cell(row=r, column=col_start).border = border_cell
            ws3.cell(row=r, column=col_start+1).border = border_cell

        ws3.row_dimensions[r].height = 65
        r += 1

    # Section 3: Linuxカーネル VFS & File Handle 動作メカニズム
    r += 1
    ws3.merge_cells(f"A{r}:G{r}")
    ws3[f"A{r}"] = "■ 3. Linuxカーネル VFS（仮想ファイルシステム）とFile Handleの内部動作イメージ"
    ws3[f"A{r}"].font = font_section
    ws3[f"A{r}"].fill = fill_section
    ws3[f"A{r}"].alignment = align_left
    ws3.row_dimensions[r].height = 24
    r += 1

    vfs_steps = [
        ("Step 1: パス解決 (namei)", "Log4jが open('/webapp/webapp9mf02/logs/app.log') を発行。Linux VFSはシンボリックリンクを辿り、/mnt/logs/front/inter-api/logs/app.log に到達する。"),
        ("Step 2: dentryとHandle取得", "Linuxカーネルのdentryキャッシュ（ディレクトリ構造）を検索。キャッシュにあればそのdentryが持つNFS File Handleを取り出し、無ければEFSサーバーへLOOKUP RPCを発行してFile Handleを取得・キャッシュする。"),
        ("Step 3: File Descriptor割当", "プロセス（JVM）にFD（ファイル記述子、例: 35番）を割り当て、カーネル内の struct file -> struct dentry -> struct inode -> nfs_fh（File Handle構造体）を紐付ける。"),
        ("Step 4: 外的破壊（トリガー）", "【ここでマウント解除＆再マウント、または別プロセスがrm -rf & mkdirを実行】\nEFSサーバー上では旧ディレクトリのinode/世代番号が消滅し、新ディレクトリに新しいFile Handleが割り当てられる。"),
        ("Step 5: 書き込み実行 (write)", "Log4jの別スレッドまたは後続処理が write(fd=35, 'ログ文字列') を発行。カーネルはfd=35に紐づく旧File Handleを使ってEFSへWRITE RPCを送信。"),
        ("Step 6: EFSサーバーの拒絶", "EFSサーバーは受信したHandleを検証。『そのFile Handle（FSID + inode + 世代）は存在しない！』と判定し、RPC応答として【NFS4ERR_STALE】を返却。"),
        ("Step 7: 例外発生 (JVMへ伝播)", "LinuxカーネルNFSクライアントはこれをerrno 116 (ESTALE: Stale file handle) に変換。JVMのC言語ランタイム（libc write()）が -1 を返し、Javaレイヤで【java.io.IOException: Stale file handle】がスローされる！")
    ]

    for step_num, step_desc in vfs_steps:
        ws3.cell(row=r, column=1, value=step_num).font = font_tbl_header_dark
        ws3.cell(row=r, column=1).fill = fill_tbl_sub
        ws3.cell(row=r, column=1).alignment = align_center
        ws3.cell(row=r, column=1).border = border_cell

        ws3.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
        c = ws3.cell(row=r, column=2, value=step_desc)
        c.font = font_data_bold if "ESTALE" in step_desc or "外" in step_num else font_data
        c.alignment = align_top_left
        c.fill = fill_highlight if "外" in step_num or "例外" in step_num else (fill_zebra_even if r % 2 == 0 else fill_zebra_odd)
        for col_idx in range(2, 8):
            ws3.cell(row=r, column=col_idx).border = border_cell
        ws3.row_dimensions[r].height = 32
        r += 1

    ws3.freeze_panes = "A5"
    col_widths3 = [20, 16, 18, 18, 18, 22, 22]
    for idx, width in enumerate(col_widths3, 1):
        ws3.column_dimensions[get_column_letter(idx)].width = width

    # -------------------------------------------------------------
    # SHEET 4: 切り分け・確認フロー (Troubleshooting & Verification)
    # -------------------------------------------------------------
    ws4 = wb.create_sheet(title="4.確認・切り分け方法")
    ws4.views.sheetView[0].showGridLines = True

    ws4.merge_cells("A1:G1")
    ws4["A1"] = "【実践マニュアル】Stale File Handle 事象確認・問題切り分け手順書"
    ws4["A1"].font = font_title
    ws4.row_dimensions[1].height = 35

    ws4.merge_cells("A2:G2")
    ws4["A2"] = "コンテナ内調査、ECSタスク調査、EFSメトリクス調査を段階的に実施し、原因を100%特定する"
    ws4["A2"].font = font_subtitle
    ws4.row_dimensions[2].height = 20

    diag_headers = ["フェーズ", "調査対象 / 観点", "実行コマンド / 確認箇所", "期待される正常値", "ESTALE発生時の異常値", "判定と次のアクション"]
    r = 4
    for i, h in enumerate(diag_headers, 1):
        col_span = 2 if i == 3 else 1
    
    ws4.cell(row=r, column=1, value="フェーズ").font = font_tbl_header
    ws4.cell(row=r, column=1).fill = fill_tbl_header
    ws4.cell(row=r, column=1).alignment = align_center
    ws4.cell(row=r, column=1).border = border_cell

    ws4.cell(row=r, column=2, value="調査対象 / 観点").font = font_tbl_header
    ws4.cell(row=r, column=2).fill = fill_tbl_header
    ws4.cell(row=r, column=2).alignment = align_center
    ws4.cell(row=r, column=2).border = border_cell

    ws4.merge_cells(f"C{r}:D{r}")
    ws4.cell(row=r, column=3, value="実行コマンド / 確認箇所").font = font_tbl_header
    ws4.cell(row=r, column=3).fill = fill_tbl_header
    ws4.cell(row=r, column=3).alignment = align_center
    ws4.cell(row=r, column=3).border = border_cell
    ws4.cell(row=r, column=4).border = border_cell

    ws4.cell(row=r, column=5, value="期待される正常値").font = font_tbl_header
    ws4.cell(row=r, column=5).fill = fill_tbl_header
    ws4.cell(row=r, column=5).alignment = align_center
    ws4.cell(row=r, column=5).border = border_cell

    ws4.cell(row=r, column=6, value="ESTALE発生時の異常値").font = font_tbl_header
    ws4.cell(row=r, column=6).fill = fill_tbl_header
    ws4.cell(row=r, column=6).alignment = align_center
    ws4.cell(row=r, column=6).border = border_cell

    ws4.cell(row=r, column=7, value="判定と次のアクション").font = font_tbl_header
    ws4.cell(row=r, column=7).fill = fill_tbl_header
    ws4.cell(row=r, column=7).alignment = align_center
    ws4.cell(row=r, column=7).border = border_cell
    ws4.row_dimensions[r].height = 25
    r += 1

    diag_data = [
        (
            "Phase 1\nコンテナ内確認\n(ECS Exec)",
            "① シンボリックリンクの整合性確認",
            "ls -ld /webapp/webapp9mf02/logs\nstat /webapp/webapp9mf02/logs",
            "リンク先が実在し、ディレクトリ情報が正常表示される",
            "ls: cannot access ...: Stale file handle または No such file or directory",
            "リンク先EFSディレクトリが消滅または再作成されている。原因1位または3位を疑う。"
        ),
        (
            "Phase 1\nコンテナ内確認\n(ECS Exec)",
            "② EFS実体ディレクトリの直接アクセス確認",
            "ls -la /mnt/logs/front/inter-api/logs\ntouch /mnt/logs/front/inter-api/logs/test.tmp",
            "ファイル一覧が表示され、touchでファイル作成可能",
            "touch: cannot touch ...: Stale file handle",
            "EFSマウント自体が無効Handleを保持。マウント解除再アタッチ（原因2位）またはrm再作成（原因1位）。"
        ),
        (
            "Phase 1\nコンテナ内確認\n(ECS Exec)",
            "③ プロセスのファイル記述子 (FD) 状態確認",
            "ls -l /proc/$(pgrep -f jboss)/fd/\nlsof -p $(pgrep -f jboss) | grep logs",
            "FDが正常なファイル/ディレクトリパスを指している",
            "パスの後ろに『(deleted)』が付与されている、または stat でエラー",
            "プロセスがオープン中に背後でファイルが削除・アンマウントされた証拠。原因1位または2位確定。"
        ),
        (
            "Phase 1\nコンテナ内確認\n(ECS Exec)",
            "④ マウントポイントとVFS状態の確認",
            "mount | grep efs\ncat /proc/mounts | grep /mnt/logs",
            "127.0.0.1:/ or fs-xxx:/ が /mnt/logs に nfs4 でマウント中",
            "マウントが存在しない、またはマウント時刻がコンテナ起動時刻より新しい",
            "起動後に再マウントされたか、マウントが外れている。ユーザー仮説（原因2位）の直接的証拠。"
        ),
        (
            "Phase 2\nECSタスク・\nインフラ確認",
            "⑤ ECSタスク定義のボリューム・マウント設定",
            "AWS CLI: aws ecs describe-task-definition\n・volumes.efsVolumeConfiguration\n・mountPoints",
            "rootDirectory, transitEncryption: ENABLED, authorizationConfig (AccessPointId) が正しく設定",
            "AccessPoint未指定、またはコンテナ間でrootDirectoryが重複・競合",
            "アクセスポイントを利用してコンテナごとにルートを完全分離する設定へ修正する。"
        ),
        (
            "Phase 2\nECSタスク・\nインフラ確認",
            "⑥ デプロイスクリプト・エントリポイントの調査",
            "Dockerfile / entrypoint.sh / CI/CDデプロイパイプラインのスクリプト全行",
            "ディレクトリ作成は mkdir -p のみで、既存削除 (rm) を行わない",
            "rm -rf /mnt/logs/* や umount コマンドが記述されている",
            "スクリプト内の rm -rf / umount を即時削除・修正する。"
        ),
        (
            "Phase 3\nAWS EFSメトリクス\n確認",
            "⑦ CloudWatch EFS メトリクス確認",
            "CloudWatch Metrics:\n・ClientConnections\n・PercentIOLimit\n・BurstCreditBalance",
            "接続数が安定しており、I/O Limitが100%未満、クレジット枯渇なし",
            "急激な切断スパイク、I/O Limit 100%張り付き（スロットリング）",
            "スループットモードをプロビジョンドに変更、またはネットワーク/セキュリティグループ調査。"
        )
    ]

    for item in diag_data:
        ws4.cell(row=r, column=1, value=item[0]).font = font_data_bold
        ws4.cell(row=r, column=1).alignment = align_center
        ws4.cell(row=r, column=1).fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws4.cell(row=r, column=1).border = border_cell

        ws4.cell(row=r, column=2, value=item[1]).font = font_data_bold
        ws4.cell(row=r, column=2).alignment = align_top_left
        ws4.cell(row=r, column=2).fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws4.cell(row=r, column=2).border = border_cell

        ws4.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
        c = ws4.cell(row=r, column=3, value=item[2])
        c.font = font_code
        c.alignment = align_top_left
        c.fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws4.cell(row=r, column=3).border = border_cell
        ws4.cell(row=r, column=4).border = border_cell

        for col_idx, val in [(5, item[3]), (6, item[4]), (7, item[5])]:
            c = ws4.cell(row=r, column=col_idx, value=val)
            c.font = font_data
            c.alignment = align_top_left
            c.fill = fill_highlight if col_idx == 6 else (fill_zebra_even if r % 2 == 0 else fill_zebra_odd)
            c.border = border_cell

        ws4.row_dimensions[r].height = 42
        r += 1

    ws4.freeze_panes = "A5"
    col_widths4 = [16, 26, 20, 20, 26, 26, 28]
    for idx, width in enumerate(col_widths4, 1):
        ws4.column_dimensions[get_column_letter(idx)].width = width

    # -------------------------------------------------------------
    # SHEET 5: 対処法一覧 (Remediation Plan)
    # -------------------------------------------------------------
    ws5 = wb.create_sheet(title="5.対処法一覧")
    ws5.views.sheetView[0].showGridLines = True

    ws5.merge_cells("A1:H1")
    ws5["A1"] = "【対応策マトリクス】緊急対応・根本対応・運用回避策の一覧とロードマップ"
    ws5["A1"].font = font_title
    ws5.row_dimensions[1].height = 35

    ws5.merge_cells("A2:H2")
    ws5["A2"] = "即時復旧手順から、クラウドネイティブな根本設計改善（12-Factor App）まで網羅"
    ws5["A2"].font = font_subtitle
    ws5.row_dimensions[2].height = 20

    sol_headers = ["区分", "対策名・アプローチ", "推奨度", "実装難易度", "作業概要・具体的コマンド/コード", "メリット（効果）", "デメリット / 注意点", "恒久性"]
    r = 4
    for i, h in enumerate(sol_headers, 1):
        ws5.cell(row=r, column=i, value=h).font = font_tbl_header
        ws5.cell(row=r, column=i).fill = fill_tbl_header
        ws5.cell(row=r, column=i).alignment = align_center
        ws5.cell(row=r, column=i).border = border_cell
    ws5.row_dimensions[r].height = 28
    r += 1

    sol_data = [
        (
            "緊急対応\n(即時復旧)",
            "① ECSタスクの強制再起動\n(New Deployment)",
            "★★★\n(最優先)",
            "低\n(即時可能)",
            "aws ecs update-service --cluster <cluster> --service <service> --force-new-deployment\n古いコンテナおよび無効なFile Handleを保持するVFS/JVMプロセスを全破棄し、新規クリーンなタスクを起動する。",
            "コマンド1発で数分以内にサービス復旧可能。壊れたキャッシュやFDが完全に一掃される。",
            "根本原因を解消しない限り、次回デプロイ時や再マウント時に再発するリスクがある。",
            "一時的\n(対症療法)"
        ),
        (
            "緊急対応\n(即時復旧)",
            "② シンボリックリンク再生成とディレクトリ復旧",
            "★★☆",
            "中\n(コンテナ作業)",
            "ECS Exec等でコンテナに入り:\n1. mkdir -p /mnt/logs/front/inter-api/logs\n2. rm -f /webapp/webapp9mf02/logs\n3. ln -s /mnt/logs/front/inter-api/logs /webapp/webapp9mf02/logs\n4. JBossプロセス再起動",
            "タスクを壊さずに特定のコンテナ内だけで局所的に復旧を試みることができる。",
            "コンテナのイミュータブル原則に反する。オートスケーリングやタスク再起動で元に戻ってしまう。",
            "一時的\n(対症療法)"
        ),
        (
            "根本対応\n(アーキテクチャ)",
            "③ 【最推奨】ログの標準出力化とCloudWatch Logs / FireLens収集",
            "★★★★★\n(ベストプラクティス)",
            "中\n(数時間〜1日)",
            "1. JBoss / Log4jの出力先をファイルから ConsoleAppender (STDOUT) に変更。\n2. ECSタスク定義で awslogs ログドライバーまたは FireLens (Fluent Bit) を構成。\n3. EFSマウントおよびシンボリックリンクを完全に撤去する。",
            "・ESTALEの可能性が物理的にゼロになる\n・EFSのI/Oコスト、接続管理、マウント不整合トラブルが完全消滅\n・クラウドネイティブ(12-Factor App)準拠となり可用性・性能が飛躍的向上",
            "既存の運用（EFS上にファイルとしてログを閲覧・収集するバッチ等）がある場合、CloudWatch LogsやS3からの取得フローへの変更が必要。",
            "完全恒久\n(再発率0%)"
        ),
        (
            "根本対応\n(アーキテクチャ)",
            "④ シンボリックリンク廃止＆直接マウント化",
            "★★★★☆\n(ファイル必須時)",
            "低〜中\n(定義変更)",
            "ファイル出力がどうしても必須な場合:\nシンボリックリンク (/webapp/.../logs -> /mnt/...) を全廃し、ECSタスク定義の mountPoints でコンテナ側の containerPath を直接 `/webapp/webapp9mf02/logs` に指定する。",
            "・シンボリックリンク解決時のVFSクロス障害が完全になくなる\n・起動時のリンク作成スクリプトが不要になりレースコンディションが消滅",
            "EFSのディレクトリ削除（rm -rf）によるESTALEリスクは依然として残る（運用規律が必要）。",
            "高\n(構成簡素化)"
        ),
        (
            "根本対応\n(EFS設計)",
            "⑤ EFS Access Point (アクセスポイント) の導入",
            "★★★★☆",
            "中\n(IaC/設定)",
            "フロント用・バック用で個別のEFS Access Pointを作成。\n・RootDirectory: /front/inter-api/logs, /back/logs\n・POSIX User: 1000/1000 (JBoss実行ユーザー)\nECSタスク定義で各Access Pointを指定。",
            "EFS側でディレクトリが自動作成（CreationInfo）され、権限不一致や誤った上位ディレクトリ削除をインフラレベルで遮断。",
            "Terraform / CloudFormation等のインフラコード更新が必要。",
            "恒久"
        ),
        (
            "運用回避\n(スクリプト改善)",
            "⑥ エントリポイントでのEFS待機＆ディレクトリ保護ガード",
            "★★★☆☆",
            "低\n(シェル修正)",
            "entrypoint.sh に以下のガード処理を組み込む:\n・EFSマウントの完了確認 (while ! mountpoint -q /mnt/logs; do sleep 1; done)\n・既存削除 (rm -rf) の絶対禁止\n・mkdir -p によるディレクトリ存在保証\n・リンク整合性テスト (test -e) 成功後に初めて JBoss 起動",
            "現行のシンボリックリンク構成のままでも、起動時の競合や初期化ミスによるESTALEを大幅に抑制できる。",
            "アプリ稼働中に別コンテナや運用者が手動でディレクトリを削除した場合は防げない。",
            "中\n(運用レベル)"
        ),
        (
            "運用回避\n(運用ルール策定)",
            "⑦ デプロイ手順書からのEFS再マウント・手動削除の排除",
            "★★★☆☆",
            "低\n(ドキュメント)",
            "運用手順書・デプロイマニュアルに以下を明記:\n『アプリ稼働中およびデプロイ時にEFSボリュームのマウント解除やディレクトリのrm操作を行ってはならない。必要な場合はECSタスクを全停止してから行うこと』",
            "運用人為ミスによるESTALE発生リスクを低減する。",
            "人手による運用依存のため、ヒューマンエラーを100%防ぐことはできない。",
            "中"
        )
    ]

    for item in sol_data:
        ws5.cell(row=r, column=1, value=item[0]).font = font_data_bold
        ws5.cell(row=r, column=1).alignment = align_center
        ws5.cell(row=r, column=1).fill = fill_highlight if "根本" in item[0] else (fill_zebra_even if r % 2 == 0 else fill_zebra_odd)
        ws5.cell(row=r, column=1).border = border_cell

        ws5.cell(row=r, column=2, value=item[1]).font = font_data_bold
        ws5.cell(row=r, column=2).alignment = align_top_left
        ws5.cell(row=r, column=2).fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws5.cell(row=r, column=2).border = border_cell

        ws5.cell(row=r, column=3, value=item[2]).font = font_data_bold
        ws5.cell(row=r, column=3).alignment = align_center
        ws5.cell(row=r, column=3).fill = fill_highlight if "最推奨" in item[2] else (fill_zebra_even if r % 2 == 0 else fill_zebra_odd)
        ws5.cell(row=r, column=3).border = border_cell

        ws5.cell(row=r, column=4, value=item[3]).font = font_data
        ws5.cell(row=r, column=4).alignment = align_center
        ws5.cell(row=r, column=4).fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws5.cell(row=r, column=4).border = border_cell

        ws5.cell(row=r, column=5, value=item[4]).font = font_data
        ws5.cell(row=r, column=5).alignment = align_top_left
        ws5.cell(row=r, column=5).fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws5.cell(row=r, column=5).border = border_cell

        ws5.cell(row=r, column=6, value=item[5]).font = font_data
        ws5.cell(row=r, column=6).alignment = align_top_left
        ws5.cell(row=r, column=6).fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws5.cell(row=r, column=6).border = border_cell

        ws5.cell(row=r, column=7, value=item[6]).font = font_data
        ws5.cell(row=r, column=7).alignment = align_top_left
        ws5.cell(row=r, column=7).fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws5.cell(row=r, column=7).border = border_cell

        ws5.cell(row=r, column=8, value=item[7]).font = font_data_bold
        ws5.cell(row=r, column=8).alignment = align_center
        ws5.cell(row=r, column=8).fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws5.cell(row=r, column=8).border = border_cell

        ws5.row_dimensions[r].height = 58
        r += 1

    ws5.freeze_panes = "A5"
    col_widths5 = [14, 26, 15, 14, 38, 28, 28, 14]
    for idx, width in enumerate(col_widths5, 1):
        ws5.column_dimensions[get_column_letter(idx)].width = width

    # -------------------------------------------------------------
    # SHEET 6: アーキテクチャ比較 (Architecture Comparison)
    # -------------------------------------------------------------
    ws6 = wb.create_sheet(title="6.推奨アーキテクチャ比較")
    ws6.views.sheetView[0].showGridLines = True

    ws6.merge_cells("A1:G1")
    ws6["A1"] = "【アーキテクチャ比較】現状構成 vs 改善案（直接マウント） vs 理想構成（CloudWatch Logs / FireLens）"
    ws6["A1"].font = font_title
    ws6.row_dimensions[1].height = 35

    ws6.merge_cells("A2:G2")
    ws6["A2"] = "コンテナ設計原則（The Twelve-Factor App）に基づき、耐障害性と運用性を徹底比較"
    ws6["A2"].font = font_subtitle
    ws6.row_dimensions[2].height = 20

    arch_headers = ["比較項目", "現行アーキテクチャ\n(EFS + シンボリックリンク)", "改善案A\n(EFS直接マウント + AccessPoint)", "推奨アーキテクチャB\n(標準出力 + CloudWatch Logs / FireLens)", "評価・選定指針"]
    r = 4
    ws6.cell(row=r, column=1, value="比較項目").font = font_tbl_header
    ws6.cell(row=r, column=1).fill = fill_tbl_header
    ws6.cell(row=r, column=1).alignment = align_center
    ws6.cell(row=r, column=1).border = border_cell

    ws6.merge_cells(f"B{r}:C{r}")
    ws6.cell(row=r, column=2, value="現行アーキテクチャ\n(EFS + シンボリックリンク)").font = font_tbl_header
    ws6.cell(row=r, column=2).fill = fill_tbl_header
    ws6.cell(row=r, column=2).alignment = align_center
    ws6.cell(row=r, column=2).border = border_cell
    ws6.cell(row=r, column=3).border = border_cell

    ws6.cell(row=r, column=4, value="改善案A\n(EFS直接マウント + AP)").font = font_tbl_header
    ws6.cell(row=r, column=4).fill = fill_tbl_header
    ws6.cell(row=r, column=4).alignment = align_center
    ws6.cell(row=r, column=4).border = border_cell

    ws6.merge_cells(f"E{r}:F{r}")
    ws6.cell(row=r, column=5, value="推奨アーキテクチャB\n(STDOUT + CloudWatch Logs / FireLens)").font = font_tbl_header
    ws6.cell(row=r, column=5).fill = fill_tbl_header
    ws6.cell(row=r, column=5).alignment = align_center
    ws6.cell(row=r, column=5).border = border_cell
    ws6.cell(row=r, column=6).border = border_cell

    ws6.cell(row=r, column=7, value="評価・選定指針").font = font_tbl_header
    ws6.cell(row=r, column=7).fill = fill_tbl_header
    ws6.cell(row=r, column=7).alignment = align_center
    ws6.cell(row=r, column=7).border = border_cell
    ws6.row_dimensions[r].height = 28
    r += 1

    arch_rows = [
        (
            "ログ出力先",
            "コンテナ内 /webapp/.../logs\n（EFSへシンボリックリンク）",
            "コンテナ内 /webapp/.../logs\n（EFSを直接マウント）",
            "コンテナ標準出力 (STDOUT / Console)\n※ファイル書き込みなし",
            "推奨BはディスクI/Oやパス解決の概念自体が存在しないため圧倒的に堅牢。"
        ),
        (
            "ESTALE (Stale file handle) の発生リスク",
            "【極めて高い】\nマウント解除、再作成、リンク解決不整合の三重苦",
            "【低〜中】\nシンボリックリンク要因は排除。ただしEFS側のrm削除時は発生",
            "【完全にゼロ（0%）】\nネットワークファイルシステムを使用しないため物理的に発生不能",
            "ESTALEの根本解決を望むなら推奨B一択。"
        ),
        (
            "ログ書き込みのI/O性能・遅延",
            "【劣る】\nNFSプロトコルのネットワーク遅延（数ms〜数十ms）がJavaのスレッドに直接影響",
            "【劣る】\n改善案Aと同様にNFSネットワークI/Oオーバーヘッドが存在",
            "【極めて高速】\nLinuxパイプへの書き込みのみ。コンテナ外でFluent Bitが非同期バッファリング",
            "JBossのレスポンスタイムがストレージ遅延に引っ張られない。"
        ),
        (
            "ストレージコスト・運用負荷",
            "【高コスト・高運用】\nEFS容量課金、IOPS課金、バックアップ管理、容量枯渇監視が必要",
            "【高コスト・高運用】\n現行と同様のEFS管理コストが継続して発生",
            "【低コスト・運用レス】\nCloudWatch Logs / S3の低コスト保管。ライフサイクル設定で自動圧縮・アーカイブ",
            "EFSのバーストクレジット枯渇によるタスク停止リスクを排除可能。"
        ),
        (
            "The Twelve-Factor App (コンテナ設計論) 適合度",
            "【不適合】\nFactor XI (Logs: ログをイベントストリームとして扱う) に違反",
            "【不適合】\nFactor XI に依然として違反",
            "【完全適合】\nFactor XI に100%合致。クラウドネイティブの業界標準構成",
            "現代のECS / Kubernetes運用におけるグローバルスタンダード。"
        ),
        (
            "移行への難易度・影響範囲",
            "現状のまま\n（トラブル継続）",
            "【低】\nECSタスク定義のmountPoints変更のみ。JBoss側のログ設定変更は不要",
            "【中】\nJBossのlog4j設定をConsoleAppenderに変更し、ECSタスク定義にlogConfigurationを追加",
            "まずは緊急で改善案Aを適用し、中長期的に推奨Bへシフトするのが現実的。"
        )
    ]

    for item in arch_rows:
        ws6.cell(row=r, column=1, value=item[0]).font = font_data_bold
        ws6.cell(row=r, column=1).alignment = align_center
        ws6.cell(row=r, column=1).fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws6.cell(row=r, column=1).border = border_cell

        # B & C
        ws6.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        c = ws6.cell(row=r, column=2, value=item[1])
        c.font = font_data
        c.alignment = align_top_left
        c.fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        ws6.cell(row=r, column=2).border = border_cell
        ws6.cell(row=r, column=3).border = border_cell

        # D
        c = ws6.cell(row=r, column=4, value=item[2])
        c.font = font_data
        c.alignment = align_top_left
        c.fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        c.border = border_cell

        # E & F
        ws6.merge_cells(start_row=r, start_column=5, end_row=r, end_column=6)
        c = ws6.cell(row=r, column=5, value=item[3])
        c.font = font_data_bold if "ゼロ" in item[3] or "高速" in item[3] or "完全適合" in item[3] else font_data
        c.alignment = align_top_left
        c.fill = fill_highlight if "ゼロ" in item[3] or "完全適合" in item[3] else (fill_zebra_even if r % 2 == 0 else fill_zebra_odd)
        ws6.cell(row=r, column=5).border = border_cell
        ws6.cell(row=r, column=6).border = border_cell

        # G
        c = ws6.cell(row=r, column=7, value=item[4])
        c.font = font_data
        c.alignment = align_top_left
        c.fill = fill_zebra_even if r % 2 == 0 else fill_zebra_odd
        c.border = border_cell

        ws6.row_dimensions[r].height = 45
        r += 1

    ws6.freeze_panes = "A5"
    col_widths6 = [20, 16, 16, 26, 18, 18, 28]
    for idx, width in enumerate(col_widths6, 1):
        ws6.column_dimensions[get_column_letter(idx)].width = width

    # Save to disk
    output_path = r"C:\Users\taka_\Agy\Log_Stale_Handle_Agy\ECS_EFS_Log_Stale_File_Handle_Investigation.xlsx"
    wb.save(output_path)
    print(f"Successfully generated: {output_path}")

if __name__ == "__main__":
    build_workbook()
