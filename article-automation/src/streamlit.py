import pandas as pd
import streamlit as st
from datetime import datetime, date

from scrapper import ArticleScrapper
from llm import LLM
from utils import DataPreprocessor, Utils

import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s       - %(message)s [%(filename)s:%(lineno)d]',  # Custom log format
    datefmt='%Y-%m-%d %H:%M:%S'  # Custom date format
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main():
            
    # Set page title and configuration
    st.set_page_config(page_title="News Automation", layout="wide")
    
    # Add title
    st.title("News Article Automation")
    
    # Input Source Selectbox
    input_src_options = ["File Upload", "Article URL"]
    selected_src_option = st.selectbox("Select News Input Source:", input_src_options, index=None)

    # LLM model Selectbox
    llm_options = ["OpenAI", "Gemini"]
    selected_llm_option = st.selectbox("Select LLM Model:", llm_options, index=None)

    if selected_llm_option:
        st.write(f"Selected LLM Model: {selected_llm_option}")
    
    if selected_src_option == "File Upload":    
        submit_button = None
        # File upload section
        uploaded_file = st.file_uploader("Please attach the PDF/CSV/EXCEL or Outlook email file here", 
                                       type=['pdf', 'csv', 'excel','eml'],
                                       help="Upload your news document")
        st.write("Note: CSV/Excel file should have the following columns: 'Article URL', 'Received Date'")
        # Submit button - now directly under the file upload
        submit_button = st.button("Fetch Article URLs", use_container_width=True)
        # Handle form submission
        articles = []
        if submit_button:
            if uploaded_file is None:
                st.error("Please upload a file first!")
            else:
                # Add loading spinner while processing
                with st.spinner('Processing your file...'):
                    article_scrapper  = ArticleScrapper(logger)
                    if uploaded_file.type == 'application/pdf':                                           
                        articles = article_scrapper.scrape_pdf(uploaded_file)
                                # Initialize session state if it doesn't exist
                        if 'table_data' not in st.session_state:
                            # Create initial data
                            data = {
                                'Article': articles,
                                'Received Date': [datetime.today()] * len(articles)
                            }
                            st.session_state.table_data = pd.DataFrame(data)
                            st.session_state.table_data.index = st.session_state.table_data.index + 1
                            # Utils(logger).create_table(st, articles)
                            st.session_state.extract_button_clicked = False
                            if st.session_state.table_data is not None:
                                st.write(st.data_editor(
                                    st.session_state.table_data,
                                    column_config={
                                        "Article": st.column_config.TextColumn(
                                            "Article",
                                            disabled=False
                                        ),
                                        "Received Date": st.column_config.DateColumn(
                                            "Received Date",
                                            min_value=datetime(2000, 1, 1),
                                            max_value=datetime(2050, 12, 31),
                                            format="DD/MM/YYYY",
                                        )
                                    },
                                    hide_index=False,
                                    num_rows="fixed",
                                    key="editor_data"
                                ))
    # Handle 'Extract Features' Button
    # if st.button("Extract Features", use_container_width=True):
    #     st.session_state.extract_button_clicked = True  # Set extract button clicked state
    #     logger.info("Features extracted successfully!")
    #     st.write("Extracted Data:")
    #     st.write(st.session_state.table_data)
                        # if len(articles) > 0:
                        #     st.success(f"File processed successfully: {uploaded_file.name}")
                        #     if 'extract_button_clicked' not in st.session_state:
                        #         st.session_state.extract_button_clicked = False

                        #     if st.button("Extract Features", use_container_width=True, key="extract_features_btn"):
                        #         st.session_state.extract_button_clicked = True
                        #         logger.info("Extracting features from the uploaded file...")
                        #         st.write(f"Button State: {st.session_state.extract_button_clicked}")
                        #         logger.info(f"Button State: {st.session_state.extract_button_clicked}")
                        #         return
                        #     if st.session_state.extract_button_clicked:
                        #         st.write("Updated Data:")
                        #         st.write(st.session_state.table_data)

                    # elif uploaded_file.type == 'application/vnd.ms-outlook':
                    #     pass
                    # elif uploaded_file.type == 'text/csv':
                    #     pass
                    # elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    #     pass
                    # # Here you would add your file processing logic
                    # selected_month = None
                    # selected_year  = None
                    
                    
                    # # Display file details
                    # st.write("File Details:")
                    # file_details = {
                    #     "Filename": uploaded_file.name,
                    #     "File type": uploaded_file.type,
                    #     "Selected Month": selected_month,
                    #     "Selected Year": selected_year
                    # }
                    # st.json(file_details)
                                       
    if selected_src_option == "Article URL":
        article_url = st.text_input("Enter your Article URL:", placeholder="https://www.example.com")
        if article_url:
            st.write(f"Article URL: {article_url}")
                
        # Date selection section
        st.subheader("Select the date you received this news letter")

        today = date.today()

        selected_date = st.date_input("Article Received Date", None)

        if selected_date:
            # st.write(f"You selected: {selected_date}")
            # selected_month = selected_date.month
            # selected_year  = selected_date.year

            # Submit button - Scrape data from the URL and extract features using GenAI
            btn_extract_features = st.button("Extract Features", use_container_width=True, key="extract_article_features_btn")
            if btn_extract_features:
                if article_url:
                    # Add loading spinner while processing
                    with st.spinner('Extracting features from the article...'):
                        # Initialize the ArticleScrapper and LLM 
                        article_scrapper  = ArticleScrapper(logger)
                        llm_processor     = LLM(logger, selected_llm_option)
                        data_preprocessor = DataPreprocessor(logger)
                        page_document     = article_scrapper.extract_web_content(article_url)
                        features          = llm_processor.run_llm(page_document.page_content)
                        logger.info(f"Extracted Features: {features}")
                        # Here you would add your URL processing logic
                        st.success(f"Features extracted successfully for URL: {article_url}")
                        features          = data_preprocessor.clean_and_parse_features(features)
                        features['article_date'] = data_preprocessor.standardize_date(features.get('article_date'))
                        features['date'] =  data_preprocessor.standardize_date(features.get('date'))
                        
                        
                        # Display file details
                        st.write("Article Details:")
                        article_details = {
                            "article_received_month": selected_date.strftime("%B") + " " + str(selected_date.year),
                            "article_url": article_url,
                            "page_source": page_document.metadata.get('source'),
                            "page_title" : page_document.metadata.get('title'),
                            'page_content' : page_document.page_content,
                            'features'   : features
                        }
                        st.json(article_details)
if __name__ == "__main__":
    main()
