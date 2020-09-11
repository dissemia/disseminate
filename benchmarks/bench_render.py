"""
Test and benchmark the render performance.
"""
import random
import tempfile
import os
import shutil
import pathlib

from disseminate.document import Document
from disseminate.builders.environment import Environment


dummy_text = """This is my dummy text. It has a few sentences that can be used.
to generate dummy paragraphs and repeat words."""
words = dummy_text.split()


class Suite:

    count = 50  # number of chapters
    word_count = 10000  # number of words per chapter

    def setup(self):
        # create a tmpdir
        self.tmpdir = tempfile.mkdtemp()
        self.tgt_path = pathlib.Path(self.tmpdir)
        self.src_path = pathlib.Path(os.path.join(self.tmpdir, 'src'))
        os.mkdir(self.src_path)

        # Create the chapters and main file
        # Create 50 chapters
        self.root_filepath = os.path.join(self.src_path, 'main.dm')
        chapter_filenames = []
        total_word_count = 0
        for i in range(self.count):
            chapter_filename = 'chapter-' + str(i) + '.dm'
            chapter_filenames.append(chapter_filename)

            remaining_words = self.word_count
            text = ("---\n"
                    "toc: all headings collapsed\n"
                    "---\n")
            text += "@chapter{{{}}}\n".format(i)
            while remaining_words > 0:
                # Add a paragraph.
                text += " ".join([random.choice(words) for i in range(150)])
                text += "\n\n"
                remaining_words -= 150
                total_word_count += 150

            chapter_filepath = os.path.join(self.src_path, chapter_filename)
            with open(chapter_filepath, 'w') as f:
                f.write(text)

        # Create the root document

        with open(self.root_filepath, 'w') as f:
            f.write("""
        ---
        targets: html, tex
        toc: all headings expanded
        include:
          {}
        ---
        """.format("\n          ".join(chapter_filenames)))

        # Load the document
        envs = Environment.create_environments(root_path=self.src_path, target_root=self.tgt_path)
        self.env = envs[0]
        self.doc = self.env.root_document

    def teardown(self):
        # Cleanup tmpdir
        shutil.rmtree(self.tmpdir)

    def time_load_independent_files(self):
        """Benchmark the render performance of independent files."""
        # Load the document
        doc = self.doc
        doc.load()

    def time_render_independent_files_html(self):
        """Benchmark the render performance of independent files."""
        # Render the file
        targets = {k: v for k, v in self.doc.targets.items() if k == '.html'}
        self.doc.build()

    def time_render_independent_files_tex(self):
        """Benchmark the render performance of independent files."""
        # Render the file
        targets = {k: v for k, v in self.doc.targets.items() if k == '.tex'}
        self.doc.build()
