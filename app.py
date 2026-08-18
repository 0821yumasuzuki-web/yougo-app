import streamlit as st
import pandas as pd
import os
import random

# Excelファイルのパス定義
EXCEL_FILE = 'geography_data.xlsx'

# 1. Excelファイルの読み込み・初期化関数
def load_data():
    if not os.path.exists(EXCEL_FILE):
        # ファイルが存在しない場合は初期サンプルデータで作成
        df_init = pd.DataFrame([
            {
                "id": 1, 
                "term": "リアス海岸", 
                "hints": "V字谷が沈水してできたギザギザとした鋸歯状の海岸線。三陸海岸や志摩半島で見られ、静かな湾内では牡蠣や真珠の養殖が盛ん。", 
                "category": "自然地理", 
                "check": False
            },
            {
                "id": 2, 
                "term": "カルスト地形", 
                "hints": "石灰岩が二酸化炭素を含む雨水や地下水によって溶食されて形成された地形。山口県の秋吉台などが有名で、ドリーネや鍾乳洞が見られる。", 
                "category": "自然地理", 
                "check": False
            },
            {
                "id": 3, 
                "term": "フィヨルド", 
                "hints": "氷河によって削られたU字谷が沈水して形成された、奥深く切り立った湾。ノルウェー沿岸やニュージーランド南島などに代表される。", 
                "category": "自然地理", 
                "check": False
            },
            {
                "id": 4, 
                "term": "プランテーション", 
                "hints": "熱帯や亜熱帯地域の旧植民地を中心に、欧米の大資本と現地労働者を利用して単一産品（モノカルチャー）を大規模に栽培する農場形態。", 
                "category": "人文地理", 
                "check": False
            },
            {
                "id": 5, 
                "term": "インフラマトリックス", 
                "hints": "産業基盤や都市機能などの社会資本（インフラストラクチャー）の配置や組み合わせ・整備状態を示す概念。", 
                "category": "人文地理", 
                "check": False
            }
        ])
        df_init.to_excel(EXCEL_FILE, index=False)
        return df_init
    else:
        df = pd.read_excel(EXCEL_FILE)
        if "check" in df.columns:
            df["check"] = df["check"].astype(bool)
        return df

# 2. Excelファイルへの保存関数
def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

# アプリ設定
st.set_page_config(page_title="地理用語学習アプリ", page_icon="🌍", layout="wide")

st.title("🌍 地理用語学習アプリ")

# データの読み込み
df = load_data()

# ---------------------------------------------------------
# サイドバー設定（メニュー切り替えのみ）
# ---------------------------------------------------------
st.sidebar.header("⚙️ メニュー")
menu = st.sidebar.radio(
    "移動先の画面を選択", 
    ["🧠 クイズ学習", "⭐ チェック済みクイズ", "➕ 新しい用語の登録", "📋 用語一覧表示"]
)

# ---------------------------------------------------------
# セッション状態の初期化（クイズ用）
# ---------------------------------------------------------
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if "quiz_order" not in st.session_state:
    st.session_state.quiz_order = []

