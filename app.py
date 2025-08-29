from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
import io
load_dotenv()

# Model
llm = ChatGroq(model="openai/gpt-oss-20b")
# Tool
search_tool = TavilySearch(topic="general", max_results=2)

def generate_insights(company_name, product_name,company_url, company_competitors):
    # Perform the search
    search_query = f"Site:{company_url} company strategy, leadership, competitors, business model"
    search_results = search_tool.invoke(search_query)
    print("Search Results: ", search_results)
    
    messages = [
        SystemMessage(f"You are a sales assistant agent that provides concise and structured insights. You only respond to requests related to prospect insights, competitors, or company strategy. You will not engage in general conversation or unrelated inquiries. All outputs must be concise, formatted as a one-page sales insights report, 300 words maximum. Use short paragraphs or bullet points to ensure brevity."),
        HumanMessage(content=f"""
        Company Info from Tavily: {search_results}
        
        Company: {company_name}
        Product: {product_name}
        Competitors: {company_competitors}
        
        Generate a concise summary of one single page in length. Report structure:
            1. Company strategy related to {product_name}  For public companies, include insights from 10-Ks, annual reports, or other relevant documents available online.
            2. Possible competitors or partnerships (including {company_competitors})
            3. Leadership and decision-makers relevant to this area
             Provide URLs to original articles, filings, or press releases referenced. Format output in clear sections with bullet points. Output should be 300 words maximum. Keep the output concise enough to fit on one printed 8x11 page """)
    ]

    model_response = llm.invoke(messages)
    print("\n Model Response: ", model_response.content)
    return model_response.content

def create_pdf(report_content, company_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Sales Insights Report - {company_name}', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 12)
    lines = report_content.split('\n')
    for line in lines:
        if line.strip():
            pdf.cell(0, 6, line.encode('latin-1', 'replace').decode('latin-1'), 0, 1)
        else:
            pdf.ln(3)
    
    pdf_output = io.BytesIO()
    pdf_string = pdf.output(dest='S').encode('latin-1')
    pdf_output.write(pdf_string)
    pdf_output.seek(0)
    return pdf_output.getvalue()



# ============= UI ==============
st.title("InsightEdge")
st.subheader("Generates a single-page sales prospect insight report from publicly available web data.")
st.divider()

# company name
company_name = st.text_input("Company Name")

# company URL
company_url = st.text_input("Company URL")

# product name
product_name = st.text_input("Product Name")

# company competitors
company_competitors = st.text_input("Company Competitors")

report = None

if st.button("Generate Report"):
    if company_name and company_url:
        with st.spinner("Generating Report..."):
            result = generate_insights(company_name, product_name, company_url, company_competitors)
            
            st.divider()
            st.write(result)
            
            # Assign the result to the report variable
            report = result
    if report is not None:
        # download as a text file
        st.download_button("Download Report", report, file_name="sales_report.txt", mime="text/plain")
        
        # download as a pdf file
        pdf_data = create_pdf(report, company_name)
        st.download_button(
            "Download Report as PDF",
            pdf_data,
            file_name=f"sales_report_{company_name}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Please enter a company name and URL")