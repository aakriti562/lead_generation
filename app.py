from flask import Flask, render_template, request, send_file , make_response , Response
import cohere
import re 
import pdfkit
import io , os , tempfile , shutil
from fpdf import FPDF
from html.parser import HTMLParser
from bs4 import BeautifulSoup

app = Flask(__name__)

# Replace 'your-api-key' with your actual Cohere API key
cohere_client = cohere.Client('6i8Z6zqJIO2Bk92mavh8MGdwO2zENVctV71jM75K')

def create_prompt(data):
    prompt = (f"You are an expert in {data['strategyType']}. "
              f"Here is the business information:\n"
              f"Company: {data['companyDescription']} (Niche: {data['companyNiche']})\n"
              f"Average Sales: {data['avgSales']} INR, Sales Unit: {data['salesUnit']}\n"
              f"Instagram Followers: {data['instaFollowers']}, LinkedIn Followers: {data['linkedinFollowers']}, Twitter Followers: {data['twitterFollowers']}\n"
              f"Target Clients: {data['targetClients']}\n"
              f"Average Ad Budget: {data['avgAdBudget']} INR, Return on Ads: {data['returnOnAds']}%\n\n"
              f"Generate a comprehensive {data['strategyType']} based on this information.")
    return prompt

def generate_content(prompt):
    try:
        # Call Cohere's generate endpoint
        response = cohere_client.generate(
            model='command-xlarge-nightly',  # or use 'command-xlarge' or another model
            prompt=prompt,
            max_tokens=800,
            temperature=0.7
        )
        return response.generations[0].text
    except Exception as e:
        return f"An error occurred while generating content: {str(e)}"

def format_bold_headings(text):
    """
    This function wraps bullet points and headings in <strong> tags to make them bold.
    It identifies headings like '- ', '1. ', etc.
    """
    text = re.sub(r'(^\d+\.\s)', r'<strong>\1</strong>', text, flags=re.MULTILINE)  # For numbered lists
    text = re.sub(r'(^[-•]\s)', r'<strong>\1</strong>', text, flags=re.MULTILINE)    # For bullet points

    # Make text between ** bold by replacing **text** with <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    return text   

def is_text_complete(text):
    # Check if the text ends with proper punctuation
    return text.endswith(('.', '!', '?'))

def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)

    # Create a temporary file to save the PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_output_path = temp_file.name
    pdf.output(pdf_output_path)
    temp_file.close()  # Close the file so it can be accessed by send_file
    
    return pdf_output_path

def strip_html_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    form_data = {
        'strategyType': request.form['strategyType'],
        'avgSales': request.form['avgSales'],
        'salesUnit': request.form['salesUnit'],
        'instaFollowers': request.form['instaFollowers'],
        'linkedinFollowers': request.form['linkedinFollowers'],
        'twitterFollowers': request.form['twitterFollowers'],
        'companyDescription': request.form['companyDescription'],
        'companyNiche': request.form['companyNiche'],
        'targetClients': request.form['targetClients'],
        'avgAdBudget': request.form['avgAdBudget'],
        'returnOnAds': request.form['returnOnAds']
    }

    prompt = create_prompt(form_data)
    generated_content = generate_content(prompt)

    if is_text_complete(generated_content):
        # Apply bold formatting to headings and **text** before rendering
        formatted_content = format_bold_headings(generated_content)
    else:
        # If the content is incomplete, set formatted_content to an empty string or a default message
        formatted_content = ""
    
    formatted_content = format_bold_headings(generated_content)

    return render_template('result.html', generated_content=formatted_content)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    content = request.form.get('generated_content')
    if not content:
        return "No content provided", 400  # Return a 400 error if no content is provided

    # Strip HTML tags
    content = strip_html_tags(content)

    # Create PDF content
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Split the content by points to add new lines
    lines = content.split('\n')  # Assuming points are separated by new lines
    
    for line in lines:
        pdf.multi_cell(0, 10, line)
        pdf.ln()  # Add a new line after each point

    # Output PDF to a byte string
    pdf_output = pdf.output(dest='S').encode('latin1')  # Use 'latin1' to ensure compatibility

    # Create a Response object with the PDF byte string
    response = Response(pdf_output, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=generated_content.pdf'

    return response

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
