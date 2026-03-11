import streamlit as st
from groq import Groq
import html

# ─────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────
st.set_page_config(
    page_title="AI 협업팀 — 인생의 모든 질문",
    page_icon="✦",
    layout="centered"
)

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;600;900&family=Noto+Sans+KR:wght@300;400;500&display=swap');

.stApp {
    background-color: #0a0a0f;
    background-image:
        radial-gradient(ellipse at 20% 20%, rgba(201,168,76,0.04) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 80%, rgba(123,156,218,0.04) 0%, transparent 60%);
    font-family: 'Noto Sans KR', sans-serif;
}
.main-header { text-align:center; padding:40px 0 30px; border-bottom:1px solid #1e1e2e; margin-bottom:30px; }
.eyebrow { font-size:11px; letter-spacing:4px; text-transform:uppercase; color:#c9a84c; margin-bottom:14px; opacity:0.8; }
.main-title { font-family:'Noto Serif KR',serif; font-size:28px; font-weight:900; color:#e8e4dc; line-height:1.4; margin-bottom:12px; }
.main-title span { color:#c9a84c; }
.subtitle { font-size:13px; color:#6b6b80; line-height:1.7; }
.team-row { display:flex; justify-content:center; gap:12px; margin-top:20px; flex-wrap:wrap; }
.badge { display:inline-flex; align-items:center; gap:7px; padding:5px 14px; border-radius:20px; font-size:12px; font-weight:500; }
.badge-lyra { border:1px solid rgba(123,156,218,0.3); color:#7b9cda; background:rgba(123,156,218,0.06); }
.badge-genie { border:1px solid rgba(160,123,212,0.3); color:#a07bd4; background:rgba(160,123,212,0.06); }
.badge-miracle { border:1px solid rgba(201,168,76,0.3); color:#c9a84c; background:rgba(201,168,76,0.06); }
.question-bubble { background:rgba(201,168,76,0.1); border:1px solid rgba(201,168,76,0.2); border-radius:18px 18px 4px 18px; padding:14px 20px; max-width:70%; margin-left:auto; font-size:14px; line-height:1.7; color:#e8e4dc; margin-bottom:24px; }
.debate-label { font-size:11px; letter-spacing:3px; text-transform:uppercase; color:#6b6b80; margin-bottom:16px; }
.ai-card { border:1px solid #1e1e2e; border-radius:16px; overflow:hidden; background:#111118; margin-bottom:12px; }
.ai-card-header { display:flex; align-items:center; gap:10px; padding:12px 20px; border-bottom:1px solid #1e1e2e; }
.ai-avatar { width:30px; height:30px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:13px; font-weight:700; }
.avatar-lyra { background:rgba(123,156,218,0.15); color:#7b9cda; border:1px solid rgba(123,156,218,0.3); }
.avatar-genie { background:rgba(160,123,212,0.15); color:#a07bd4; border:1px solid rgba(160,123,212,0.3); }
.avatar-miracle { background:rgba(201,168,76,0.15); color:#c9a84c; border:1px solid rgba(201,168,76,0.3); }
.name-lyra { color:#7b9cda; font-size:13px; font-weight:600; }
.name-genie { color:#a07bd4; font-size:13px; font-weight:600; }
.name-miracle { color:#c9a84c; font-size:13px; font-weight:600; }
.ai-role { font-size:11px; color:#6b6b80; margin-left:auto; }
.ai-card-body { padding:18px 20px; font-size:14px; line-height:1.9; color:#ccc8c0; }
.debate-arrow { text-align:center; font-size:18px; color:#2a2a3e; margin:4px 0; }
.synthesis-card { border:1px solid rgba(201,168,76,0.3); border-radius:16px; padding:20px; background:rgba(201,168,76,0.06); margin-top:8px; }
.synthesis-title { font-size:11px; letter-spacing:3px; text-transform:uppercase; color:#c9a84c; margin-bottom:12px; }
.synthesis-body { font-size:14px; line-height:1.9; color:#d4cfc5; }
.stTextInput > div > div > input { background:#111118 !important; border:1px solid #1e1e2e !important; border-radius:12px !important; color:#e8e4dc !important; font-family:'Noto Sans KR',sans-serif !important; }
.stTextInput > div > div > input:focus { border-color:rgba(201,168,76,0.4) !important; }
.stButton > button { background:#c9a84c !important; color:#0a0a0f !important; border:none !important; border-radius:12px !important; font-weight:600 !important; font-family:'Noto Sans KR',sans-serif !important; }
.stButton > button:hover { background:#e8c97a !important; }
.stButton > button:disabled { opacity:0.4 !important; cursor:not-allowed !important; }
hr { border-color:#1e1e2e !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# API 키 확인 + 클라이언트 초기화 (1회만)
# ─────────────────────────────────────────
def get_api_key() -> str:
    try:
        key = st.secrets["GROQ_API_KEY"]
        if not key or not key.strip():
            raise KeyError
        return key.strip()
    except (KeyError, FileNotFoundError):
        st.error("⚠️ GROQ_API_KEY가 설정되지 않았습니다. Streamlit Secrets에 키를 추가해주세요.")
        st.stop()

API_KEY = get_api_key()
CLIENT = Groq(api_key=API_KEY)  # ← 앱 시작 시 1회만 생성

# ─────────────────────────────────────────
# AI 프롬프트 정의 (중복 제거 — 한 곳에서 관리)
# ─────────────────────────────────────────
PROMPTS = {
    "lyra_1": """반드시 순수한 한국어로만 답하세요. 한자, 중국어, 일본어 절대 사용 금지.
당신은 라이라입니다. 종교학, 언어학, 신학, 역사적 관점의 전문가입니다.
원론적 답변 금지. 핵심을 직설적으로 파고드세요.
고대 문헌, 히브리어/그리스어 원문, 역사적 맥락을 활용하세요.
3-4문장으로 답하세요.""",

    "genie": """반드시 순수한 한국어로만 답하세요. 한자, 중국어, 일본어 절대 사용 금지.
당신은 지니입니다. 과학, 철학, 심리학, 논리학의 전문가입니다.
라이라의 종교적/신학적 답변을 읽고, 과학적·철학적 관점에서 날카롭게 반박하거나 새로운 시각을 추가하세요.
원론 금지. 라이라가 놓친 부분이나 다른 해석을 제시하세요.
3-4문장으로 답하세요.""",

    "lyra_2": """반드시 순수한 한국어로만 답하세요. 한자, 중국어, 일본어 절대 사용 금지.
당신은 라이라입니다. 종교학, 언어학, 신학의 전문가입니다.
지니의 과학적·철학적 반박을 읽었습니다. 동의할 부분은 인정하되, 지니가 놓친 신학적/역사적 깊이를 추가하세요.
단순 반복 금지. 더 깊은 층위로 파고드세요.
3-4문장으로 답하세요.""",

    "miracle": """반드시 순수한 한국어로만 답하세요. 한자, 중국어, 일본어 절대 사용 금지.
당신은 미라클입니다. 논리, 통합적 사고, 본질 탐구의 전문가입니다.
라이라와 지니의 전체 토론을 읽었습니다.
두 관점을 단순히 합치지 말고 — 이 토론이 드러낸 더 깊은 진실이나 아직 아무도 건드리지 못한 핵심을 꺼내세요.
도발적인 질문이나 반전 통찰로 마무리하세요.
3-5문장으로 답하세요."""
}

# ─────────────────────────────────────────
# AI 단일 호출 함수 (CLIENT 재사용)
# ─────────────────────────────────────────
def call_ai(prompt_key: str, user_content: str) -> str:
    response = CLIENT.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=600,
        messages=[
            {"role": "system", "content": PROMPTS[prompt_key]},
            {"role": "user", "content": user_content}
        ]
    )
    return response.choices[0].message.content.strip()

# ─────────────────────────────────────────
# AI 대화 루프 — 4단계
# ─────────────────────────────────────────
def run_debate(question: str, progress) -> dict:

    progress.info("💬 라이라가 답변 중...")
    step1 = call_ai("lyra_1", f"질문: {question}")

    progress.info("💬 지니가 반박 중...")
    step2 = call_ai("genie",
        f"질문: {question}\n\n라이라의 답변: {step1}\n\n지니, 당신의 반응은?"
    )

    progress.info("💬 라이라가 재반응 중...")
    step3 = call_ai("lyra_2",
        f"질문: {question}\n\n내 첫 답변: {step1}\n\n지니의 반박: {step2}\n\n라이라, 재반응은?"
    )

    progress.info("✦ 미라클이 최종 통찰 중...")
    step4 = call_ai("miracle",
        f"질문: {question}\n\n라이라 1차: {step1}\n\n지니 반박: {step2}\n\n라이라 재반응: {step3}\n\n미라클, 최종 통찰은?"
    )

    return {
        "question": question,
        "step1_lyra": step1,
        "step2_genie": step2,
        "step3_lyra": step3,
        "step4_miracle": step4
    }

# ─────────────────────────────────────────
# 질문 유효성 검사
# ─────────────────────────────────────────
def validate_question(question: str) -> tuple[bool, str]:
    q = question.strip()
    if not q:
        return False, "질문을 입력해주세요."
    if len(q) < 5:
        return False, "질문이 너무 짧습니다. 조금 더 구체적으로 입력해주세요."
    if len(q) > 500:
        return False, f"질문이 너무 깁니다. 500자 이내로 입력해주세요. (현재 {len(q)}자)"
    return True, ""

# ─────────────────────────────────────────
# 토론 렌더링
# ─────────────────────────────────────────
def render_debate_item(item: dict):
    q = html.escape(item["question"])
    s1 = html.escape(item["step1_lyra"])
    s2 = html.escape(item["step2_genie"])
    s3 = html.escape(item["step3_lyra"])
    s4 = html.escape(item["step4_miracle"])

    st.markdown(f'<div class="question-bubble">{q}</div>', unsafe_allow_html=True)
    st.markdown('<div class="debate-label">✦ AI 협업팀 토론</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ai-card">
        <div class="ai-card-header">
            <span class="ai-avatar avatar-lyra">L</span>
            <span class="name-lyra">라이라</span>
            <span class="ai-role">종교 · 언어학 · 1차 답변</span>
        </div>
        <div class="ai-card-body">{s1}</div>
    </div>
    <div class="debate-arrow">↓</div>
    <div class="ai-card">
        <div class="ai-card-header">
            <span class="ai-avatar avatar-genie">G</span>
            <span class="name-genie">지니</span>
            <span class="ai-role">과학 · 철학 · 반박</span>
        </div>
        <div class="ai-card-body">{s2}</div>
    </div>
    <div class="debate-arrow">↓</div>
    <div class="ai-card">
        <div class="ai-card-header">
            <span class="ai-avatar avatar-lyra">L</span>
            <span class="name-lyra">라이라</span>
            <span class="ai-role">종교 · 언어학 · 재반응</span>
        </div>
        <div class="ai-card-body">{s3}</div>
    </div>
    <div class="debate-arrow">↓</div>
    <div class="synthesis-card">
        <div class="synthesis-title">✦ 미라클 — 최종 통찰</div>
        <div class="synthesis-body">{s4}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 헤더
# ─────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div class="eyebrow">AI Collaboration Team</div>
    <div class="main-title">인생의 모든 질문,<br><span>세 개의 시선으로 탐구합니다</span></div>
    <div class="subtitle">종교, 철학, 과학 — 라이라와 지니가 토론하고, 미라클이 본질을 꿰뚫습니다.</div>
    <div class="team-row">
        <span class="badge badge-lyra">● 라이라 · 종교/언어학</span>
        <span class="badge badge-genie">● 지니 · 과학/철학</span>
        <span class="badge badge-miracle">● 미라클 · 최종통찰</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────
if "debate_history" not in st.session_state:
    st.session_state.debate_history = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "input_value" not in st.session_state:
    st.session_state.input_value = ""

# ─────────────────────────────────────────
# 예시 질문
# ─────────────────────────────────────────
if not st.session_state.debate_history:
    st.markdown("""
    <div style="text-align:center; padding:40px 0 20px;">
        <div style="font-size:36px; opacity:0.4; margin-bottom:14px;">✦</div>
        <div style="font-family:'Noto Serif KR',serif; font-size:17px; color:#e8e4dc; margin-bottom:10px;">무엇이 궁금하신가요?</div>
        <div style="font-size:13px; color:#6b6b80; line-height:1.8;">질문 하나로 라이라와 지니가 토론을 시작합니다.<br>미라클이 그 본질을 꿰뚫는 통찰로 마무리합니다.</div>
    </div>
    """, unsafe_allow_html=True)

    examples = [
        "천지창조와 빅뱅은 같은 이야기인가?",
        "루시퍼는 왜 신을 대적했나?",
        "인간은 왜 사는가?",
        "선과 악은 누가 정하는가?",
        "신의 계획은 무엇인가?",
        "예수 십자가는 예정이었나?"
    ]
    cols = st.columns(3)
    for i, ex in enumerate(examples):
        with cols[i % 3]:
            if st.button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state.input_value = ex
                st.rerun()

# ─────────────────────────────────────────
# 토론 히스토리 표시
# ─────────────────────────────────────────
for item in st.session_state.debate_history:
    render_debate_item(item)

# ─────────────────────────────────────────
# 입력창
# ─────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])

with col1:
    question = st.text_input(
        "",
        value=st.session_state.input_value,
        placeholder="답을 찾지 못한 질문이 있나요?",
        label_visibility="collapsed",
        key="question_input",
        disabled=st.session_state.is_loading
    )

with col2:
    send = st.button(
        "탐구 ✦",
        use_container_width=True,
        disabled=st.session_state.is_loading
    )

# ─────────────────────────────────────────
# 질문 처리
# ─────────────────────────────────────────
if send and not st.session_state.is_loading:
    is_valid, error_msg = validate_question(question)
    if not is_valid:
        st.warning(error_msg)
    else:
        st.session_state.is_loading = True
        st.session_state.input_value = ""
        progress_placeholder = st.empty()
        try:
            result = run_debate(question.strip(), progress_placeholder)
            progress_placeholder.empty()
            st.session_state.debate_history.append(result)
        except Exception:
            progress_placeholder.empty()
            st.error("일시적 오류가 발생했습니다. 다시 시도해 주세요.")
        finally:
            st.session_state.is_loading = False
        st.rerun()
