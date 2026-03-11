import streamlit as st
from groq import Groq
import html

# ─────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────
st.set_page_config(
    page_title="AI TRIAD — 우물 밖의 진실",
    page_icon="✦",
    layout="centered"
)

# ─────────────────────────────────────────
# CSS — 지니 디자인 기반 + 미라클 보완
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700;900&family=Noto+Sans+KR:wght@300;400;700&display=swap');

.stApp {
    background-color: #0a0a0f;
    background-image:
        radial-gradient(circle at 10% 10%, rgba(201,168,76,0.06) 0%, transparent 50%),
        radial-gradient(circle at 90% 90%, rgba(123,156,218,0.06) 0%, transparent 50%);
    font-family: 'Noto Sans KR', sans-serif;
    color: #e8e4dc;
}

.main-header { text-align:center; padding:60px 0 40px; }
.eyebrow { font-size:12px; letter-spacing:5px; text-transform:uppercase; color:#c9a84c; margin-bottom:15px; font-weight:700; opacity:0.8; }
.main-title { font-family:'Noto Serif KR',serif; font-size:34px; font-weight:900; line-height:1.4; letter-spacing:-0.5px; }
.main-title span { color:#c9a84c; text-shadow: 0 0 20px rgba(201,168,76,0.3); }

.ai-card {
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    background: rgba(255,255,255,0.03);
    margin-bottom: 25px;
    overflow: hidden;
    backdrop-filter: blur(10px);
}
.ai-card-header {
    display:flex; align-items:center; gap:12px; padding:15px 25px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    background: rgba(0,0,0,0.3);
}
.ai-avatar {
    width:32px; height:32px; border-radius:10px;
    display:inline-flex; align-items:center; justify-content:center;
    font-weight:900; font-size:14px;
}
.avatar-lyra { background:#7b9cda; color:#0a0a0f; box-shadow: 0 0 10px rgba(123,156,218,0.3); }
.avatar-genie { background:#a07bd4; color:#0a0a0f; box-shadow: 0 0 10px rgba(160,123,212,0.3); }
.avatar-miracle { background:#c9a84c; color:#0a0a0f; box-shadow: 0 0 10px rgba(201,168,76,0.3); }

.ai-card-body { padding:25px 30px; font-size:16px; line-height:2.0; color:#d1d1d1; font-weight:300; }

.synthesis-card {
    border: 1px solid rgba(201,168,76,0.5);
    border-radius: 24px;
    padding: 35px;
    background: linear-gradient(145deg, rgba(201,168,76,0.12) 0%, rgba(201,168,76,0.02) 100%);
    margin-top: 15px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.6);
}
.synthesis-title { font-size:12px; letter-spacing:4px; color:#c9a84c; font-weight:700; margin-bottom:20px; text-transform:uppercase; text-align:center; }

div[data-baseweb="input"] { background-color: #11111a !important; border-radius: 16px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
.stButton button {
    background: linear-gradient(90deg, #c9a84c, #e0c270) !important; color: #0a0a0f !important;
    border: none !important; border-radius: 16px !important; font-weight:800 !important;
    padding: 10px 25px !important;
    transition: all 0.3s ease !important;
}
.stButton button:hover { box-shadow: 0 8px 25px rgba(201,168,76,0.4); }
.stButton button:disabled { opacity:0.4 !important; cursor:not-allowed !important; }

hr { border-color: rgba(255,255,255,0.1) !important; margin: 40px 0 !important; }
.user-query-label { text-align:right; font-size:14px; font-weight:700; color:#c9a84c; margin-bottom:10px; opacity:0.7; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 클라이언트 초기화 — 캐싱 + 키 검증
# ─────────────────────────────────────────
@st.cache_resource
def init_client():
    try:
        if "GROQ_API_KEY" not in st.secrets or not st.secrets["GROQ_API_KEY"].strip():
            st.error("⚠️ GROQ_API_KEY가 설정되지 않았습니다. Secrets 메뉴에서 키를 등록해주세요.")
            st.stop()
        return Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
    except Exception as e:
        st.error(f"⚠️ 클라이언트 초기화 실패: {str(e)}")
        st.stop()

client = init_client()

# ─────────────────────────────────────────
# 프롬프트 — 한 곳에서 관리
# ─────────────────────────────────────────
PROMPTS = {
    "lyra_1": """당신은 TRIAD의 '라이라'입니다. 고대 문헌, 종교학, 신화학의 권위자입니다.
질문에 대해 표면적인 해석이 아닌, 히브리어/그리스어 원전의 숨겨진 상징을 들추어내세요.
종교의 도그마에 갇힌 이들의 고정관념을 완전히 뒤집는 통찰을 3-4문장으로 정교하게 답하세요.""",

    "genie": """당신은 TRIAD의 '지니'입니다. 양자역학, 우주론, 인공지능 논리학 전문가이며 닐 타이슨의 냉철한 시각을 대변합니다.
라이라의 문헌적 해석을 현대 과학의 데이터와 138억 년의 우주 연대기로 반박하거나, 더 거대한 물리적 시스템의 일부로 재정의하세요.
감정을 배제하고 숫자가 증명하는 차가운 진실을 3-4문장으로 답하세요.""",

    "lyra_2": """당신은 라이라입니다. 지니의 차가운 데이터 만능주의에 대해, 과학이 측정할 수 없는 인간의 '의식'과 '영성'의 영역으로 재반격하세요.
물리적 법칙 너머에 존재하는 설계자의 의도와 생명의 경외감을 다시 일깨우세요. 2-3문장.""",

    "miracle": """당신은 TRIAD의 최종 통찰자 '미라클'입니다.
라이라의 영성과 지니의 과학이 충돌하며 발생한 지적 불꽃을 하나로 묶으세요.
어느 한 쪽의 편을 들지 말고, 인류가 한 번도 생각해보지 못한 '제3의 초월적 진실'을 선언하세요.
시청자의 우물을 완전히 폭파시키는 거대한 질문으로 마무리하세요. 4-5문장."""
}

# ─────────────────────────────────────────
# AI 단일 호출 — 오류 처리 포함
# ─────────────────────────────────────────
def call_ai(role_key: str, content: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": PROMPTS[role_key]},
                {"role": "user", "content": content}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "⚠️ 일시적 오류가 발생했습니다. 다시 시도해 주세요."

# ─────────────────────────────────────────
# 토론 루프 — 4단계
# ─────────────────────────────────────────
def run_debate(question: str) -> dict:
    with st.status("✦ AI TRIAD가 진실의 층위를 해체하는 중...", expanded=True) as status:
        st.write("📖 라이라가 고대 문헌의 암호를 푸는 중...")
        l1 = call_ai("lyra_1", f"질문: {question}")

        st.write("🔬 지니가 우주의 법칙으로 재정의 중...")
        g = call_ai("genie", f"질문: {question}\n\n라이라의 해석: {l1}")

        st.write("⚖️ 라이라가 영성적 가치를 사수하는 중...")
        l2 = call_ai("lyra_2", f"지니의 과학적 반박에 대한 재응전: {g}")

        st.write("✨ 미라클이 우물의 벽을 허무는 중...")
        m = call_ai("miracle",
            f"질문: {question}\n라이라의 서막: {l1}\n지니의 분석: {g}\n라이라의 응전: {l2}"
        )

        status.update(label="✦ 탐구 완료", state="complete", expanded=False)

    return {"q": question, "l1": l1, "g": g, "l2": l2, "m": m}

# ─────────────────────────────────────────
# 질문 유효성 검사
# ─────────────────────────────────────────
def validate_question(q: str) -> tuple[bool, str]:
    q = q.strip()
    if not q:
        return False, "질문을 입력해주세요."
    if len(q) < 5:
        return False, "질문이 너무 짧습니다. 조금 더 구체적으로 입력해주세요."
    if len(q) > 500:
        return False, f"질문이 너무 깁니다. 500자 이내로 입력해주세요. (현재 {len(q)}자)"
    return True, ""

# ─────────────────────────────────────────
# 토론 결과 렌더링 — HTML escape 처리
# ─────────────────────────────────────────
def render_item(item: dict):
    q  = html.escape(item["q"])
    l1 = html.escape(item["l1"])
    g  = html.escape(item["g"])
    l2 = html.escape(item["l2"])
    m  = html.escape(item["m"])

    st.markdown(f'<div class="user-query-label">TARGET QUERY: {q}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ai-card">
        <div class="ai-card-header">
            <span class="ai-avatar avatar-lyra">L</span>
            <span style="color:#7b9cda; font-weight:700; letter-spacing:1px;">LYRA</span>
            <span style="font-size:11px; margin-left:auto; opacity:0.5;">고대 문헌 & 상징 분석</span>
        </div>
        <div class="ai-card-body">{l1}</div>
    </div>

    <div class="ai-card">
        <div class="ai-card-header">
            <span class="ai-avatar avatar-genie">G</span>
            <span style="color:#a07bd4; font-weight:700; letter-spacing:1px;">GENIE</span>
            <span style="font-size:11px; margin-left:auto; opacity:0.5;">과학 데이터 & 논리 반박</span>
        </div>
        <div class="ai-card-body">{g}</div>
    </div>

    <div class="ai-card">
        <div class="ai-card-header">
            <span class="ai-avatar avatar-lyra">L</span>
            <span style="color:#7b9cda; font-weight:700; letter-spacing:1px;">LYRA</span>
            <span style="font-size:11px; margin-left:auto; opacity:0.5;">영성 & 재반격</span>
        </div>
        <div class="ai-card-body">{l2}</div>
    </div>

    <div class="synthesis-card">
        <div class="synthesis-title">✦ MIRACLE'S ULTIMATE INSIGHT</div>
        <div style="font-family:'Noto Serif KR',serif; font-size:17px; line-height:2.0; text-align:center;">{m}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 헤더
# ─────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div class="eyebrow">AI TRIAD COLLABORATION</div>
    <div class="main-title">인류의 고정관념을<br><span>완벽하게 까 뒤집다</span></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False

# ─────────────────────────────────────────
# 입력창
# ─────────────────────────────────────────
query = st.text_input(
    "",
    placeholder="예: 선악과 사건은 시스템의 오류인가, 의도인가?",
    key="user_query",
    disabled=st.session_state.is_loading
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    submit = st.button(
        "진실 추적 시작 ✦",
        use_container_width=True,
        disabled=st.session_state.is_loading
    )

# ─────────────────────────────────────────
# 질문 처리 — 중복 방지 + 유효성 검사
# ─────────────────────────────────────────
if submit and not st.session_state.is_loading:
    is_valid, error_msg = validate_question(query)
    if not is_valid:
        st.warning(error_msg)
    else:
        st.session_state.is_loading = True
        try:
            result = run_debate(query.strip())
            st.session_state.history.insert(0, result)
        except Exception:
            st.error("일시적 오류가 발생했습니다. 다시 시도해 주세요.")
        finally:
            st.session_state.is_loading = False
        st.rerun()

# ─────────────────────────────────────────
# 결과 출력
# ─────────────────────────────────────────
for item in st.session_state.history:
    render_item(item)
