import streamlit as st
import pandas as pd
import google.generativeai as genai
import json

st.set_page_config(page_title="English Tool", layout="wide", initial_sidebar_state="expanded")

st.sidebar.markdown("##Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

prompt_translate = """Translate the given sentence or paragraph into Thai.
Return the translation in JSON format with the following structure:
{
    "translation": "translated sentence or paragraph"
}
Only return the JSON format without any explanation.

Example:
Input: "The quick brown fox jumps over the lazy dog."
Output: {
    "translation": "สุนัขจิ้งจอกสีน้ำตาลที่รวดเร็วกระโดดข้ามสุนัขขี้เกียจ"
}"""


tab1, tab2 = st.tabs(["Translate to Thai", "Grammar Checker"])

with tab1:
    st.markdown("Translation")
    user_input = st.text_area("Enter your paragraph:", "Your text here", key="tab1_input")

    if st.button('Submit', key="tab1_btn"):
        if not api_key:
            st.error("❌ Please enter your Gemini API key in the sidebar first!")
        elif not user_input.strip():
            st.error("❌ Please enter text!")
        else:
            with st.spinner("🔄 Processing..."):
                try:                 
                    translate_prompt = f"{prompt_translate}\n\nText to translate: {user_input}"
                    translate_response = model.generate_content(translate_prompt)
                    translate_text = translate_response.text
                    
                    if "```json" in translate_text:
                        translate_text = translate_text.split("```json")[1].split("```")[0]
                    elif "```" in translate_text:
                        translate_text = translate_text.split("```")[1].split("```")[0]
                    
                    sdict_translate = json.loads(translate_text)
                    
                    st.markdown('## Results:')
            
                    st.markdown('### Thai Translation:')
                    
                    st.success(sdict_translate['translation'])

                    csv_data = pd.DataFrame([{'Translation': sdict_translate['translation']}]).to_csv(index=False)
                    st.download_button(
                        label="📥 Download Translation as CSV",
                        data=csv_data,
                        file_name="translation.csv",
                        mime="text/csv"
                    )
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ Error parsing JSON response: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with tab2:
    st.markdown("### Grammar Checker")
    grammar_input = st.text_area("Enter text to check:", "Your text here", key="tab2_input")
    
    if st.button('Check Grammar', key="tab2_btn"):
        if not api_key:
            st.error("❌ Please enter your Gemini API key in the sidebar first!")
        elif not grammar_input.strip():
            st.error("❌ Please enter text!")
        else:
            with st.spinner("Checking grammar..."):
                try:
                    promt_Grammar = """Act as a Grammar checker.
                                        You will be given a sentence or paragraph with error.
                                        Identify and correct any grammatical errors.
                                        Return the corrected sentence or paragraph in JSON format with the following structure:"""
                    
                    response = model.generate_content(promt_Grammar)
                    response_text = response.text
                    
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0]
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0]
                    
                    result = json.loads(response_text)
                    
                    st.success("✅ Grammar Check Complete!")
                      
                    if result['errors']:
                        st.markdown("### 🔴 Errors Found:")
                        errors_df = pd.DataFrame(result['errors'])
                        st.dataframe(errors_df, use_container_width=True)
                        
                        csv_errors = errors_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Errors as CSV",
                            data=csv_errors,
                            file_name="grammar_errors.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No grammatical errors found! Your text is correct.")
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ Error parsing response: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

