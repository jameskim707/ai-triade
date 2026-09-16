"""실행: python -m streamlit run app_fixed.py"""
import os
import html
import hashlib
import streamlit as st
from groq import Groq

st.set_page_config(page_title="AI 협업팀 — 인생의 모든 질문", page_icon="✦", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;900&family=Noto+Sans+KR:wght@400;500&display=swap');
.stApp {background:#0a0a0f;color:#e8e4dc;font-family:'Noto Sans KR',sans-serif;}
.main-header{text-align:center;padding:35px 0;border-bottom:1px solid #1e1e2e;margin-bottom:25px;}
.eyebrow{font-size:11px;letter-spacing:3px;color:#c9a84c;}
.main-title{font-family:'Noto Serif KR',serif;font-size:28px;font-weight:900;line-height:1.5;color:#e8e4dc;}
.main-title span{color:#c9a84c;}
.subtitle{font-size:13px;color:#aaa9b9;line-height:1.8;}
.team-row{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:18px;}
.badge{padding:6px 12px;border-radius:20px;border:1px solid #36364b;font-size:12px;}
.lyra{color:#7b9cda;}.genie{color:#a07bd4;}.miracle{color:#c9a84c;}
.question-bubble{background:#262117;border:1px solid #54462a;border-radius:18px;padding:15px 20px;margin:25px 0;white-space:pre-wrap;overflow-wrap:anywhere;}
.ai-card{border:1px solid #292939;border-radius:16px;background:#111118;margin:12px 0;overflow:hidden;}
.ai-card-header{padding:12px 20px;border-bottom:1px solid #292939;font-weight:600;}
.ai-role{font-size:11px;color:#aaa9b9;margin-left:12px;}
.ai-card-body{padding:18px 20px;line-height:1.9;color:#d4cfc5;white-space:pre-wrap;overflow-wrap:anywhere;}
.synthesis{border-color:#66532b;background:#19170f;}
.stButton>button,.stFormSubmitButton>button{background:#c9a84c !important;color:#0a0a0f !important;border:1px solid #c9a84c !important;border-radius:12px;font-weight:600;}
.stButton>button p,.stFormSubmitButton>button p{color:#0a0a0f !important;}
.stButton>button:hover,.stFormSubmitButton>button:hover{background:#e8c97a !important;border-color:#e8c97a !important;}
.stButton>button:disabled,.stFormSubmitButton>button:disabled{background:#655733 !important;color:#ffffff !important;opacity:1 !important;}
.stButton>button:disabled p,.stFormSubmitButton>button:disabled p{color:#ffffff !important;}
[data-testid="stWidgetLabel"] p,[data-testid="stCaptionContainer"] p{color:#c5c5d5 !important;}
[data-testid="stTextInput"] input{background:#161620 !important;color:#f5f3ee !important;-webkit-text-fill-color:#f5f3ee !important;caret-color:#e8c97a !important;}
[data-testid="stTextInput"] input::placeholder{color:#aeb0c1 !important;-webkit-text-fill-color:#aeb0c1 !important;opacity:1 !important;}
[data-testid="stTextInput"] [data-baseweb="input"]{background:#161620 !important;border-color:#676779 !important;}
[data-testid="stMarkdownContainer"] h3{color:#e8e4dc !important;}
[data-testid="stAlert"]{background:#202331 !important;color:#f1f1f6 !important;}
[data-testid="stAlert"] p{color:#f1f1f6 !important;}
</style>
""", unsafe_allow_html=True)

LANGUAGE = "한국어로 답하세요. 한자, 중국어, 일본어는 쓰지 마세요. 외국어 원문은 한글 음역과 뜻으로 설명하세요. 사실과 해석을 구분하고 확인하지 않은 출처나 원문을 지어내지 마세요. 별표나 마크다운 강조 없이 일반 문장으로 쓰고, 700자 이내에서 마지막 문장까지 완결하세요."
PROMPTS = {
    "lyra_1": LANGUAGE + " 당신은 라이라 역할입니다. 종교학, 언어학, 신학, 역사적 관점으로 질문을 탐구하세요. 모든 질문을 억지로 종교에 연결하지 마세요. 핵심을 구체적으로 3~4문장으로 답하세요.",
    "genie": LANGUAGE + " 당신은 지니 역할입니다. 과학, 철학, 심리학, 논리적 관점에서 라이라의 답변을 검토하세요. 타당한 점은 인정하고 근거가 부족한 점이나 새로운 해석을 제시하세요. 억지 반박은 하지 마세요. 3~4문장으로 답하세요.",
    "lyra_2": LANGUAGE + " 당신은 라이라 역할입니다. 지니의 검토에 타당한 부분은 인정하고 신학적·역사적 맥락을 더하세요. 단순 반복을 피하고 3~4문장으로 답하세요.",
    "miracle": LANGUAGE + " 당신은 미라클 역할입니다. 전체 토론의 공통점과 차이를 짚고 근거 있는 결론과 아직 모르는 점을 구분하세요. 새로운 통찰이나 열린 질문으로 마무리하세요. 3~5문장으로 답하세요.",
}

def has_cjk(text):
    ranges = ((0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF),
              (0x20000, 0x323AF), (0x3040, 0x30FF), (0x31F0, 0x31FF), (0xFF66, 0xFF9F))
    return any(any(start <= ord(char) <= end for start, end in ranges) for char in text)

def get_api_key():
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key
    try:
        return str(st.secrets.get("GROQ_API_KEY", "")).strip()
    except (FileNotFoundError, KeyError):
        return ""

def call_ai(client, prompt_key, content, model):
    system = PROMPTS[prompt_key]
    for attempt in range(3):
        messages = [{"role": "system", "content": system}, {"role": "user", "content": content}]
        result = ""
        truncated = False
        # 최초 요청 + 최대 두 번 이어쓰기. 사용량 폭증을 방지하는 유한 루프.
        for continuation in range(3):
            response = client.chat.completions.create(
                model=model, max_tokens=2400, messages=messages,
            )
            choice = response.choices[0]
            piece = choice.message.content or ""
            result += piece
            truncated = choice.finish_reason == "length"
            if not truncated:
                break
            messages.extend([
                {"role": "assistant", "content": piece},
                {"role": "user", "content": "출력 한도로 답변이 끊겼습니다. 앞부분을 반복하지 말고 끊긴 지점부터 이어서 마지막 문장까지 짧게 완결하세요."},
            ])
        result = result.strip()
        if not result:
            raise ValueError("empty_response")
        if not has_cjk(result):
            if truncated:
                result += "\n\n[출력 한도로 답변이 아직 완결되지 않았습니다.]"
            return result
        system = "한자와 일본어 없이 한글로 다시 작성하세요.\n" + system
    raise ValueError("language_retry_failed")

def run_debate(client, question, progress, model):
    progress.info("💬 라이라가 답변 중...")
    s1 = call_ai(client, "lyra_1", f"질문: {question}", model)
    progress.info("💬 지니가 검토 중...")
    s2 = call_ai(client, "genie", f"질문: {question}\n\n라이라의 답변: {s1}", model)
    progress.info("💬 라이라가 재반응 중...")
    s3 = call_ai(client, "lyra_2", f"질문: {question}\n\n첫 답변: {s1}\n\n지니의 검토: {s2}", model)
    progress.info("✦ 미라클이 최종 통찰 중...")
    s4 = call_ai(client, "miracle", f"질문: {question}\n\n라이라: {s1}\n\n지니: {s2}\n\n라이라 재반응: {s3}", model)
    return {"question": question, "answers": [s1, s2, s3, s4]}

def render_debate(item):
    st.markdown(f'<div class="question-bubble">{html.escape(item["question"])}</div>', unsafe_allow_html=True)
    labels = [("라이라", "lyra", "종교 · 언어학 · 1차 답변"),
              ("지니", "genie", "과학 · 철학 · 검토"),
              ("라이라", "lyra", "종교 · 언어학 · 재반응"),
              ("미라클", "miracle", "최종 통찰")]
    for (name, color, role), answer in zip(labels, item["answers"]):
        extra = " synthesis" if color == "miracle" else ""
        st.markdown(f'<div class="ai-card{extra}"><div class="ai-card-header {color}">{name}<span class="ai-role">{role}</span></div><div class="ai-card-body">{html.escape(answer)}</div></div>', unsafe_allow_html=True)

def submit_question():
    question = st.session_state.question_input.strip()
    if len(question) < 5:
        st.session_state.notice = "질문을 5자 이상 입력해주세요."
    elif len(question) > 500:
        st.session_state.notice = "질문은 500자 이내로 입력해주세요."
    else:
        st.session_state.pending_question = question
        st.session_state.question_input = ""
        st.session_state.notice = ""

def choose_example(question):
    st.session_state.question_input = question

for key, default in [("debate_history", []), ("question_input", ""), ("pending_question", ""), ("notice", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown('''<div class="main-header"><div class="eyebrow">AI Collaboration Team</div><div class="main-title">인생의 모든 질문,<br><span>세 개의 시선으로 탐구합니다</span></div><div class="subtitle">종교, 철학, 과학 — 라이라와 지니가 토론하고, 미라클이 통찰을 더합니다.</div><div class="team-row"><span class="badge lyra">● 라이라 · 종교/언어학</span><span class="badge genie">● 지니 · 과학/철학</span><span class="badge miracle">● 미라클 · 최종 통찰</span></div></div>''', unsafe_allow_html=True)
st.caption("이 앱은 하나의 Groq 모델에 세 가지 역할을 부여합니다. GPT·Gemini·Claude를 직접 연결한 앱은 아닙니다.")
api_key = get_api_key()
selected_model = ""
if api_key:
    fingerprint = hashlib.sha256(api_key.encode()).hexdigest()
    if st.button("모델 목록 새로고침"):
        st.session_state.pop("model_fingerprint", None)
    if st.session_state.get("model_fingerprint") != fingerprint:
        try:
            with st.spinner("Groq 모델 목록 확인 중..."):
                client = Groq(api_key=api_key, timeout=15.0, max_retries=0)
                try:
                    models = client.models.list()
                finally:
                    client.close()
                st.session_state.available_models = sorted(
                    m.id for m in models.data if getattr(m, "active", True)
                    and not any(word in m.id.lower() for word in ("whisper", "tts", "guard", "safeguard", "orpheus"))
                )
                st.session_state.model_fingerprint = fingerprint
        except Exception as exc:
            st.session_state.available_models = []
            st.error(f"모델 목록 조회 실패: {type(exc).__name__}. API 키와 연결 설정을 확인해주세요.")
    choices = st.session_state.get("available_models", [])
    if choices:
        preferred = next((m for m in ("llama-3.3-70b-versatile", "llama-3.1-8b-instant") if m in choices), choices[0])
        selected_model = st.selectbox("토론 모델", choices, index=choices.index(preferred))
        st.caption("목록에 표시되어도 조직 권한이나 모델 기능에 따라 대화 요청이 제한될 수 있습니다.")
    else:
        st.warning("사용 가능한 대화 모델을 확인하지 못했습니다. 모델 목록을 새로고침해주세요.")
if not api_key:
    st.info('API 키를 설정하면 토론을 시작할 수 있습니다. 프로젝트의 .streamlit/secrets.toml에 GROQ_API_KEY = "실제 키"를 입력하세요. 배포 환경에서는 Secrets에 설정하세요.')

if not st.session_state.debate_history:
    st.markdown("### 무엇이 궁금하신가요?")
    examples = ["천지창조는 정말 6일인가?", "루시퍼는 왜 신을 대적했나?", "인간은 왜 사는가?", "선과 악은 누가 정하는가?", "신의 계획은 무엇인가?", "예수 십자가는 예정이었나?"]
    cols = st.columns(3)
    for i, example in enumerate(examples):
        with cols[i % 3]:
            st.button(example, key=f"ex_{i}", on_click=choose_example, args=(example,))

for item in st.session_state.debate_history:
    render_debate(item)
st.divider()
with st.form("question_form"):
    st.text_input("질문", placeholder="답을 찾지 못한 질문이 있나요?", key="question_input", max_chars=500)
    st.form_submit_button("탐구 ✦", on_click=submit_question, disabled=not bool(api_key and selected_model))
if st.session_state.notice:
    st.warning(st.session_state.notice)

if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = ""
    progress = st.empty()
    try:
        client = Groq(api_key=api_key, timeout=30.0, max_retries=1)
        try:
            result = run_debate(client, question, progress, selected_model)
        finally:
            client.close()
        st.session_state.debate_history.append(result)
        progress.empty()
        st.rerun()
    except Exception as exc:
        progress.empty()
        status = getattr(exc, "status_code", None)
        if status == 401:
            message = "API 키가 유효하지 않습니다. GROQ_API_KEY를 확인해주세요."
        elif status == 429:
            message = "API 사용량 한도에 도달했습니다. 잠시 뒤 다시 시도해주세요."
        elif status == 400 or status == 404:
            message = "모델 또는 요청 설정 오류입니다. Groq에서 해당 모델을 사용할 수 있는지 확인해주세요."
        elif isinstance(exc, ValueError):
            message = "빈 답변 또는 한국어 변환 실패입니다. 다시 시도해주세요."
        else:
            message = "연결 또는 처리 오류입니다. 인터넷 연결과 패키지 설치를 확인해주세요."
        st.error(message)
        st.caption(f"오류 유형: {type(exc).__name__}" + (f" / HTTP {status}" if status else ""))
        st.info("질문을 다시 입력해 재시도해주세요. 완료되지 않은 토론은 기록에 추가되지 않았습니다.")
