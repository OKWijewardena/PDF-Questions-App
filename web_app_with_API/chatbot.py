from flask import Flask, render_template, request, Response
import openai
from werkzeug.utils import secure_filename
import fitz
import pdfkit  # Import pdfkit

app = Flask(__name__)

# Set your OpenAI API key here
openai.api_key = "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"

# Define a list to store PDF information
pdf_data = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        # Save the uploaded PDF to a folder or process it as needed
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(filename)

        # Convert PDF to text and store relevant information using PyMuPDF
        text = extract_text_with_pymupdf(filename)  # Define this function
        pdf_info = {
            'filename': filename,
            'text': text
        }
        pdf_data.append(pdf_info)

        return "File uploaded successfully"

    return "No file uploaded"

def extract_text_with_pymupdf(pdf_filename):
    text = ""
    doc = fitz.open(pdf_filename)
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

@app.route('/ask', methods=['POST'])
def ask_question():
    user_questions = request.form['questions'].split('\n')  # Split questions by newlines
    
    # Retrieve the relevant PDF text from your local database
    relevant_text = ""
    for pdf_info in pdf_data:
        relevant_text += pdf_info['text']
    
    # Use GPT-4 to generate answers for each question separately
    responses = []
    for i, user_question in enumerate(user_questions):
        if user_question.strip():  # Check if the question is not empty
            prompt = f"Question {i + 1}: {user_question}\nText: {relevant_text}"
            response = openai.Completion.create(
                engine="text-davinci-002",  # Use the appropriate GPT-4 engine
                prompt=prompt,
                max_tokens=300  # Adjust the max_tokens as needed
            )
            answer = response.choices[0].text.strip()
            responses.append((user_question, answer))
    
    return render_template('index.html', responses=responses)

@app.route('/download', methods=['POST'])
def download_pdf():
    # Get the responses from the form data
    responses = request.form.getlist('responses')

    # Create a PDF from the responses using pdfkit
    pdfkit.from_string('\n'.join(responses), 'output.pdf')

    # Serve the PDF file as a downloadable response
    with open('output.pdf', 'rb') as pdf_file:
        response = Response(pdf_file.read(), content_type='application/pdf')
        response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'
        return response

if __name__ == '__main__':
    app.run(debug=True)