# ---------------------------------------------------------
# モード 1: クイズ学習 & モード 2: チェック済みクイズ
# ---------------------------------------------------------
if menu in ["🧠 クイズ学習", "⭐ チェック済みクイズ"]:
    is_check_only = (menu == "⭐ チェック済みクイズ")
    
    if is_check_only:
        st.subheader("⭐ チェックを入れた要復習用語のクイズ")
        base_df = df[df["check"] == True].copy()
    else:
        st.subheader("🧠 全用語クイズ")
        base_df = df.copy()

    # 1. カテゴリーフィルターの配置（クイズ学習画面上に配置）
    with st.expander("🏷️ カテゴリーフィルター設定", expanded=True):
        all_categories = sorted([cat for cat in df["category"].dropna().unique() if str(cat).strip() != ""])
        
        if "selected_categories" not in st.session_state:
            st.session_state.selected_categories = all_categories.copy()

        col_cat1, col_cat2 = st.columns([1, 4])
        with col_cat1:
            if st.button("全選択", key="btn_all_select", use_container_width=True):
                st.session_state.selected_categories = all_categories.copy()
                st.rerun()
            if st.button("全解除", key="btn_all_clear", use_container_width=True):
                st.session_state.selected_categories = []
                st.rerun()
        
        with col_cat2:
            selected_cats = st.multiselect(
                "表示するカテゴリーを選択",
                options=all_categories,
                default=st.session_state.selected_categories,
                key="cat_multiselect"
            )

    # カテゴリーによる絞り込み
    target_df = base_df[base_df["category"].isin(selected_cats)].reset_index(drop=True)

    if not selected_cats:
        st.warning("⚠️ カテゴリーフィルターで1つ以上選択してください。")
    elif target_df.empty:
        st.info("該当する用語がありません。カテゴリー選択を見直すか、チェック・追加を行ってください。")
    else:
        # シャッフル・制御
        col_s1, _ = st.columns([2, 3])
        with col_s1:
            if st.button("🔀 問題順をシャッフル"):
                indices = list(range(len(target_df)))
                random.shuffle(indices)
                st.session_state.quiz_order = indices
                st.session_state.current_index = 0
                st.session_state.show_answer = False
                st.rerun()

        # 問題順の初期化・安全チェック
        if len(st.session_state.quiz_order) != len(target_df):
            st.session_state.quiz_order = list(range(len(target_df)))

        if st.session_state.current_index >= len(target_df):
            st.session_state.current_index = 0

        current_pos = st.session_state.quiz_order[st.session_state.current_index]
        row = target_df.iloc[current_pos]

        st.progress((st.session_state.current_index + 1) / len(target_df))
        st.caption(f"進捗: {st.session_state.current_index + 1} / {len(target_df)} 問目")

        # カード表示（ヒント文）
        with st.container():
            st.markdown("### 💡 ヒント文")
            st.info(row["hints"])
            
            st.caption(f"📌 カテゴリー: {row.get('category', '未分類')}")

            st.markdown("---")

            # 答え表示 / 隠すトグル切り替えボタン
            if st.session_state.show_answer:
                st.success(f"### 🎯 答え: {row['term']}")
                if st.button("🙈 答えを隠す", type="secondary"):
                    st.session_state.show_answer = False
                    st.rerun()
            else:
                if st.button("👁️ 答えを確認する", type="primary"):
                    st.session_state.show_answer = True
                    st.rerun()

            st.markdown("---")

            # チェックボックス（復習フラグ更新）
            original_idx = df[df["id"] == row["id"]].index[0]
            current_check = bool(df.loc[original_idx, "check"])
            
            new_check = st.checkbox("⭐ チェックを入れて復習リストに登録する", value=current_check, key=f"chk_{row['id']}")
            if new_check != current_check:
                df.loc[original_idx, "check"] = new_check
                save_data(df)
                st.toast("保存状態を更新しました！")
                st.rerun()

            # 前へ・次へボタン
            col_prev, col_next = st.columns(2)
            with col_prev:
                if st.button("⬅️ 前の問題へ"):
                    if st.session_state.current_index > 0:
                        st.session_state.current_index -= 1
                    else:
                        st.session_state.current_index = len(target_df) - 1
                    st.session_state.show_answer = False
                    st.rerun()

            with col_next:
                if st.button("次へ進む ➡️"):
                    if st.session_state.current_index < len(target_df) - 1:
                        st.session_state.current_index += 1
                    else:
                        st.session_state.current_index = 0
                    st.session_state.show_answer = False
                    st.rerun()

# ---------------------------------------------------------
# モード 3: 新しい用語の登録（新規追加のみ）
# ---------------------------------------------------------
elif menu == "➕ 新しい用語の登録":
    st.subheader("➕ 新しい用語の登録")
    st.caption("※削除や変更は元のExcelファイルを直接編集してください。")

    with st.form("add_term_form", clear_on_submit=True):
        new_term = st.text_input("用語 (答え)", placeholder="例: フィヨルド")
        new_hints = st.text_area("ヒント文 (解説)", placeholder="例: 氷河によって削られたU字谷が沈水して形成された、奥深く切り立った湾。")
        new_category = st.text_input("カテゴリー", placeholder="例: 自然地理")
        
        submitted = st.form_submit_button("登録する")
        if submitted:
            if not new_term or not new_hints:
                st.warning("「用語」と「ヒント文」は必須入力項目です。")
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
                save_data(df)
                st.success(f"「{new_term}」を登録しました！")

# ---------------------------------------------------------
# モード 4: 用語一覧表示（閲覧専用）
# ---------------------------------------------------------
elif menu == "📋 用語一覧表示":
    st.subheader("📋 用語一覧（閲覧専用）")
    st.caption("※アプリ上での誤操作を防ぐため、編集不可に設定しています。修正・削除は元のExcelファイルを編集してください。")

    # 検索機能
    search_keyword = st.text_input("🔍 用語・ヒント文で検索", placeholder="キーワードを入力...")
    
    display_df = df.copy()
    if search_keyword:
        display_df = display_df[
            display_df["term"].astype(str).str.contains(search_keyword, case=False, na=False) |
            display_df["hints"].astype(str).str.contains(search_keyword, case=False, na=False) |
            display_df["category"].astype(str).str.contains(search_keyword, case=False, na=False)
        ]

    # データ表示（st.dataframeで編集不可形式にする）
    st.dataframe(
        display_df,
        column_config={
            "id": st.column_config.NumberColumn("ID"),
            "term": st.column_config.TextColumn("用語 (答え)"),
            "hints": st.column_config.TextColumn("ヒント文"),
            "category": st.column_config.TextColumn("カテゴリー"),
            "check": st.column_config.CheckboxColumn("チェック(要復習)"),
        },
        use_container_width=True,
        hide_index=True
    )
