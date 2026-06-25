import markdown2
from fpdf import FPDF
import os
from crewai.tools import BaseTool

class MarkdownToPDFTool(BaseTool):
    name: str = "Markdown to PDF Converter"
    description: str = "Converts markdown text to a PDF file. Use this to prepare the resume before sending."
    
    def _run(self, markdown_text: str, output_filepath: str) -> str:
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_filepath) or '.', exist_ok=True)
            
            # Convert MD to HTML
            html = markdown2.markdown(markdown_text)
            
            # Initialize FPDF and add a page
            pdf = FPDF()
            pdf.add_page()
            
            # Write HTML to the PDF
            pdf.write_html(html)
            
            # Output the PDF
            pdf.output(output_filepath)
            
            return f"Successfully generated PDF at {output_filepath}"
        except Exception as e:
            return f"Failed to generate PDF at {output_filepath}. Error: {str(e)}"
