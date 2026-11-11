import streamlit as st
from cleaner import load_file, clean_dataframe
import tempfile
import os
import io

st.set_page_config(page_title='CSVH Cleaner', layout='wide')
st.title('Data Cleaner')
st.write('Upload CSV or Excel. The file is cleaned and returned for download.')

uploaded = st.file_uploader('Upload file', type=['csv','xlsx','xls'])

if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp:
        tmp.write(uploaded.getvalue())
        tmp_path = tmp.name
    df_raw = load_file(tmp_path)
    df_clean = clean_dataframe(df_raw)
    
    col1, col2 = st.columns(2)
    col1.metric('Rows before', len(df_raw))
    col2.metric('Rows after', len(df_clean))
    
    st.dataframe(df_clean.head(100))
    
    # Download
    out_name = f'cleaned_{uploaded.name}'
    if out_name.lower().endswith('.csv'):
        csv_bytes = df_clean.to_csv(index=False).encode('utf-8')
        st.download_button('Download cleaned CSV', csv_bytes, file_name=out_name, mime='text/csv')
    else:
        excel_buffer = io.BytesIO()
        df_clean.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        st.download_button('Download cleaned Excel', excel_buffer.getvalue(), file_name=out_name, mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    os.unlink(tmp_path)
