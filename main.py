import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import json
import urllib.parse
import os
import PyPDF2
import pandas as pd
import docx2txt


def scrape_text_from_url(url):

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the URL: {url}")
    soup = BeautifulSoup(response.content, 'html.parser')
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def scrap_pdf_from_url(url):

    response = requests.get(f"https://pdf2text-mounseflit.vercel.app/api/pdf-text-all?pdfUrl={url}")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the URL: {url}")
    return response.text
    

def extract_text_from_document(doc_path):
        """Extract text from various document types including PDF, DOCX, TXT, XLSX, etc."""
        
        file_ext = os.path.splitext(doc_path)[1].lower()
        
        # Text files
        if file_ext == '.txt':
            with open(doc_path, 'r', encoding='utf-8', errors='replace') as file:
                return file.read()
        
        # PDF files
        elif file_ext == '.pdf':
            try:
                text = ""
                with open(doc_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                return text
            except Exception as e:
                return f"Error extracting PDF text: {str(e)}"
        
        # Excel files
        elif file_ext in ['.xlsx', '.xls']:
            try:
                df = pd.read_excel(doc_path)
                return df.to_string()
            except Exception as e:
                return f"Error extracting Excel text: {str(e)}"
            
        # DOCX files
        elif file_ext == '.docx':
            try:
                text = docx2txt.process(doc_path)
                return text
            except Exception as e:
                return f"Error extracting DOCX text: {str(e)}"
            
        # PPTX files
        elif file_ext == '.pptx':
            try:
                text = docx2txt.process(doc_path)
                return text
            except Exception as e:
                return f"Error extracting PPTX text: {str(e)}"
        
        # CSV files
        elif file_ext == '.csv':
            try:
                df = pd.read_csv(doc_path)
                return df.to_string()
            except Exception as e:
                return f"Error extracting CSV text: {str(e)}"
        
        else:
            return f"Unsupported file format: {file_ext}"
        
        


def call_llm_api(article_text, format, Example):

    api_url = "https://a.picoapps.xyz/ask-ai?prompt="
    prompt = '''Text Content : '''  + article_text + ''' 
    Task :  You are an llm Specialized in data extraction and normalization in '''  + format + ''' format, where you Extract and format data without missing anything.
    Output Example : '''  + Example + ''' 
    '''
    
    encoded_prompt = urllib.parse.quote(prompt)
    full_url = f"{api_url}{encoded_prompt}"
    response = requests.get(full_url)
    if response.status_code != 200:
        raise Exception(f"Failed to call the LLM API: {response.status_code}")
    result = response.json()

    # Parse the API response
    if isinstance(result, dict) and 'response' in result:
        # The API returned a dictionary with a 'response' key
        result = result['response']

    return result


def save_and_clean_json(response, file_path):
    # First, handle the case where response is a string
    if isinstance(response, str):
        response = json.loads(response.replace('\n', '').replace('\\', ''))
    
    # If response is a dict and contains 'response' key
    if isinstance(response, dict) and 'response' in response:
        response = response['response']
        # If response is still a string, parse it
        if isinstance(response, str):
            response = json.loads(response.replace('\n', '').replace('\\', ''))

    # Write the cleaned JSON to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)
    
    return response


def fix_unicode(text):
     # Preprocess text - replace common Unicode characters
    # French characters
    text = text.replace('\\u00e9', 'é').replace('\\u00e8', 'è').replace('\\u00ea', 'ê')
    text = text.replace('\\u00e0', 'à').replace('\\u00e2', 'â').replace('\\u00f9', 'ù')
    text = text.replace('\\u00fb', 'û').replace('\\u00ee', 'î').replace('\\u00ef', 'ï')
    text = text.replace('\\u00e7', 'ç').replace('\\u0153', 'œ').replace('\\u00e6', 'æ')
    text = text.replace('\\u20ac', '€').replace('\\u00ab', '«').replace('\\u00bb', '»')
    text = text.replace('\\u2013', '–').replace('\\u2014', '—').replace('\\u2018', '‘')
    text = text.replace('\\u2019', '’').replace('\\u201a', '‚').replace('\\u201c', '“')
    text = text.replace('\\u201d', '”').replace('\\u201e', '„').replace('\\u2026', '…')
    text = text.replace('\\u2030', '‰').replace('\\u0152', 'Œ').replace('\\u00a0', ' ')
    text = text.replace('\\u00b0', '°').replace('\\u00a3', '£').replace('\\u00a7', '§')
    text = text.replace('\\u00b7', '·').replace('\\u00bf', '¿').replace('\\u00a9', '©')
    text = text.replace('\\u00ae', '®').replace('\\u2122', '™').replace('\\u00bc', '¼')
    text = text.replace('\\u00bd', '½').replace('\\u00be', '¾').replace('\\u00b1', '±')
    text = text.replace('\\u00d7', '×').replace('\\u00f7', '÷').replace('\\u00a2', '¢')
    text = text.replace('\\u00a5', '¥').replace('\\u00ac', '¬').replace('\\u00b6', '¶')
    text = text.replace('\\u2022', '•')

    # Spanish characters
    text = text.replace('\\u00f1', 'ñ').replace('\\u00ed', 'í').replace('\\u00f3', 'ó')
    text = text.replace('\\u00fa', 'ú').replace('\\u00fc', 'ü').replace('\\u00a1', '¡')
    text = text.replace('\\u00bf', '¿').replace('\\u00e1', 'á').replace('\\u00e9', 'é')
    text = text.replace('\\u00f3', 'ó').replace('\\u00fa', 'ú').replace('\\u00fc', 'ü')
    # German characters
    text = text.replace('\\u00df', 'ß').replace('\\u00e4', 'ä').replace('\\u00f6', 'ö')
    text = text.replace('\\u00fc', 'ü')

    # Italian characters
    text = text.replace('\\u00e0', 'à').replace('\\u00e8', 'è').replace('\\u00e9', 'é')
    text = text.replace('\\u00ec', 'ì').replace('\\u00f2', 'ò').replace('\\u00f9', 'ù')
    text = text.replace('\\u00f9', 'ù')

    # Russian characters
    text = text.replace('\\u0410', 'А').replace('\\u0411', 'Б').replace('\\u0412', 'В')
    text = text.replace('\\u0413', 'Г').replace('\\u0414', 'Д').replace('\\u0415', 'Е')
    text = text.replace('\\u0416', 'Ж').replace('\\u0417', 'З').replace('\\u0418', 'И')
    text = text.replace('\\u0419', 'Й').replace('\\u041a', 'К').replace('\\u041b', 'Л')
    text = text.replace('\\u041c', 'М').replace('\\u041d', 'Н').replace('\\u041e', 'О')
    text = text.replace('\\u041f', 'П').replace('\\u0420', 'Р').replace('\\u0421', 'С')
    text = text.replace('\\u0422', 'Т').replace('\\u0423', 'У').replace('\\u0424', 'Ф')
    text = text.replace('\\u0425', 'Х').replace('\\u0426', 'Ц').replace('\\u0427', 'Ч')
    text = text.replace('\\u0428', 'Ш').replace('\\u0429', 'Щ').replace('\\u042a', 'Ъ')
    text = text.replace('\\u042b', 'Ы').replace('\\u042c', 'Ь').replace('\\u042d', 'Э')
    text = text.replace('\\u042e', 'Ю').replace('\\u042f', 'Я').replace('\\u0430', 'а')
    text = text.replace('\\u0431', 'б').replace('\\u0432', 'в').replace('\\u0433', 'г')
    text = text.replace('\\u0434', 'д').replace('\\u0435', 'е').replace('\\u0436', 'ж')
    text = text.replace('\\u0437', 'з').replace('\\u0438', 'и').replace('\\u0439', 'й')
    text = text.replace('\\u043a', 'к').replace('\\u043b', 'л').replace('\\u043c', 'м')
    text = text.replace('\\u043d', 'н').replace('\\u043e', 'о').replace('\\u043f', 'п')
    text = text.replace('\\u0440', 'р').replace('\\u0441', 'с').replace('\\u0442', 'т')
    text = text.replace('\\u0443', 'у').replace('\\u0444', 'ф').replace('\\u0445', 'х')
    text = text.replace('\\u0446', 'ц').replace('\\u0447', 'ч').replace('\\u0448', 'ш')
    text = text.replace('\\u0449', 'щ').replace('\\u044a', 'ъ').replace('\\u044b', 'ы')
    text = text.replace('\\u044c', 'ь').replace('\\u044d', 'э').replace('\\u044e', 'ю')
    text = text.replace('\\u044f', 'я')
    
    # Arabic characters - generic replacement for common encoding issues
    text = text.replace('\\u0627', 'ا').replace('\\u064a', 'ي').replace('\\u0644', 'ل')
    text = text.replace('\\u062a', 'ت').replace('\\u0646', 'ن').replace('\\u0633', 'س')
    text = text.replace('\\u0645', 'م').replace('\\u0631', 'ر').replace('\\u0648', 'و')
    text = text.replace('\\u0639', 'ع').replace('\\u062f', 'د').replace('\\u0628', 'ب')
    text = text.replace('\\u0649', 'ى').replace('\\u0629', 'ة').replace('\\u062c', 'ج')
    text = text.replace('\\u0642', 'ق').replace('\\u0641', 'ف').replace('\\u062d', 'ح')
    text = text.replace('\\u0635', 'ص').replace('\\u0637', 'ط').replace('\\u0632', 'ز')
    text = text.replace('\\u0634', 'ش').replace('\\u063a', 'غ').replace('\\u062e', 'خ')
    text = text.replace('\\u0623', 'أ').replace('\\u0621', 'ء').replace('\\u0624', 'ؤ')
    text = text.replace('\\u0626', 'ئ').replace('\\u0625', 'إ').replace('\\u0651', 'ّ')
    text = text.replace('\\u0652', 'ْ').replace('\\u064b', 'ً').replace('\\u064c', 'ٌ')
    text = text.replace('\\u064d', 'ٍ').replace('\\u064f', 'ُ').replace('\\u0650', 'ِ')
    text = text.replace('\\u064e', 'َ').replace('\\u0653', 'ٓ').replace('\\u0654', 'ٔ')
    text = text.replace('\\u0670', 'ٰ').replace('\\u0671', 'ٱ').replace('\\u0672', 'ٲ')
    text = text.replace('\\u0673', 'ٳ').replace('\\u0675', 'ٵ').replace('\\u0676', 'ٶ')
    text = text.replace('\\u0677', 'ٷ').replace('\\u0678', 'ٸ').replace('\\u0679', 'ٹ')
    text = text.replace('\\u067a', 'ٺ').replace('\\u067b', 'ٻ').replace('\\u067c', 'ټ')
    text = text.replace('\\u067d', 'ٽ').replace('\\u067e', 'پ').replace('\\u067f', 'ٿ')
    text = text.replace('\\u0680', 'ڀ').replace('\\u0681', 'ځ').replace('\\u0682', 'ڂ')
    text = text.replace('\\u0683', 'ڃ').replace('\\u0684', 'ڄ').replace('\\u0685', 'څ')
    text = text.replace('\\u0686', 'چ').replace('\\u0687', 'ڇ').replace('\\u0688', 'ڈ')
    text = text.replace('\\u0689', 'ډ').replace('\\u068a', 'ڊ').replace('\\u068b', 'ڋ')
    text = text.replace('\\u068c', 'ڌ').replace('\\u068d', 'ڍ').replace('\\u068e', 'ڎ')
    text = text.replace('\\u068f', 'ڏ').replace('\\u0690', 'ڐ').replace('\\u0691', 'ڑ')
    text = text.replace('\\u0692', 'ڒ').replace('\\u0693', 'ړ').replace('\\u0694', 'ڔ')
    text = text.replace('\\u0695', 'ڕ').replace('\\u0696', 'ږ').replace('\\u0697', 'ڗ')
    text = text.replace('\\u0698', 'ژ').replace('\\u0699', 'ڙ').replace('\\u069a', 'ښ')
    text = text.replace('\\u069b', 'ڛ').replace('\\u069c', 'ڜ').replace('\\u069d', 'ڝ')
    text = text.replace('\\u069e', 'ڞ').replace('\\u069f', 'ڟ').replace('\\u06a0', 'ڠ')
    text = text.replace('\\u06a1', 'ڡ').replace('\\u06a2', 'ڢ').replace('\\u06a3', 'ڣ')
    text = text.replace('\\u06a4', 'ڤ').replace('\\u06a5', 'ڥ').replace('\\u06a6', 'ڦ')
    text = text.replace('\\u06a7', 'ڧ').replace('\\u06a8', 'ڨ').replace('\\u06a9', 'ک')
    text = text.replace('\\u06aa', 'ڪ').replace('\\u06ab', 'ګ').replace('\\u06ac', 'ڬ')
    text = text.replace('\\u06ad', 'ڭ').replace('\\u06ae', 'ڮ').replace('\\u06af', 'گ')
    text = text.replace('\\u06b0', 'ڰ').replace('\\u06b1', 'ڱ').replace('\\u06b2', 'ڲ')
    text = text.replace('\\u06b3', 'ڳ').replace('\\u06b4', 'ڴ').replace('\\u06b5', 'ڵ')
    text = text.replace('\\u06b6', 'ڶ').replace('\\u06b7', 'ڷ').replace('\\u06b8', 'ڸ')
    text = text.replace('\\u06b9', 'ڹ').replace('\\u06ba', 'ں').replace('\\u06bb', 'ڻ')

    return text


def main():
        st.set_page_config(page_title="Extracteur de Données", page_icon="📊", layout="wide")
        
        # Custom CSS for better styling
        st.markdown("""
            <style>
            .main-header {
                font-size: 2.5rem;
                color: #1E88E5;
                text-align: center;
                margin-bottom: 2rem;
            }
            .subheader {
                font-size: 1.5rem;
                color: #0D47A1;
                margin-top: 1.5rem;
            }
            .sidebar-header {
                font-size: 1.2rem;
                font-weight: bold;
                color: #1E88E5;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<h1 class='main-header'>Extraction et Formatage Automatique de Données ✨📝</h1>", unsafe_allow_html=True)
        
        # Sidebar configuration
        st.sidebar.markdown("<h2 class='sidebar-header'>Paramètres</h2>", unsafe_allow_html=True)
        
        format = st.sidebar.selectbox(

            "Format de normalisation des données :",
            ["json", "csv", "xml", "txt", "bulletpoints", "paragraphes", "résumé"],
            index=0
        )

        st.sidebar.markdown("<h3 class='sidebar-header'>Exemple de Sortie</h3>", unsafe_allow_html=True)
        example_output = st.sidebar.text_area("Fournissez un exemple du format souhaité", height=200)

        # Main content area with tabs
        tabs = st.tabs(["Extraction de Données", "À Propos"])
        
        with tabs[0]:
            st.markdown("<h2 class='subheader'>Choisissez votre source de données</h2>", unsafe_allow_html=True)
            
            input_method = st.radio(
                "Méthode d'entrée :", 
                ["Page Web (URL)", "Texte manuel", "Fichier local", "Document PDF en ligne"],
                captions=["Extraire depuis une URL", "Coller ou écrire du texte", "Télécharger un fichier", "Utiliser un PDF accessible via URL"]
            )
            
            article_text = ""
            url = ""
            
            if input_method == "Page Web (URL)":
                url = st.text_input("Entrez l'URL de la page web", placeholder="https://exemple.com/article")
                if st.button("Extraire le contenu", type="primary"):
                    if url:
                        with st.spinner("Extraction en cours..."):
                            try:
                                article_text = scrape_text_from_url(url)
                                st.success("Extraction réussie!")
                                with st.spinner(f"Formatage des données en {format}..."):
                                    try:
                                        result = call_llm_api(article_text, format, example_output)
                                        result = fix_unicode(str(result))
                                        
                                        st.markdown("<h2 class='subheader'>Résultats</h2>", unsafe_allow_html=True)
                                        st.code(result)
                                        
                                        # Add download button
                                        file_name = f"data_formatted.{format if format not in ['bulletpoints', 'paragraphes', 'résumé'] else 'txt'}"
                                        st.download_button(
                                            label="Télécharger les résultats",
                                            data=result,
                                            file_name=file_name,
                                            mime="text/plain",
                                            use_container_width=True
                                        )
                                    except Exception as e:
                                        st.error(f"Erreur lors du formatage: {str(e)}")

                            except Exception as e:
                                st.error(f"Erreur lors de l'extraction: {str(e)}")
                    else:
                        st.warning("Veuillez entrer une URL valide")
            
            elif input_method == "Texte manuel":
                article_text = st.text_area("Entrez ou collez votre texte ici", height=300)
                with st.spinner(f"Formatage des données en {format}..."):
                        try:
                            result = call_llm_api(article_text, format, example_output)
                            result = fix_unicode(str(result))
                            
                            st.markdown("<h2 class='subheader'>Résultats</h2>", unsafe_allow_html=True)
                            st.code(result)
                            
                            # Add download button
                            file_name = f"data_formatted.{format if format not in ['bulletpoints', 'paragraphes', 'résumé'] else 'txt'}"
                            st.download_button(
                                label="Télécharger les résultats",
                                data=result,
                                file_name=file_name,
                                mime="text/plain",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Erreur lors du formatage: {str(e)}")
            
            elif input_method == "Fichier local":
                uploaded_file = st.file_uploader("Choisissez un fichier", type=['pdf', 'docx', 'txt', 'xlsx', 'csv', 'pptx'])
                if uploaded_file is not None:
                    with st.spinner("Lecture du fichier..."):
                        # Save uploaded file temporarily
                        temp_file_path = os.path.join(os.getcwd(), uploaded_file.name)
                        with open(temp_file_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                        
                        article_text = extract_text_from_document(temp_file_path)
                        
                        # Clean up
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)
                        
                        st.success("Fichier chargé avec succès!")

                        with st.spinner(f"Formatage des données en {format}..."):
                            try:
                                result = call_llm_api(article_text, format, example_output)
                                result = fix_unicode(str(result))
                                
                                st.markdown("<h2 class='subheader'>Résultats</h2>", unsafe_allow_html=True)
                                st.code(result)
                                
                                # Add download button
                                file_name = f"data_formatted.{format if format not in ['bulletpoints', 'paragraphes', 'résumé'] else 'txt'}"
                                st.download_button(
                                    label="Télécharger les résultats",
                                    data=result,
                                    file_name=file_name,
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Erreur lors du formatage: {str(e)}")
            
            elif input_method == "Document PDF en ligne":
                pdf_url = st.text_input("Entrez l'URL du PDF", placeholder="https://exemple.com/document.pdf")
                if st.button("Extraire le contenu du PDF", type="primary"):
                    if pdf_url:
                        with st.spinner("Extraction du PDF en cours..."):
                            try:
                                article_text = scrap_pdf_from_url(pdf_url)
                                st.success("PDF extrait avec succès!")

                                with st.spinner(f"Formatage des données en {format}..."):
                                    try:
                                        result = call_llm_api(article_text, format, example_output)
                                        result = fix_unicode(str(result))
                                        
                                        st.markdown("<h2 class='subheader'>Résultats</h2>", unsafe_allow_html=True)
                                        st.code(result)
                                        
                                        # Add download button
                                        file_name = f"data_formatted.{format if format not in ['bulletpoints', 'paragraphes', 'résumé'] else 'txt'}"
                                        st.download_button(
                                            label="Télécharger les résultats",
                                            data=result,
                                            file_name=file_name,
                                            mime="text/plain",
                                            use_container_width=True
                                        )
                                    except Exception as e:
                                        st.error(f"Erreur lors du formatage: {str(e)}")
                            except Exception as e:
                                st.error(f"Erreur lors de l'extraction du PDF: {str(e)}")
                    else:
                        st.warning("Veuillez entrer une URL de PDF valide")
            
            
                   
        
        with tabs[1]:
            st.markdown("<h2 class='subheader'>À Propos de cet Outil</h2>", unsafe_allow_html=True)
            st.markdown("""
                <div style="padding: 20px; border-radius: 10px;">
                    <h3>Développé par AI Crafters ✨ pour Attijari Wafa Bank</h3>
                    <p>Cet outil d'extraction et de formatage automatique de données est conçu pour simplifier 
                    le traitement des informations provenant de diverses sources.</p>
                    <p>Il permet d'extraire des données structurées à partir de pages web, documents PDF, 
                    ou texte brut, puis de les normaliser dans le format de votre choix.</p>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
