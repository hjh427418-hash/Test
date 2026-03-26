import streamlit as st
import PyPDF2
import google.generativeai as genai
import warnings

warnings.filterwarnings('ignore')

# PDF 텍스트 추출 함수
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
    
    # [수정 포인트] 모델 ID를 gemini-2.0-flash로 고정
    SELECTED_MODEL = 'gemini-2.0-flash'
    st.success(f"현재 엔진: {SELECTED_MODEL}")
    st.info("💡 **시연 모드 활성화**")

st.title("🛡️ 금융 규제 멀티 에이전트 분석 시스템")
st.subheader("PDF 분석 + 가상 뉴스 트렌드 결합 보고서")

uploaded_file = st.file_uploader("금융위원회/금감원 보도자료 PDF 업로드", type=['pdf'])

if uploaded_file is not None:
    if st.button("멀티 에이전트 협업 분석 시작"):
        with st.status("에이전트들이 협업 중입니다...", expanded=True) as status:
            
            # 모델 설정 (SELECTED_MODEL 사용)
            model = genai.GenerativeModel(
                model_name=SELECTED_MODEL,
                generation_config={"temperature": 0} 
            )
            
            # 1. 텍스트 추출
            pdf_text = extract_text_from_pdf(uploaded_file)
            if "PDF 추출 오류" in pdf_text or not pdf_text.strip():
                st.error("PDF 내용을 읽을 수 없습니다.")
                st.stop()

            # Step 1: Doc Analyst
            st.write("🔍 **Doc Analyst**: PDF 핵심 팩트 추출 중...")
            doc_prompt = f"당신은 금융감독관입니다. 다음 문서에서 '핵심 요약'과 '금융사 의무사항'을 아주 상세하게 팩트 위주로 추출하세요: \n\n{pdf_text}"
            
            try:
                doc_analysis = model.generate_content(doc_prompt).text
            except Exception as e:
                st.error(f"Doc Analyst 에러: {e}")
                st.stop()
            
            # Step 2: News Scouter
            st.write("🌐 **News Scouter**: 관련 뉴스 및 시장 트렌드 분석 중...")
            news_prompt = f"금융 전문 기자로서 다음 규제({pdf_text[:500]})와 관련된 가상 뉴스 제목 3개와 핵심 내용, 업계 동향을 정리하세요."
            news_context = model.generate_content(news_prompt).text
            
            # Step 3: Compliance Editor
            st.write("📋 **Compliance Editor**: 최종 보고서 작성 중...")
            final_prompt = f"""
            Deloitte 컨설턴트 입장에서 아래 데이터를 통합해 경영진 보고서를 작성해.
            [분석 데이터]: {doc_analysis}
            [뉴스 동향]: {news_context}
            [항목]: 1. 요약, 2. 규제 변경, 3. 영향도, 4. 책무구조도 제언, 5. 일정
            """
            final_report = model.generate_content(final_prompt).text
            
            status.update(label="✅ 분석 완료!", state="complete", expanded=False)
            
            # 결과 출력
            st.divider()
            st.markdown(final_report)
            
            with st.expander("🕵️ 에이전트별 상세 분석 근거"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("📍 **PDF 추출 데이터**", doc_analysis)
                with col2:
                    st.write("📰 **참고 뉴스 리스트**", news_context)

st.markdown("---")
st.caption("Deloitte Consulting - AI-powered Financial Governance Lab")
