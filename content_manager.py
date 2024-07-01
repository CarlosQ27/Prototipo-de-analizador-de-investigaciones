import os

class ContentManager:
    def __init__(self, directory):
        self.directory = directory

    def load_files(self):
        content = ""
        for filename in os.listdir(self.directory):
            if filename.endswith(".txt"):
                with open(os.path.join(self.directory, filename), 'r', encoding='utf-8') as file:
                    content += file.read() + "\n"
        return content

    def truncate_content(self, content, max_words):
        words = content.split()
        truncated_content = " ".join(words[:max_words])
        return truncated_content
