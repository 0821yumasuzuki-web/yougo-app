import streamlit as st
import pandas as pd
import os
import random

# 教科ごとの設定と初期データ定義
SUBJECT_CONFIG = {
    "地理": {
        "file": "geography_data.xlsx",
        "icon": "🌍",
        "init_data": [
            {"id": 1, "term": "リアス海岸", "hints": "V字谷が沈水してできたギザギザとした鋸歯状の海岸線。三陸海岸や志摩半島で見られ、静かな湾内では牡蠣や真珠の養殖が盛ん。", "category": "自然地理", "check": False},
            {"id": 2, "term": "カルスト地形", "hints": "石灰岩が二酸化炭素を含む雨水や地下水によって溶食されて形成された地形。山口県の秋吉台などが有名で、ドリーネや鍾乳洞が見られる。", "category": "自然地理", "check": False},
            {"id": 3, "term": "フィヨルド", "hints": "氷河によって削られたU字谷が沈水して形成された、奥深く切り立った湾。ノルウェー沿岸やニュージーランド南島などに代表される。", "category": "自然地理", "check": False},
            {"id": 4, "term": "プランテーション", "hints": "熱帯や亜熱帯地域の旧植民地を中心に、欧米の大資本と現地労働者を利用して単一産品（モノカルチャー）を大規模に栽培する農場形態。", "category": "人文地理", "check": False}
        ]
    },
    "英語": {
        "file": "english_data.xlsx",
        "icon": "🔤",
        "init_data": [
            {"id": 1, "term": "abandon", "hints": "〜を捨てる、〜をあきらめる、見捨てる", "category": "単語", "check": False},
            {"id": 2, "term": "take advantage of", "hints": "〜を利用する、〜に乗ずる", "category": "熟語", "check": False}
        ]
    },
    "情報": {
        "file": "info_data.xlsx",
        "icon": "💻",
        "init_data": [
            {"id": 1, "term": "アルゴリズム", "hints": "問題を解決するための手順や計算方法のこと。", "category": "プログラミング", "check": False},
            {"id": 2, "term": "フィッシング詐欺", "hints": "実在する金融機関などを装った偽Webサイトに誘導し、個人情報を盗み取る行為。", "category": "情報セキュリティ", "check": False}
        ]
    },
    "化学": {
        "file": "chemistry_data.xlsx",
        "icon": "🧪",
        "init_data": [
            {"id": 1, "term": "炎色反応", "hints": "金属元素の塩類を炎の中に入れると、元素特有の色を示す現象。リアカー無きK村などの語呂合わせで覚える。", "category": "無機化学", "check": False},
            {"id": 2, "term": "ボイル・シャルルの法則", "hints": "気体の圧力、体積、絶対温度の間の関係を表した法則。PV/T = 一定。", "category": "理論化学", "check": False}
        ]
    }
}

# 1. データ読み込み関数（教科ごと）
def load_subject_data(subject_name):
    config = SUBJECT_CONFIG[subject_name]
    excel_file = config["file"]
    
    if not os.path.exists(excel_file):
        df_init = pd.DataFrame(config["init_data"])
        df_init.to_excel(excel_file, index=False)
        return df_init
    else:
        df = pd.read_excel(excel_file)
        if "check" in df.columns:
            df["check"] = df["check"].astype(bool)
        return df

# 2. データ保存関数（教科ごと）
def save_subject_data(df, subject_name):
    excel_file = SUBJECT_CONFIG[subject_name]["file"]
    df.to_excel(excel_file, index=False)

# アプリの基本設定
st.set_page_config(page_title="用語学習アプリ", page_icon="📚", layout="wide")

# セッション状態の初期化
if "current_subject" not in st.session_state:
    st.session_state.current_subject = None
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if "quiz_order" not in st.session_state:
    st.session_state.quiz_order = []

# サイドバー設定
st.sidebar.markdown("### ⚙️ メニュー")
if st.sidebar.button("🏠 ホーム（教科選択）", use_container_width=True):
    st.session_state.current_subject = None
    st.rerun()

