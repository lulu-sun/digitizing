from new_testament_books import page_starts, books, links, book_chapters, book_formal_names
# from google_cloud import get_page_assignments_as_df, download_docx_from_drive
from format_text import format_text
from chap_finder import insert_chapters_from_to_file
# from parse_verse_commentary import parse_and_write_commentary
from datetime import datetime
from html_to_docx import convert_html_to_docx
from html_to_pdf import convert_html_to_pdf
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

def get_file_path(num):
    # filenames in pattern of: extracted_text-1.docx, etc
    return f"{input_dir}/extracted_texts/extracted_text-{num}.docx"

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


def get_all_html_from_docx(startNum, endNum):
   
    # completed_count = get_progress(df)
    current = 0

    all_htmls = {} # key: (volume, part, page)

    #         current += 1
    #         file_name = row[starting_column]            
    #         page_number = int(re.search(r'\d+', file_name).group(0))
    
    for num in range(startNum, endNum + 1):
        docx_file_path = get_file_path(num)
        print(f"num: {num}, filepath: {docx_file_path}")
            
            # print(f"{current}/{completed_count} Volume {volume} Part {part}", page_number, editor, completed, docx_file_path)
    # print(f"\r{current}/{completed_count}", end="")

        if not os.path.exists(docx_file_path):
            print("File not found. You may need to redownload. Skipping.")
            continue

        doc = docx.Document(docx_file_path)

        htmls = []

        for i, paragraph in enumerate(doc.paragraphs):
            htmls.append('\n')

            for j, run in enumerate(paragraph.runs):
                line = run_to_html(run)

                if line.isspace() and i == 0 and j == 0: # empty line at the top is treated as two newline chars.
                    htmls.append('\n')
                
                htmls.append(line)
        print(htmls)

        break

        # if volume == 1 and part == 1 and page_number == 228:
        #     print(htmls)
        #     input()

        # all_htmls[(volume, part, page_number)] = ''.join(htmls)

    print()
    
    return all_htmls

# Steps:
# (Create an output at every step of the way so intermediate progress can be viewed.)
# 1. Compile and convert all docx into various html files.
# 2. Combine all html into single big html file.
# 3. Run text formatting and space normalization on the big html.
# 4. Parse all book, chapter, verse information into new html.
# 5. Write everything to a nice formatted PDF.
def consolidate():
    start_time = time.time()

    # 1. Compile and convert all docx into various html files.
    print(f"Converting each docx file into an html file ...")
    convert_docx_to_html()
    print(f"Done.")

    # 2. Combine all html into single big html file.
    # print("Combining html files into one html file...")
    # consolidate_html(f'{output_dir}/2_alford.html')
    breakpoint

    # 3. Run text formatting and space normalization on the html.
    print("Formatting and processing the html file...")
    process_big_html(f'{output_dir}/2_alford.html', f'{output_dir}/3_alford-processed-with-verse-tags.html')

    # 3a. Keep a copy with custom verse tags. Consolidation continues without custom verse tags.
    remove_custom_verse_tags(f'{output_dir}/3_alford-processed-with-verse-tags.html', f'{output_dir}/3_alford-processed.html')
    remove_docx_links(f'{output_dir}/3_alford-processed-with-verse-tags.html', f'{output_dir}/3_alford-processed-with-verse-tags.html')

    # 3b. Generate Henry Alford verse-by-verse commentaries.
    print("Parsing commentary by verse sections (for BibleGo)...")
    parse_and_write_commentary(f'{output_dir}/3_alford-processed-with-verse-tags.html', f'{output_dir}/Henry Alford/')

    # 4. Parse all book, chapter, verse information into new html.
    print("Inserting chapter markers...")
    insert_chapters_from_to_file(f'{output_dir}/3_alford-processed.html', f'{output_dir}/4_alford-chap-inserted.html')

    # 4a. Copy final html to index.hml.
    print("Copying final html to index...")
    copy_and_rename_file(f'{output_dir}/4_alford-chap-inserted.html', '.', 'index.html', )

    # 4b. Remove docx links for PDF generation.
    print("Preparing final html for PDF generation...")
    remove_docx_links(f'{output_dir}/4_alford-chap-inserted.html', f'{output_dir}/4b_alford-pdf-gen.html')

    # 5. Write everything to a nice formatted PDF.
    print("Generating final PDF...")
    convert_html_to_pdf(f'{output_dir}/4b_alford-pdf-gen.html', f'{output_dir}/5_alford.pdf')
    copy_and_rename_file(f'{output_dir}/5_alford.pdf', '.', 'New Testament for English Readers - Henry Alford (DRAFT).pdf')

    print("All done!")

    print(f"That took {round((time.time() - start_time) / 60, 2)} minutes.")


