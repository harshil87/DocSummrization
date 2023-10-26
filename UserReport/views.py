from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import SummaryData
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
from transformers import pipeline
import warnings
import pytextrank
from PyPDF2 import PdfReader
import docx2txt
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.core.mail import EmailMessage
from django.conf import settings


warnings.filterwarnings("ignore")


def calculate_sentence_scores(text, large_text_threshold=50000):
    # Load the English language model and add the TextRank component
    nlp = spacy.load("en_core_web_lg")
    nlp.add_pipe("textrank")

    # Process the input text with Spacy
    doc = nlp(text)

    # Define stopwords and initialize variables
    stop_words = list(STOP_WORDS)
    word_freq = {}
    max_freq = 0

    # Calculate word frequencies
    for word in doc:
        # Check if the word is not a stopword or punctuation
        if (
            word.text.lower().strip("\n") not in stop_words
            and word.text.lower() not in punctuation
        ):
            # Update word frequency
            word_freq[word.text] = word_freq.get(word.text, 0) + 1
            # Track the maximum frequency
            if word_freq[word.text] > max_freq:
                max_freq = word_freq[word.text]

    # Normalize word frequencies
    word_freq = {
        key: value / max_freq for key, value in word_freq.items() if key != "\n"
    }

    # Extract sentences from the processed text
    sent_tokens = [sent for sent in doc.sents]

    # Calculate sentence scores using word frequencies
    sent_scores = {}
    for sent in sent_tokens:
        for word in sent:
            if word.text in word_freq:
                # Update sentence score
                sent_scores[sent] = sent_scores.get(sent, 0) + word_freq[word.text]

    # Determine the summary length based on the length of the input text
    lenT = len(text)
    # print(lenT)
    if lenT > large_text_threshold and lenT < 500000:
        select_len = int(len(sent_tokens) * 0.005)

    elif lenT > 500000:
        select_len = int(len(sent_tokens) * 0.001)
    elif lenT > 30000 and lenT < 50000:
        select_len = int(len(sent_tokens) * 0.02)

    else:
        select_len = int(len(sent_tokens) * 0.05)

    # Generate the sentence summary
    summary = nlargest(select_len, sent_scores, key=sent_scores.get)
    final_summary = [word.text.replace("\n", "") for word in summary]
    summary = " ".join(final_summary)

    return summary


def abstractive(sentence_scores):
    text_example = sentence_scores
    model_path = "D:\\DocSummarization\\distilbart-cnn-12-6"
    summarizer = pipeline("summarization", model=model_path)
    AblenT = len(text_example)

    if AblenT > 1000:
        summary = summarizer(text_example, min_length=300, max_length=AblenT)
    elif 100 < AblenT < 400:
        summary = summarizer(text_example, min_length=150, max_length=AblenT)
    else:
        # Default summarization settings if the length doesn't match the above conditions
        summary = summarizer(text_example, min_length=200, max_length=AblenT)

    return summary[0]["summary_text"]


def home(request):
    files = SummaryData.objects.all()
    return render(request, "index.html", {"files": files})


def aboutus(request):
    return render(
        request,
        "aboutus.html"
    )



def download_file(request, id):
    summarized_data = SummaryData.objects.get(id=id)
    summary_text = summarized_data.summary

    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{summarized_data.file_name}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Add the summary text as a paragraph in the PDF
    paragraph = Paragraph(summary_text, styles["Normal"])
    story.append(paragraph)

    doc.build(story)

    return response


def document_upload(request):
    if request.method == "POST":
        try:
            uploaded_files = request.FILES.getlist("fileinput")
            upload_date = datetime.now() + timedelta(hours=5)
            email_address = request.POST.get('email')
            
            pdf_attachments = []

            for file in uploaded_files:
                # extract pdf

                file_name = file.name
                print(f"\nextract text from {file_name}")
                if file_name.endswith(".pdf"):
                    text = extract_text_from_pdf(file)
                elif file_name.endswith(".docx"):
                    text = extract_text_from_word(file)
                else:
                    text = "Unsupported file format"

                # ml

                print(f"summrize the {file_name}....")

                text_input = text
                extractive = calculate_sentence_scores(text_input)
                summary = abstractive(extractive)
                print(f"summrized file {file_name}")

                # save data

                summarized_data = SummaryData(
                    file_name=file_name, upload_date=upload_date, summary=summary
                )
                summarized_data.save()

                # generate the pdf 

                response = HttpResponse(content_type="application/pdf")
                response["Content-Disposition"] = f'attachment; filename="{summarized_data.file_name}.pdf"'

                doc = SimpleDocTemplate(response, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []

                # Add summary in pdf
                paragraph = Paragraph(summarized_data.summary, styles["Normal"])
                story.append(paragraph)

                doc.build(story)

                pdf_attachments.append((f"{summarized_data.file_name}.pdf", response.content))

            # Email send
            
            if pdf_attachments:
                subject = 'File Summaries'
                message = "Summarized PDF's"
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email_address]
                email = EmailMessage(subject, message, from_email, recipient_list)

                for pdf_filename, pdf_data in pdf_attachments:
                    email.attach(pdf_filename, pdf_data, "application/pdf")

                email.send()
            
            return redirect("home")

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return HttpResponse(error_message)

    return redirect("home")


def extract_text_from_pdf(file):
    pdf_text = ""
    try:
        pdf_reader = PdfReader(file)

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text()

    except Exception as e:
        error_message = f"Failed to extract text from PDF: {str(e)}"
        return error_message

    return pdf_text


def extract_text_from_word(file):
    text = docx2txt.process(file)

    return text