# ---------------------------------------------------------
# 1. ホーム画面（教科未選択時）
# ---------------------------------------------------------
if st.session_state.current_subject is None:
    st.markdown("<h2 style='text-align: center;'>📚 学習教科を選択してください</h2>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2 = st.columns(2)
    subjects = list(SUBJECT_CONFIG.keys())
    
    with col1:
        for subj in subjects[:2]:
            icon = SUBJECT_CONFIG[subj]["icon"]
            if st.button(f"{icon} {subj}", key=f"btn_{subj}", use_container_width=True, type="primary"):
                st.session_state.current_subject = subj
                st.session_state.current_index = 0
                st.session_state.show_answer = False
                st.session_state.quiz_order = []
                st.rerun()
            st.write("")
            
    with col2:
        for subj in subjects[2:]:
            icon = SUBJECT_CONFIG[subj]["icon"]
            if st.button(f"{icon} {subj}", key=f"btn_{subj}", use_container_width=True, type="primary"):
                st.session_state.current_subject = subj
                st.session_state.current_index = 0
                st.session_state.show_answer = False
                st.session_state.quiz_order = []
                st.rerun()
            st.write("")

# ---------------------------------------------------------
# 2. 各教科のメイン画面
# ---------------------------------------------------------
else:
    current_subj = st.session_state.current_subject
    subj_icon = SUBJECT_CONFIG[current_subj]["icon"]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"現在選択中: **{subj_icon} {current_subj}**")
    
    menu = st.sidebar.radio(
        "機能選択",
        ["🧠 クイズ学習", "⭐ チェック済みクイズ", "➕ 用語追加", "📋 一覧表示"]
    )
    
    df = load_subject_data(current_subj)

    # ---------------------------------------------------------
    # モード 1: クイズ学習 & モード 2: チェック済みクイズ
    # ---------------------------------------------------------
    if menu in ["🧠 クイズ学習", "⭐ チェック済みクイズ"]:
        is_check_only = (menu == "⭐ チェック済みクイズ")
        base_df = df[df["check"] == True].copy() if is_check_only else df.copy()

        # ヘッダー（タイトルは控えめなサイズに）
        st.markdown(f"##### {subj_icon} {current_subj} - {'復習' if is_check_only else '全用語'}クイズ")

        # カテゴリーフィルター（シンプルな常時表示の丸マーク付き選択）
        all_categories = sorted([cat for cat in df["category"].dropna().unique() if str(cat).strip() != ""])
        
        # アイコン丸のリスト
        color_dots = ["🟢", "🔵", "🟡", "🔴", "🟣", "🟠"]
        cat_options = ["すべて"] + [
            f"{color_dots[i % len(color_dots)]} {cat}" 
            for i, cat in enumerate(all_categories)
        ]
        
        selected_option = st.radio(
            "カテゴリー選択",
            options=cat_options,
            horizontal=True,
            label_visibility="collapsed"
        )

        # 選択カテゴリーの抽出
        if selected_option == "すべて":
            target_df = base_df.reset_index(drop=True)
        else:
            selected_cat_name = selected_option.split(" ", 1)[1]
            target_df = base_df[base_df["category"] == selected_cat_name].reset_index(drop=True)

        if target_df.empty:
            st.info("該当する用語がありません。")
        else:
            # 問題順序とインデックスの維持
            if len(st.session_state.quiz_order) != len(target_df):
                st.session_state.quiz_order = list(range(len(target_df)))

            if st.session_state.current_index >= len(target_df):
                st.session_state.current_index = 0

            # シャッフルボタン
            col_shuf, _ = st.columns([1, 2])
            with col_shuf:
                if st.button("🔀 シャッフル", use_container_width=True):
                    indices = list(range(len(target_df)))
                    random.shuffle(indices)
                    st.session_state.quiz_order = indices
                    st.session_state.current_index = 0
                    st.session_state.show_answer = False
                    st.rerun()

            current_pos = st.session_state.quiz_order[st.session_state.current_index]
            row = target_df.iloc[current_pos]

            st.write("")

            # クイズ表示エリア（シンプル化：ヒント文の見出し・進捗表示を廃止）
            with st.container():
                st.info(row["hints"])  # 文章のみを直接表示

                st.write("")

                # 答え表示 / 非表示トグル
                if st.session_state.show_answer:
                    st.success(f"### {row['term']}")
                    if st.button("🙈 答えを隠す"):
                        st.session_state.show_answer = False
                        st.rerun()
                else:
                    if st.button("👁️ 答えを確認", type="primary"):
                        st.session_state.show_answer = True
                        st.rerun()

                st.write("")

                # チェックボックス（説明テキストなしの星マークのみ）
                original_idx = df[df["id"] == row["id"]].index[0]
                current_check = bool(df.loc[original_idx, "check"])
                
                new_check = st.checkbox("⭐", value=current_check, key=f"chk_{current_subj}_{row['id']}")
                if new_check != current_check:
                    df.loc[original_idx, "check"] = new_check
                    save_subject_data(df, current_subj)
                    st.toast("更新しました")
                    st.rerun()

                # 移動ボタン
                col_prev, col_next = st.columns(2)
                with col_prev:
                    if st.button("⬅️ 前へ", use_container_width=True):
                        if st.session_state.current_index > 0:
                            st.session_state.current_index -= 1
                        else:
                            st.session_state.current_index = len(target_df) - 1
                        st.session_state.show_answer = False
                        st.rerun()

                with col_next:
                    if st.button("次へ ➡️", use_container_width=True):
                        if st.session_state.current_index < len(target_df) - 1:
                            st.session_state.current_index += 1
                        else:
                            st.session_state.current_index = 0
                        st.session_state.show_answer = False
                        st.rerun()

    # ---------------------------------------------------------
    # モード 3: 新規追加
    # ---------------------------------------------------------
    elif menu == "➕ 用語追加":
        st.markdown(f"##### {subj_icon} {current_subj} - 新しい用語の登録")

        with st.form("add_term_form", clear_on_submit=True):
            new_term = st.text_input("用語 (答え)")
            new_hints = st.text_area("文章 (説明・解説)")
            new_category = st.text_input("カテゴリー", placeholder="例: 自然地理")
            
            submitted = st.form_submit_button("登録する")
            if submitted:
                if not new_term or not new_hints:
                    st.warning("「用語」と「文章」を入力してください。")
                else:
                    new_id = int(df["id"].max() + 1) if not df.empty else 1
                    new_row = pd.DataFrame([{
                        "id": new_id,
                        "term": new_term,
                        "hints": new_hints,
                        "category": new_category if new_category else "全般",
                        "check": False
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_subject_data(df, current_subj)
                    st.success(f"「{new_term}」を登録しました！")

    # ---------------------------------------------------------
    # モード 4: 用語一覧表示（シンプル＆全体折り返し表示）
    # ---------------------------------------------------------
    elif menu == "📋 一覧表示":
        st.markdown(f"##### {subj_icon} {current_subj} - 用語一覧")

        search_keyword = st.text_input("🔍 検索", placeholder="キーワードを入力...")
        
        display_df = df.copy()
        if search_keyword:
            display_df = display_df[
                display_df["term"].astype(str).str.contains(search_keyword, case=False, na=False) |
                display_df["hints"].astype(str).str.contains(search_keyword, case=False, na=False)
            ]

        # 用語と文章のみ表示し、文章は横スクロール不要な折り返し構造で配置
        st.dataframe(
            display_df[["term", "hints"]],
            column_config={
                "term": st.column_config.TextColumn("用語", width="medium"),
                "hints": st.column_config.TextColumn("説明・文章", width="large"),
            },
            use_container_width=True,
            hide_index=True
        )
