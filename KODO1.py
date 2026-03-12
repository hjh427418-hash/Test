import streamlit as st
import PyPDF2
import google.generativeai as genai
import warnings

warnings.filterwarnings('ignore')

def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = "".join([page.extract_text() for page in pdf_reader.pages])
        return text[:15000]
    except Exception as e:
        return f"PDF 추출 오류: {str(e)}"

# --- UI 구성 ---
st.set_page_config(page_title="Reg-Tech Fixed Agent", layout="wide")

with st.sidebar:
    st.header("⚙️ Agent Settings")
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # 모델 선택 및 고정 설정
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = st.selectbox("AI Engine", available_models, index=0)
    except:
        selected_model = "models/gemini-1.5-flash"

    st.markdown("---")
    st.info("💡 **시연 모드 활성화**")

st.title("🛡️ 금융 규제 멀티 에이전트 분석 시스템")
st.subheader("PDF 분석 + 가상 뉴스 트렌드 결합 보고서")

uploaded_file = st.file_uploader("금융위원회/금감원 보도자료 PDF 업로드", type=['pdf'])

if uploaded_file is not None:
    if st.button("멀티 에이전트 협업 분석 시작"):
        with st.status("에이전트들이 협업 중입니다...", expanded=True) as status:
            # [핵심] 결과 고정을 위해 generation_config 추가
            model = genai.GenerativeModel(
                model_name=selected_model,
                generation_config={"temperature": 0} 
            )
            
            # Step 1: Doc Analyst
            st.write("🔍 **Doc Analyst**: PDF 내부의 핵심 팩트를 추출 중...")
            pdf_text = extract_text_from_pdf(uploaded_file)
            doc_prompt = f"당신은 금융감독관입니다. 다음 문서에서 '핵심 요약'과 '금융사 의무사항'을 아주 상세하게 팩트 위주로 추출하세요: {pdf_text}"
            doc_analysis = model.generate_content(doc_prompt).text
            
            # Step 2: News Scouter (가상 기사 리스트 포함 요청)
            st.write("🌐 **News Scouter**: 관련 뉴스 및 시장 트렌드를 분석 중...")
            news_prompt = f"""
            당신은 금융 전문 기자입니다. 다음 규제({pdf_text[:500]})와 관련하여 
            현재 가장 화제가 될 법한 가상의 뉴스 기사 제목 3개와 해당 기사의 핵심 내용을 정리하세요.
            마지막에는 '업계 동향 종합' 섹션을 추가하세요.
            """
            news_context = model.generate_content(news_prompt).text
            
            # Step 3: Compliance Editor
            st.write("📋 **Compliance Editor**: 최종 보고서 작성 중...")
            final_prompt = f"""
            너는 Deloitte 시니어 컨설턴트야. 아래 데이터를 통합해서 경영진 보고서를 작성해.
            
            [분석 근거 데이터]
            {doc_analysis}
            
            [참고 뉴스 동향]
            {news_context}
            
            [필수 포함 항목]
            1. 정책 핵심 요약 / 2. 주요 규제 변경 사항 / 3. 조직 영향도 분석 / 4. 책무구조도 반영 제언 / 5. 향후 대응 일정 추천
            """
            final_report = model.generate_content(final_prompt).text
            
            status.update(label="✅ 분석 완료!", state="complete", expanded=False)
            
            # 결과물 출력
            st.divider()
            st.markdown(final_report)
            
            # 상세 로그 영역 (재현님이 요청하신 팩트 데이터 + 기사 리스트 노출)
            with st.expander("🕵️ 에이전트별 상세 분석 근거 (Raw Data)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📍 PDF 추출 팩트 데이터")
                    st.info("Doc Analyst가 원문에서 필터링한 핵심 문구들입니다.")
                    st.write(doc_analysis)
                with col2:
                    st.subheader("📰 참고 뉴스 리스트")
                    st.info("News Scouter가 분석에 활용한 주요 뉴스 헤드라인입니다.")
                    st.write(news_context)

st.markdown("---")
st.caption("Deloitte Consulting - AI-powered Financial Governance Lab")
