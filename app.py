from flask import Flask, render_template, request
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
import os
import html

load_dotenv()

app = Flask(__name__, template_folder="templates")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    uploaded_file = request.files.get("report")

    if not uploaded_file:
        return "Please upload a report."

    filename = uploaded_file.filename

    # --------------------------------
    # READ TXT FILE
    # --------------------------------

    if filename.lower().endswith(".txt"):

        try:
            report_text = uploaded_file.read().decode("utf-8")
        except Exception:
            return """
            <h2>Unable to read the TXT file.</h2>
            <p>Please upload a valid text file.</p>
            """

    # --------------------------------
    # READ PDF FILE
    # --------------------------------

    elif filename.lower().endswith(".pdf"):

        try:

            pdf_reader = PdfReader(uploaded_file)

            report_text = ""

            for page in pdf_reader.pages:

                page_text = page.extract_text()

                if page_text:
                    report_text += page_text + "\n"

        except Exception as e:

            print("PDF Error:", e)

            return """
            <h2>Unable to read the PDF.</h2>
            <p>Please upload another PDF containing readable text.</p>
            """

    else:

        return """
        <h2>Unsupported file format</h2>
        <p>Please upload a PDF or TXT healthcare report.</p>
        """

    # --------------------------------
    # CHECK CONTENT
    # --------------------------------

    if not report_text.strip():

        return """
        <h2>No readable information found</h2>
        <p>Please upload a PDF or TXT file containing readable text.</p>
        """

    # --------------------------------
    # AI PROMPT
    # --------------------------------

    prompt = f"""
You are an AI healthcare report information assistant.

Your task is to help a user understand the information written
in a healthcare report using simple and easy-to-understand language.

Analyze ONLY the information provided in the report.

Return the response in exactly these sections:

1. SIMPLE SUMMARY

Give a short explanation of what the report contains.

2. IMPORTANT INFORMATION

List the important measurements, observations, or information
mentioned in the report.

For each measurement, explain what the measurement represents
in simple language.

Do NOT decide whether a result is normal or abnormal unless
the report itself explicitly provides that interpretation.

3. QUESTIONS TO ASK A HEALTHCARE PROFESSIONAL

Provide 3 to 5 useful questions that the user could discuss
with a qualified healthcare professional.

SAFETY RULES:

- Do not diagnose diseases.
- Do not recommend medicines.
- Do not recommend treatments.
- Do not provide medical conclusions.
- Do not create information that is not present in the report.
- Clearly state that the information is educational only.

Healthcare report:

{report_text}
"""

    # --------------------------------
    # GEMINI AI
    # --------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        ai_analysis = response.text

    except Exception as e:

        print("Gemini API Error:", e)

        return """
        <!DOCTYPE html>

        <html>

        <head>

            <title>AI Service Busy</title>

            <style>

                body {
                    margin: 0;
                    font-family: Arial, sans-serif;
                    background: #f5f8fb;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                }

                .box {
                    background: white;
                    width: 90%;
                    max-width: 600px;
                    padding: 45px;
                    border-radius: 24px;
                    text-align: center;
                    box-shadow: 0 15px 40px rgba(0,0,0,0.08);
                }

                h1 {
                    color: #315c72;
                }

                p {
                    color: #667085;
                    line-height: 1.7;
                }

                a {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 13px 24px;
                    background: #3b82a0;
                    color: white;
                    text-decoration: none;
                    border-radius: 10px;
                }

            </style>

        </head>

        <body>

            <div class="box">

                <h1>AI Service Temporarily Unavailable</h1>

                <p>
                    The AI service has temporarily reached its request limit.
                    Please wait a little while and try again.
                </p>

                <a href="/">
                    Return to Analyzer
                </a>

            </div>

        </body>

        </html>
        """

    # --------------------------------
    # SAFELY DISPLAY AI RESULT
    # --------------------------------

    safe_analysis = html.escape(ai_analysis)

    # --------------------------------
    # PROFESSIONAL RESULT PAGE
    # --------------------------------

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Analysis Results | AI Healthcare Assistant</title>

        <style>

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: Arial, Helvetica, sans-serif;
                background: #f4f8fb;
                color: #243746;
            }}

            /* HEADER */

            .topbar {{
                background: white;
                border-bottom: 1px solid #e6edf2;
                padding: 18px 7%;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}

            .brand {{
                display: flex;
                align-items: center;
                gap: 12px;
                font-weight: bold;
                color: #245b70;
                font-size: 18px;
            }}

            .brand-icon {{
                width: 42px;
                height: 42px;
                border-radius: 12px;
                background: #e4f3f7;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 21px;
            }}

            .status {{
                background: #e9f8f2;
                color: #16815e;
                padding: 8px 13px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: bold;
            }}

            /* MAIN */

            .container {{
                width: 90%;
                max-width: 1000px;
                margin: 45px auto;
            }}

            .hero {{
                text-align: center;
                margin-bottom: 35px;
            }}

            .hero h1 {{
                font-size: 36px;
                margin-bottom: 10px;
                color: #234b5d;
            }}

            .hero p {{
                color: #6c7b86;
                font-size: 16px;
            }}

            /* FILE CARD */

            .file-card {{
                background: white;
                border-radius: 20px;
                padding: 22px 26px;
                display: flex;
                align-items: center;
                gap: 18px;
                border: 1px solid #e4ebef;
                margin-bottom: 25px;
            }}

            .file-icon {{
                width: 52px;
                height: 52px;
                background: #eef6f8;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 25px;
            }}

            .file-info {{
                flex: 1;
            }}

            .file-info h3 {{
                margin: 0 0 5px;
                color: #2c4857;
                font-size: 16px;
            }}

            .file-info p {{
                margin: 0;
                color: #83909a;
                font-size: 13px;
            }}

            .processed {{
                color: #16815e;
                font-size: 13px;
                font-weight: bold;
            }}

            /* AI RESULT */

            .result-card {{
                background: white;
                border-radius: 24px;
                padding: 35px;
                border: 1px solid #e4ebef;
                box-shadow: 0 12px 35px rgba(30,70,90,0.06);
            }}

            .result-heading {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 25px;
            }}

            .ai-icon {{
                width: 46px;
                height: 46px;
                background: #e8f4f7;
                border-radius: 13px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 22px;
            }}

            .result-heading h2 {{
                margin: 0;
                color: #244b5d;
                font-size: 23px;
            }}

            .result-heading p {{
                margin: 4px 0 0;
                color: #87939c;
                font-size: 13px;
            }}

            .analysis {{
                background: #f8fafb;
                border: 1px solid #e7edf0;
                border-radius: 18px;
                padding: 28px;
                white-space: pre-wrap;
                line-height: 1.75;
                color: #394c58;
                font-size: 15px;
            }}

            /* DISCLAIMER */

            .disclaimer {{
                margin-top: 25px;
                padding: 20px;
                border-radius: 16px;
                background: #fff8e7;
                border: 1px solid #f0dfad;
                color: #705c22;
                line-height: 1.6;
                font-size: 13px;
            }}

            .disclaimer strong {{
                color: #5d4b17;
            }}

            /* BUTTONS */

            .actions {{
                display: flex;
                gap: 14px;
                margin-top: 28px;
            }}

            .button {{
                flex: 1;
                text-align: center;
                padding: 14px 20px;
                border-radius: 12px;
                text-decoration: none;
                font-weight: bold;
                font-size: 14px;
            }}

            .primary {{
                background: #3d819b;
                color: white;
            }}

            .secondary {{
                background: #eef4f6;
                color: #365565;
            }}

            /* FOOTER */

            footer {{
                text-align: center;
                color: #89959d;
                font-size: 12px;
                padding: 30px 0;
            }}

            /* MOBILE */

            @media (max-width: 650px) {{

                .topbar {{
                    padding: 15px 5%;
                }}

                .status {{
                    display: none;
                }}

                .container {{
                    width: 92%;
                    margin: 30px auto;
                }}

                .hero h1 {{
                    font-size: 28px;
                }}

                .result-card {{
                    padding: 22px;
                }}

                .file-card {{
                    padding: 18px;
                }}

                .actions {{
                    flex-direction: column;
                }}

            }}

        </style>

    </head>


    <body>


        <!-- HEADER -->

        <div class="topbar">

            <div class="brand">

                <div class="brand-icon">
                    🩺
                </div>

                AI Healthcare Assistant

            </div>

            <div class="status">
                ✓ Analysis Completed
            </div>

        </div>


        <!-- MAIN -->

        <div class="container">


            <div class="hero">

                <h1>
                    Your Report, Explained Simply
                </h1>

                <p>
                    AI-generated information to help you understand
                    the contents of your healthcare report.
                </p>

            </div>


            <!-- FILE INFORMATION -->

            <div class="file-card">

                <div class="file-icon">
                    📄
                </div>

                <div class="file-info">

                    <h3>
                        {filename}
                    </h3>

                    <p>
                        Healthcare report successfully processed
                    </p>

                </div>

                <div class="processed">
                    ✓ Processed
                </div>

            </div>


            <!-- AI RESULT -->

            <div class="result-card">

                <div class="result-heading">

                    <div class="ai-icon">
                        ✨
                    </div>

                    <div>

                        <h2>
                            AI Report Analysis
                        </h2>

                        <p>
                            Easy-to-understand explanation
                        </p>

                    </div>

                </div>


                <div class="analysis">
{safe_analysis}
                </div>


                <!-- DISCLAIMER -->

                <div class="disclaimer">

                    <strong>
                        ⚠ Important Medical Disclaimer
                    </strong>

                    <br><br>

                    This AI tool is designed for educational and
                    informational purposes only. It does not provide
                    medical diagnosis, medical advice, or treatment
                    recommendations.

                    <br><br>

                    Please consult a qualified healthcare professional
                    for interpretation of your personal health results
                    and any medical decisions.

                </div>


                <!-- ACTIONS -->

                <div class="actions">

                    <a href="/" class="button primary">
                        ↩ Analyze Another Report
                    </a>

                    <a href="/" class="button secondary">
                        🏠 Back to Home
                    </a>

                </div>


            </div>


            <footer>

                AI Healthcare Assistant
                • AI-powered information support
                • Not a medical diagnosis tool

            </footer>


        </div>


    </body>

    </html>
    """


if __name__ == "__main__":

    app.run(debug=True)
