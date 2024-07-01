from openai import OpenAI
import os
from dotenv import load_dotenv
from content_manager import ContentManager

# Cargar la API key desde el archivo .env
load_dotenv()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()


def send_to_openai(content, title, url, journal_url, publication_type):
    if publication_type == 'Revista':
        messages = [
            {"role": "system", "content": "Eres un asistente altamente detallado. Tu trabajo es resumir, no trates de decir de qué se trata el artículo. Toma la información dada y solo te debes de encargar de resumilar y presentarla en el formato indicado. Presenta el link del artículo sin corchetes ni paréntesis por favor. NO hagas un resumen del artículo, es información que no conoces. Solo hay resumen del content que te pasen. Tampoco pon astericos por favor"},
            {"role": "user", "content": f"""
            Reporte del artículo: {title}\n
            Link al artículo: {url}\n
            Link a la página principal donde se publicó: {journal_url}\n
            Resumen de la información de la revista:
            {content}
            """}
        ] 
    else:
        messages = [
            {"role": "system", "content": "Eres un asistente altamente detallado. Tu trabajo es resumir, no inventes cosas ni trates de decir de qué se trata el artículo. Toma la información dada y solo te debes de encargar de resumilar y presentarla en el formato indicado. Presenta el link del artículo sin corchetes ni paréntesis por favor. NO hagas un resumen del artículo, es información que no conoces. Solo hay resumen del content que te pasen. Tampoco pon astericos por favor"},
            {"role": "user", "content": f"""
            Reporte del artículo: {title}\n
            Link al artículo: {url}\n

            Resumen de la información de la conferencia:
            {content}
            """}
        ]

    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages
    )
    print(completion.choices[0].message.content)

    return completion.choices[0].message.content

if __name__ == "__main__":
    manager = ContentManager(".")
    files_content = manager.load_files()
    truncated_content = manager.truncate_content(files_content, 6000)

    title = "Título de ejemplo"
    url = "https://ejemplo.com"
    journal_url = "https://ejemplo.com/revista"

    report = send_to_openai(truncated_content, title, url, journal_url, "Revista")
    print(report)
