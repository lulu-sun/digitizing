# Assumptions:
# - consolidation folder contains:
#   - extracted_texts folder with all updated edited extracted_texts
#   - Page Assignments.xlsx with all updated completed tracking
#   - Above two files are in sync and agree with each other

from page_numbers import page_starts, new_testament_books, links
from google_cloud import get_page_assignments_as_df, download_docx_from_drive
from datetime import datetime
import pandas as pd
import docx
import re
import os
import shutil

working_dir = "consolidation"
input_dir = f"{working_dir}/input"
output_dir = f"{working_dir}/output"

xlsx_file = f'{input_dir}/Page Assignments.xlsx'

def get_file_path(volume, part, file_name):
    return f"{input_dir}/extracted_texts/Vol {volume} Part {part}/{file_name}"

def run_to_html(run):
    html = run.text
    if run.bold:
        html = f'<b>{html}</b>'
    if run.italic:
        html = f'<i>{html}</i>'
    if run.underline:
        html = f'<u>{html}</u>'
    return html

def download_docx(volume, part, page):
    link = links[(volume, part, page)]
    
    pattern = r"/document/d/([a-zA-Z0-9_-]+)"
    file_id = re.search(pattern, link).group(1)

    file_path = f"{input_dir}/extracted_texts/Vol {volume} Part {part}/extracted_text-{page}.docx"
    download_docx_from_drive(file_id, file_path)


def get_progress(df=pd.DataFrame()):
    if df.empty:
        df = get_page_assignments_as_df()
    
    return (df == "TRUE").sum().sum()


def convert_docx_to_html(redownload_docx=False):
    global PROGRESS
    # remove html output files
    html_output_folder = f'{output_dir}/html'
    if os.path.exists(html_output_folder):
        shutil.rmtree(html_output_folder)

    # remove input folder if redownloding.
    if redownload_docx and os.path.exists(input_dir):
        shutil.rmtree(input_dir)

    # Read the Excel file into a DataFrame
    df = get_page_assignments_as_df()
    # df = pd.read_excel(xlsx_file)
    # print(df)
    completed_count = get_progress(df)
    current = 0

    for volume, part in [(1,1),(1,2),(2,1),(2,2)]:
        starting_column = ((volume - 1) * 8 + (part - 1) * 4)
        dfvp = df.iloc[1:, starting_column:starting_column+3]

        condition = dfvp.iloc[:, 2] == "TRUE"

        dfvp_completed = dfvp[condition]

        for index, row in dfvp_completed.iterrows():
            current += 1
            file_name = row[starting_column]            
            page_number = int(re.search(r'\d+', file_name).group(0))
            editor = row[starting_column + 1]
            completed = row[starting_column + 2]
            docx_file_path = get_file_path(volume, part, file_name)
            
            print(f"{current}/{completed_count} Volume {volume} Part {part}", page_number, editor, completed, docx_file_path)

            formatted_html = []

            if redownload_docx:
                download_docx(volume, part, page_number)

            if not os.path.exists(docx_file_path):
                print("File not found. You may need to redownload. Skipping.")
                continue
            doc = docx.Document(docx_file_path)

            # if volume == 1 and part == 2 and  page_number == 68:
            #     input([doc.paragraphs[0].runs[0]])

            for i, paragraph in enumerate(doc.paragraphs):
                for run in paragraph.runs:
                    formatted_html.append(run_to_html(run))

                if i == 0: # at the top of the document, if there is just one empty line, that still counts as two newlines.
                    formatted_html.append('\n')
                formatted_html.append('\n')

            formatted_html = ''.join(formatted_html)
            formatted_html = formatted_html.rstrip()
            formatted_html = re.sub(r'\n\n\n\n', '\n\n', formatted_html)
            formatted_html = re.sub(r'\n\n\n', '\n\n', formatted_html)
            formatted_html = re.sub(r'\n\n', '<br><br>', formatted_html)
            formatted_html = re.sub(r'\s+', ' ', formatted_html)
            formatted_html = re.sub(r'</b><b>', '', formatted_html)
            formatted_html = re.sub(r'</i><i>', '', formatted_html)
            formatted_html = re.sub(r'</u><u>', '', formatted_html)
            
            output_file_path = f'{output_dir}/html/Vol {volume} Part {part}/{page_number}.html'

            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            with open(output_file_path, 'w') as f:
                f.write(formatted_html)


def process_html(html_text):
    pattern = r'<br><br>([^<>\[\]]*(?:(?!<br>|\[|\]).)*\])'
    result = re.split(pattern, html_text)

    output_text = []

    for i, block in enumerate(result):
        # block = re.sub(r'<.*>', str(block))
        if i % 2 == 1:
            if "CHAP" in block:
                h = 1
            elif re.search(r'\d+.', block):
                h = 2
            else:
                h = 3
            output_text.append(f'<h{h}><u>{block}</u></h{h}>')
        else:
            output_text.append(block)

    return ''.join(output_text)


def convert_html_to_verses():
    print("Processing html files...")
    all_text = []

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%B %d, %Y at %I:%M%p")
    all_text.append(f"<h3>This file was generated on {formatted_datetime}</h3>")

    completed_count = get_progress()
    all_text.append(f"<h3>PROGRESS: {completed_count}/1941 = {round(100 * completed_count / 1941, 2)}%</h3>")

    for book in new_testament_books:
        volume, part, first_page, last_page = page_starts[book]

        all_text.append(f"<h1>Book: {book}</h1>")

        first_missing_page = last_missing_page = -1

        for page in range(first_page, last_page + 1):
            # print(book, volume, part, curr_page)
            html_file_path = f'{output_dir}/html/Vol {volume} Part {part}/{page}.html'

            if os.path.exists(html_file_path):
                if first_missing_page != -1:
                    all_text.append(f"<h2>MISSING PAGES: Volume {volume}, Part {part}, {book}, Pages {first_missing_page}-{last_missing_page} missing.</h2>")
                    first_missing_page = last_missing_page = -1

                all_text.append(f'<h3><a href="{links[(volume, part, page)]}" target="_blank">DOCX LINK: Volume {volume}, Part {part}, Page {page}:</a></h3>')

                # Identify tags in html
                html_text = open(html_file_path, 'r').read()
                processed_html = process_html(html_text)
                all_text.append(processed_html)
                
            else:
                if first_missing_page == -1:
                    first_missing_page = last_missing_page = page
                else:
                    last_missing_page = page

        if first_missing_page != -1:
            all_text.append(f"<h2>MISSING PAGES: Volume {volume}, Part {part}, {book}, Pages {first_missing_page}-{last_missing_page} missing.</h2>")

    final_text = '<br>'.join(all_text)

    print("Writing final output...")

    with open(f'{output_dir}/test.html', 'w') as f:
        f.write(''.join(final_text))

    print("Done.")

    return final_text
    

if __name__ == '__main__':
    convert_docx_to_html(redownload_docx=True)
    convert_html_to_verses()