def remove_docx_links(input_file_path, output_file_path):
    html_text = open(input_file_path, 'r').read()
    html_text = re.sub(r'<a href="([^"]+)" target="_blank"> \(DOCX LINK Volume \d, Part \d, Page \d+\)</a>', '', html_text)
    open(output_file_path, 'w').write(html_text)


def copy_and_rename_file(source_path, destination_directory, new_filename):
    try:
        # Copy the file to the destination directory
        shutil.copy(source_path, destination_directory)

        # Construct the new file path with the desired new filename
        destination_path = os.path.join(destination_directory, new_filename)

        # Rename the copied file to the new filename
        os.rename(os.path.join(destination_directory, os.path.basename(source_path)), destination_path)

        print(f"File '{source_path}' copied and renamed to '{destination_path}'.")
    except FileNotFoundError:
        print(f"Error: File '{source_path}' not found.")
    except PermissionError:
        print(f"Error: Permission denied. Check if you have the necessary permissions.")



# def convert_big_html_to_docx():
#     convert_html_to_docx(f'{output_dir}/alford-processed.html', f'{output_dir}/alford-processed.docx')


def convert_docx_to_html():
    # remove html output files
    html_output_folder = f'{output_dir}/html'
    if os.path.exists(html_output_folder):
        shutil.rmtree(html_output_folder)

    all_htmls = get_all_html_from_docx(8, 634)

    exit

    for volume, part, page in all_htmls.keys():
        html_text = all_htmls[(volume, part, page)]

        html_text = copy_docx_formatting_to_html(html_text)
        
        output_file_path = f'{output_dir}/html/Vol {volume} Part {part}/{page}.html'

        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, 'w') as f:
            f.write(html_text)


def copy_docx_formatting_to_html(text):
    text = text.rstrip() # Remove any trailing whitespace.

    subs = [
        (r'\n</b>\n', '</b>\n\n'),
        (r'\n</i>\n', '</i>\n\n'),
        (r'\n</u>\n', '</u>\n\n'),
        (r'<i>\s*\n\s*</i>', '\n'),
        (r'<b>\s*\n\s*</b>', '\n'),
        (r'<u>\s*\n\s*</u>', '\n'),
        (r'\n\n+', '<br><br>'), # Limit newlines to two and convert two or more to br tags
        (r'\s+', ' '), # Convert all other remaining continuous whitespace to a single space.
        (r'</b><b>', ''), # Remove shortened bold tags
        (r'</i><i>', ''), # Remove shortened italics tags
        (r'</u><u>', ''), # Remove shortened underline tags 
    ]

    for find, replace in subs:
        text = re.sub(find, replace, text)

    return text


def remove_custom_verse_tags(input_file_path, output_file_path):
    html_text = open(input_file_path).read()
    html_text = re.sub(r'{\d+}', ' ', html_text)
    html_text = re.sub(r'  ', ' ', html_text)
    open(output_file_path, 'w').write(html_text)


def process_big_html(input_file_path, output_file_path):
    html_text = open(input_file_path, 'r').read()
    # html_text = process_html(html_text)
    html_text = format_text(html_text)

    with open(output_file_path, 'w') as output_file:
        output_file.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The New Testament For English Readers</title>
    <style>
        @font-face { font-family: Caslon; font-weight: normal; font-style: normal; src: url('https://github.com/brotatotes/digitizing-alford/raw/main/consolidation/fonts/Adobe%20Caslon%20Pro%20Regular.ttf'); } 
        
        @font-face { font-family: Caslon; font-weight: bold; font-style: normal; src: url('https://github.com/brotatotes/digitizing-alford/raw/main/consolidation/fonts/Adobe%20Caslon%20Pro%20Bold.ttf');}
                          
        @font-face { font-family: Caslon; font-weight: normal; font-style: italic; src: url('https://github.com/brotatotes/digitizing-alford/raw/main/consolidation/fonts/Adobe%20Caslon%20Pro%20Italic.ttf');}
                          
        @font-face { font-family: Caslon; font-weight: bold; font-style: italic; src: url('https://github.com/brotatotes/digitizing-alford/raw/main/consolidation/fonts/Adobe%20Caslon%20Pro%20Bold%20Italic.ttf');}
                          
        @font-face { font-family: Caslon; font-variant: small-caps; src: url('https://github.com/brotatotes/digitizing-alford/raw/main/consolidation/fonts/Adobe%20Caslon%20Small%20Caps.otf');}

        /* Remove hyperlink color */
        a {
            color: inherit;
        }
                          
        body {
            font-family: 'Source Serif', serif;
            font-size: 12px;
        }
                          
        h1 {
            text-align: center;
            font-variant: small-caps;
        }
                          
        .cover-page {
            text-align: center;
            padding: 100px;
            font-variant: small-caps;
            font-size: 24px;
        }
                          
        @media print {
            .new-page {
                page-break-before: always;
            }
        }
                          
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th, td {
            text-align: center;
        }

        col {
            width: 50%; /* Set each column to be 50% of the table width */
        }
    </style>
