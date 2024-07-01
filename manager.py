import json
import requests
from scrapy.crawler import CrawlerProcess
from doc_analyzer_scrapy.doc_analyzer_scrapy.spiders.about_spider import AboutSpider
from doc_analyzer_scrapy.doc_analyzer_scrapy.spiders.conference_spider import ConferenceSpider
from collector import CollectorApp
import tkinter as tk
from tkinter import messagebox
from openai_agent import send_to_openai
from content_manager import ContentManager
import os
import time
from fpdf import FPDF

class Manager:
    def __init__(self):
        self.data = None
        self.start_time = None

    def run_collector(self):
        root = tk.Tk()
        app = CollectorApp(root)
        root.mainloop()
        self.data = app.get_data()
        if self.data:
            print(f'Data collected: {self.data}')
        else:
            print('No data collected.')

    def validate_links(self):
        invalid_links = []
        for link in [self.data.get('research_link'), self.data.get('journal_link')]:
            if link and not self.check_link_validity(link):
                invalid_links.append(link)
        return invalid_links

    def check_link_validity(self, link):
        try:
            response = requests.head(link, allow_redirects=True, timeout=5)
            print(response)
            return response.status_code == 200 or response.status_code == 403 or response.status_code == 418
        except requests.RequestException as e:
            print(f"Error checking link {link}: {e}")
            return False

    def run_spider(self):
        if not self.data:
            print("No data available to run spider.")
            return

        self.start_time = time.time()

        invalid_links = self.validate_links()
        if invalid_links:
            print(f"Invalid links: {invalid_links}")
            self.show_invalid_links(invalid_links)
            return

        process = CrawlerProcess()
        if self.data['type'] == 'Conferencia':
            if os.path.exists('conference_results.txt'):
                os.remove('conference_results.txt')
            process.crawl(ConferenceSpider, conference_name=self.data['conference_name'])
        elif self.data['type'] == 'Revista':
            if os.path.exists('about_paragraphs.txt'):
                os.remove('about_paragraphs.txt')
            start_urls = [self.data['journal_link']]
            process.crawl(AboutSpider, start_urls=start_urls)

        process.start()

        if self.data['type'] == 'Conferencia':
            content_file = 'conference_results.txt'
        elif self.data['type'] == 'Revista':
            content_file = 'about_results.txt'
        else:
            print("Unknown type, unable to proceed.")
            return

        with open(content_file, 'r', encoding='utf-8') as f:
            files_content = f.read()

        manager = ContentManager(".")
        truncated_content = manager.truncate_content(files_content, 9000)

        title = self.data.get('title', 'No Title')
        url = self.data.get('research_link')
        journal_url = self.data.get('journal_link') if self.data['type'] == 'Revista' else None
        publication_type = self.data['type']

        report = send_to_openai(truncated_content, title, url, journal_url, publication_type)
        print(report)
        self.show_report(report)

    def show_invalid_links(self, invalid_links):
        def close_all():
            for widget in root.winfo_children():
                widget.destroy()
            root.quit()
        
        root = tk.Tk()
        root.title("Links inválidos")
        msg = tk.Message(root, text=f"Invalid links found: {', '.join(invalid_links)}", width=400)
        msg.pack()
        ok_button = tk.Button(root, text="OK", command=close_all)
        ok_button.pack()
        root.mainloop()

    def show_report(self, report):
        elapsed_time = time.time() - self.start_time
        root = tk.Tk()
        root.title("Reporte Generado")

        msg = tk.Message(root, text=report, width=800)
        msg.pack()

        def generate_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, report)
            pdf_path = "report.pdf"
            pdf.output(pdf_path)
            messagebox.showinfo("PDF Generado", f"El PDF ha sido guardado en {os.path.abspath(pdf_path)}")
            root.quit()

        def close():
            root.quit()

        time_label = tk.Label(root, text=f"Tiempo transcurrido: {elapsed_time:.2f} segundos")
        time_label.pack()

        ok_button = tk.Button(root, text="OK", command=close)
        ok_button.pack()

        pdf_button = tk.Button(root, text="Generar PDF", command=generate_pdf)
        pdf_button.pack()

        root.mainloop()

if __name__ == "__main__":
    manager = Manager()
    manager.run_collector()
    manager.run_spider()
