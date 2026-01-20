import streamlit as st
import time
import os
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語小教室", 
    page_icon="🐸", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 極致美化 (Salongan 主題) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFBF5; }
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        background: -webkit-linear-gradient(45deg, #FF6B6B, #FF8E53);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        text-align: center;
        padding-bottom: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        font-size: 18px;
        font-weight: 700;
        background: linear-gradient(135deg, #FFD700 0%, #FDB931 100%);
        color: #4A4A4A;
        border: none;
        padding: 15px 0px;
        box-shadow: 0px 5px 15px rgba(253, 185, 49, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0px 8px 20px rgba(253, 185, 49, 0.6);
    }
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #F0F0F0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        border-color: #FF6B6B;
    }
    .big-font {
        font-size: 32px !important;
        font-weight: 800;
        color: #FF6B6B;
        margin: 10px 0;
        letter-spacing: 1px;
    }
    .med-font {
        font-size: 18px !important;
        color: #888;
        font-weight: 500;
        margin-bottom: 15px;
    }
    .emoji-icon {
        font-size: 55px;
        margin-bottom: 5px;
        filter: drop-shadow(0 3px 5px rgba(0,0,0,0.1));
    }
    .instructor-box {
        text-align: center;
        color: #999;
        font-size: 14px;
        background: rgba(255,255,255,0.6);
        padding: 8px 20px;
        border-radius: 20px;
        display: inline-block;
        margin: 0 auto 25px auto;
        border: 1px solid #eee;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #fff;
        border-radius: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF6B6B !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 數據結構 ---
# 檔名設定：去除特殊符號 ' 以避免錯誤
VOCABULARY = {
    "Tata'ang": {"zh": "很大", "emoji": "🐘", "action": "張開雙臂畫大圓", "file": "Tataang"},
    "Mata":     {"zh": "眼睛", "emoji": "👀", "action": "指指眼睛", "file": "Mata"},
    "Takola'":  {"zh": "青蛙", "emoji": "🐸", "action": "學青蛙跳", "file": "Takola"}
}

SENTENCES = [
    {"amis": "Tata'ang ko mata no takola'.", "zh": "青蛙的眼睛很大。", "file": "sentence_tataang"}
]

# --- 1.5 智慧語音核心 ---
def play_audio(text, filename_base=None):
    if filename_base:
        path_m4a = f"audio/{filename_base}.m4a"
        if os.path.exists(path_m4a):
            st.audio(path_m4a, format='audio/mp4')
            return
        path_mp3 = f"audio/{filename_base}.mp3"
        if os.path.exists(path_mp3):
            st.audio(path_mp3, format='audio/mp3')
            return
        # 找不到檔案時顯示提示
        st.error(f"⚠️ 找不到音檔：audio/{filename_base}.m4a")

    try:
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3')
    except:
        st.caption("🔇")

# --- 2. 狀態管理 ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0

# --- 3. 介面邏輯 ---

def show_learning_mode():
    # 標題已更新：移除 Unit 2
    st.markdown("""
        <div style='text-align: center; margin-bottom: 25px;'>
            <h2 style='color: #2A9D8F; font-size: 28px; margin: 0;'>Tata'ang a Mata</h2>
            <div style='color: #A0A0A0; font-size: 18px; font-weight: 400; letter-spacing: 2px; margin-top: 5px;'>
                — 很大的眼睛 —
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("💡 點擊播放按鈕，跟著老師一起唸！")
    
    col1, col2 = st.columns(2)
    words = list(VOCABULARY.items())
    
    for idx, (amis, data) in enumerate(words):
        with (col1 if idx % 2 == 0 else col2):
            st.markdown(f"""
            <div class="card">
                <div class="emoji-icon">{data['emoji']}</div>
                <div class="big-font">{amis}</div>
                <div class="med-font">{data['zh']}</div>
                <div style="color: #2A9D8F; font-size: 13px; font-weight:bold; background: #E0F2F1; padding: 4px 10px; border-radius: 10px; display:inline-block;">
                    {data['action']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            play_audio(amis, filename_base=data.get('file'))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🗣️ 句型練習")
    
    s1 = SENTENCES[0]
    
    st.markdown(f"""
    <div class="card" style="background: linear-gradient(135deg, #FFF9C4 0%, #FFFDE7 100%); border: 2px solid #FFF59D;">
        <div style="font-size: 22px; font-weight:900; color:#FBC02D; margin-bottom: 8px; text-shadow: 1px 1px 0px #fff;">
            {s1['amis']}
        </div>
        <div style="color:#7F8C8D; font-size: 18px;">{s1['zh']}</div>
    </div>
    """, unsafe_allow_html=True)
    play_audio(s1['amis'], filename_base=s1.get('file')) 

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #FF6B6B; margin-bottom: 20px;'>🏆 小勇士挑戰</h3>", unsafe_allow_html=True)
    
    st.progress(st.session_state.current_q / 3)
    st.write("") 

    if st.session_state.current_q == 0:
        st.markdown("**第 1 關：聽聽看，這是什麼動物？**")
        target_word = "Takola'"
        play_audio(target_word, filename_base="Takola")
        
        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🐘 很大"): st.error("那是 Tata'ang 喔！")
        with c2:
            if st.button("🐸 青蛙"):
                st.balloons()
                st.success("答對了！Takola' 就是青蛙！")
                time.sleep(1.0)
                st.session_state.score += 100
                st.session_state.current_q += 1
                st.rerun()
        with c3:
            if st.button("👀 眼睛"): st.error("那是 Mata 喔！")

    elif st.session_state.current_q == 1:
        st.markdown("**第 2 關：句子接龍**")
        st.markdown("請完成句子：")
        st.markdown("""
        <div style="background:#fff; padding:15px; border-radius:10px; border-left: 5px solid #FF6B6B; margin: 10px 0;">
            <span style="font-size:20px;">Tata'ang ko <b>_______</b> no takola'.</span>
            <br><span style="color:#999; font-size:14px;">(青蛙的眼睛很大)</span>
        </div>
        """, unsafe_allow_html=True)
        
        play_audio("Tata'ang ko mata no takola'", filename_base="sentence_tataang")
        
        options = ["Mata (眼睛)", "Fodoy (衣服)", "Salongan (漂亮)"]
        choice = st.radio("請選擇正確的單字：", options)
        
        st.write("")
        if st.button("✅ 確定送出"):
            if "Mata" in choice:
                st.success("太棒了！青蛙的眼睛很大！")
                time.sleep(1.5)
                st.session_state.score += 100
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.error("再試一次！提示：我們在說眼睛喔")

    elif st.session_state.current_q == 2:
        st.markdown("**第 3 關：我是翻譯官**")
        st.markdown("當你看到一個 **超級大的西瓜** 🍉")
        st.markdown("你要說：")
        
        if st.button("Salongan! (漂亮)"): st.info("西瓜可能很漂亮，但我們想說它很大...")
        if st.button("Tata'ang! (很大)"):
            st.snow()
            st.success("沒錯！Tata'ang 就是很大！")
            time.sleep(1.5)
            st.session_state.score += 100
            st.session_state.current_q += 1
            st.rerun()
        if st.button("Miso! (你的)"): st.error("不對喔！")

    else:
        st.markdown(f"""
        <div class="card" style="background: linear-gradient(180deg, #FFFFFF 0%, #FFF3E0 100%); border: 2px solid #FFD700;">
            <h1 style="margin-bottom:0;">🎉 挑戰完成！</h1>
            <h2 style="color: #E67E22; margin-top:0;">得分：{st.session_state.score}</h2>
            <hr style="border-top: 1px dashed #FFD700;">
            <p style="font-size: 20px; color: #555;">Tata'ang ko mata no takola'! 🐸</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 再玩一次"):
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.rerun()

# --- 4. 主程式入口 ---
st.title("阿美語小教室 🌞")

# 講師資訊已更新
st.markdown("""
    <div style="text-align: center;">
        <span class="instructor-box">
            講師：高春美 &nbsp;|&nbsp; 教材提供者：高春美
        </span>
    </div>
    """, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📖 學習單詞", "🎮 練習挑戰"])

with tab1:
    show_learning_mode()

with tab2:
    show_quiz_mode()