</head>
<body>
""")
        output_file.write(html_text)

        output_file.write("</body></html>")

    return html_text


def process_html(html_text):
    pattern = r'<br><br>([^<>\[\]]*(?:(?!<br>|\[.*\]).)*?\])'
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


def consolidate_html(output_file_path):
    print("Processing html files...")
    all_text = []

    # current_datetime = datetime.now()
    # formatted_datetime = current_datetime.strftime("%B %d, %Y at %I:%M%p")
    # all_text.append(f"<h3>This file was generated on {formatted_datetime}</h3>")

    # completed_count = get_progress()
    # all_text.append(f"<h3>PROGRESS: {completed_count}/1941 = {round(100 * completed_count / 1941, 2)}%</h3>")

    all_text.append("<div class=\"cover-page\">")
    all_text.append("<h1>The New Testament For English Readers</h1>")
    all_text.append("<h2>a critical and explanatory commentary</h2>")
    all_text.append("by")
    all_text.append("<h2>HENRY ALFORD, D.D.</h2>")
    all_text.append("dean of canterbury.")
    all_text.append("</div>")

    all_text.append("<h1 class=\"new-page\">Table of Contents</h1>")

    all_text.append("<table><colgroup><col><col></colgroup>")
    for i in range(len(books) // 2 + 1):
        book1 = books[i]
        book2 = books[i + len(books) // 2 + 1] if i + len(books) // 2 + 1 < len(books) else None
        all_text.append("<tr>")
        all_text.append(f"<td><h2><a href=\"#{book1}TOC\">{book1}</a></h2></td>")
        if book2:
            all_text.append(f"<td><h2><a href=\"#{book2}TOC\">{book2}</a></h2></td>")
        all_text.append("</tr>")
    all_text.append("</table>")

    for book in books:
        volume, part, first_page, last_page = page_starts[book]

        all_text.append(f"<h1 class=\"new-page\" id=\"{book}TOC\"><a href=\"#{book}\">{book}</a></h1>")

        all_text.append("<table><colgroup><col><col></colgroup>")
        for i in range(1, (book_chapters[book] + 1) // 2 + 1):
            c1 = i
            c2 = i + (book_chapters[book] + 1) // 2 if i + (book_chapters[book] + 1) // 2 <= book_chapters[book] else -1
            all_text.append("<tr>")
            all_text.append(f"<td><h2><a href=\"#{book} {c1}\">Chapter {c1}</a></h2></td>")
            if c2 > 0:
                all_text.append(f"<td><h2><a href=\"#{book} {c2}\">Chapter {c2}</a></h2></td>")
            all_text.append("</tr>")
        all_text.append("</table>")
        
        all_text.append(f"<h1 class=\"new-page\" id=\"{book}\">{book_formal_names[book]}</h1>")

        first_missing_page = last_missing_page = -1

        for page in range(first_page, last_page + 1):
            # print(book, volume, part, curr_page)
            html_file_path = f'{output_dir}/html/Vol {volume} Part {part}/{page}.html'

            if os.path.exists(html_file_path):
                if first_missing_page != -1:
                    all_text.append(f"<h2>MISSING PAGES: Volume {volume}, Part {part}, {book}, Pages {first_missing_page}-{last_missing_page} missing.</h2>")
                    first_missing_page = last_missing_page = -1

                all_text.append(f'<a href="{links[(volume, part, page)]}" target="_blank">(DOCX LINK Volume {volume}, Part {part}, Page {page})</a>')

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

    final_text = ' '.join(all_text)

    # print("Writing final output...")

    with open(output_file_path, 'w') as f:
        f.write(final_text)

    # print("Done.")

    return final_text
    

def ask_yn(question):
    response = input(f'{question} (y/n) ')
    return response.strip().lower() == 'y'

if __name__ == '__main__':
    # Old Process:
    # convert_docx_to_html(redownload_docx=False)
    # convert_html_to_verses()
    # get_detailed_progress()

    # New Consolidation:
    consolidate()