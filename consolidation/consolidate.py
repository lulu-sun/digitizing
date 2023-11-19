# Assumptions:
# - consolidation folder contains:
#   - extracted_texts folder with all updated edited extracted_texts
#   - Page Assignments.xlsx with all updated completed tracking
#   - Above two files are in sync and agree with each other

from page_numbers import page_starts, new_testament_books, links
from google_cloud import get_page_assignments_as_df, download_docx_from_drive
from format_text import format_text
from datetime import datetime
from html_to_docx import convert_html_to_docx
import pandas as pd
import docx
import re
import os
import shutil
import time

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

def get_detailed_progress():
    df = get_page_assignments_as_df()

    counts = {}

    for volume, part in [(1,1),(1,2),(2,1),(2,2)]:
        starting_column = ((volume - 1) * 8 + (part - 1) * 4)
        dfvp = df.iloc[1:, starting_column:starting_column+3]

        condition = dfvp.iloc[:, 2] == "TRUE"

        dfvp_completed = dfvp[condition]

        for index, row in dfvp_completed.iterrows():
            file_name = row[starting_column]            
            page_number = int(re.search(r'\d+', file_name).group(0))
            editor = row[starting_column + 1]
            completed = row[starting_column + 2]
            docx_file_path = get_file_path(volume, part, file_name)

            if editor not in counts:
                counts[editor] = 1
            else:
                counts[editor] += 1

    print("---DETAILED SUMMARY---")
    print(f"{len(counts)} contributors completed {sum(counts.values())} revisions! {1941 - sum(counts.values())} left. {round(sum(counts.values()) * 100 / 1941, 2)}%")

    for editor, count in sorted(counts.items(), key=lambda pair: -pair[1]):
        print(editor, count)

    return counts


def get_all_runs_from_docx(redownload_docx=False):
     # remove input folder if redownloding.
    if redownload_docx and os.path.exists(input_dir):
        shutil.rmtree(input_dir)

    # Read the Excel file into a DataFrame
    df = get_page_assignments_as_df()
    # df = pd.read_excel(xlsx_file)
    # print(df)
    completed_count = get_progress(df)
    current = 0

    runs = {} # key: (volume, part, page)

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
            
            # print(f"{current}/{completed_count} Volume {volume} Part {part}", page_number, editor, completed, docx_file_path)

            if redownload_docx:
                download_docx(volume, part, page_number)

            if not os.path.exists(docx_file_path):
                print("File not found. You may need to redownload. Skipping.")
                continue
            doc = docx.Document(docx_file_path)

            if not (volume, part, page_number) in runs:
                runs[(volume, part, page_number)] = []

            for i, paragraph in enumerate(doc.paragraphs):
                for run in paragraph.runs:
                    runs[(volume, part, page_number)].append(run)
    
    return runs

# Steps:
# (Create an output at every step of the way so intermediate progress can be viewed.)
# 1. Compile and convert all docx into various html files.
# 2. Combine all html into single big html file.
# 3. Run text formatting and space normalization on the big html.
# 4. Convert processed big html into one big docx. 
# 5. Convert big docx into PDF.
def consolidate(redownload_docx=False):
    start_time = time.time()

    # 1. Compile and convert all docx into various html files.
    print("Converting each docx file into an html file...")
    convert_docx_to_html(redownload_docx)
    print(f"Done.")

    # 2. Combine all html into single big html file.
    print("Combining html files into one html file...")
    consolidate_html()
    print("Done.")

    # 3. Run text formatting and space normalization on the big html.
    print("Formatting and processing the big html file...")
    process_big_html()
    print("Done.")

    # 4. Convert processed big html into one big docx. 
    print("Converting bht html file into big docx file...")
    convert_big_html_to_docx()
    print("Done.")

    # 5. Convert big docx into PDF.

    print(f"That took {round((time.time() - start_time) / 60, 2)} minutes.")


def convert_big_html_to_docx():
    convert_html_to_docx(f'{output_dir}/alford-processed.html', f'{output_dir}/alford-processed.docx')


def convert_docx_to_html(redownload_docx=False):
    # remove html output files
    html_output_folder = f'{output_dir}/html'
    if os.path.exists(html_output_folder):
        shutil.rmtree(html_output_folder)

    runs = get_all_runs_from_docx(redownload_docx)

    for volume, part, page in runs.keys():
        formatted_html = []

        for i, run in enumerate(runs[(volume, part, page)]):
            formatted_html.append(run_to_html(run))

            if i == 0: # at the top of the document, if there is just one empty line, that still counts as two newlines.
                formatted_html.append('\n')
            formatted_html.append('\n')

        formatted_html = ''.join(formatted_html)
        formatted_html = copy_docx_formatting_to_html(formatted_html)
        
        output_file_path = f'{output_dir}/html/Vol {volume} Part {part}/{page}.html'

        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, 'w') as f:
            f.write(formatted_html)


def copy_docx_formatting_to_html(text):
    text = text.rstrip() # Remove any trailing whitespace.

    subs = [
        (r'\n\n\n+', '\n\n'), # Limit newlines to two.
        (r'\n\n', '<br><br>'), # Convert empty lines to br tags.
        (r'\s+', ' '), # Convert all other remaining continuous whitespace to a single space.
        (r'</b><b>', ''), # Remove shortened bold tags
        (r'</i><i>', ''), # Remove shortened italics tags
        (r'</u><u>', ''), # Remove shortened underline tags 
    ]

    for find, replace in subs:
        text = re.sub(find, replace, text)

    return text


def process_big_html():
    html_text = open(f'{output_dir}/alford.html', 'r').read()
    html_text = process_html(html_text)
    html_text = format_text(html_text)

    with open(f'{output_dir}/alford-processed.html', 'w') as output_file:
        output_file.write(html_text)

    return html_text


def process_html(html_text):
    pattern = r'<br><br>([^<>]*(?:(?!<br>|\[.*\]).)*?\])'
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

    output_text = ''.join(output_text)

    return output_text


def consolidate_html():
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
                # processed_html = process_html(html_text)
                all_text.append(html_text)
                
            else:
                if first_missing_page == -1:
                    first_missing_page = last_missing_page = page
                else:
                    last_missing_page = page

        if first_missing_page != -1:
            all_text.append(f"<h2>MISSING PAGES: Volume {volume}, Part {part}, {book}, Pages {first_missing_page}-{last_missing_page} missing.</h2>")

    final_text = '<br>'.join(all_text)

    # print("Writing final output...")

    with open(f'{output_dir}/alford.html', 'w') as f:
        f.write(''.join(final_text))

    # print("Done.")

    return final_text
    

if __name__ == '__main__':
    # convert_docx_to_html(redownload_docx=False)
    # convert_html_to_verses()
    # get_detailed_progress()

    # runs = get_all_runs_from_docx(redownload_docx=False)
    # print(len(runs))
    # print(list(r.text for r in runs[(1, 1, 68)]))

    consolidate(redownload_docx=False)