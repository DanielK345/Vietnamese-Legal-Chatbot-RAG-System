import os

import google.generativeai as genai

# Configure and load the model
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
summarizer_model = genai.GenerativeModel("gemini-2.0-flash")


def summarize_text(text):
    # prepare template for prompt
    template = """You are a very good assistant that summarizes text.

    Always keep important key points in the summary.

    ==================
    {text}
    ==================

    Write a summary of the content in Vietnamese.
    """

    prompt = template.format(text=text)

    response = summarizer_model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0),
    )
    return response.text
