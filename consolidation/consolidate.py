# Assumptions:
# - consolidation folder contains:
#   - extracted_texts folder with all updated edited extracted_texts
#   - Page Assignments.xlsx with all updated completed tracking
#   - Above two files are in sync and agree with each other

import pandas as pd
import docx
import re
import os

working_dir = "consolidation"
input_dir = f"{working_dir}/input"
output_dir = f"{working_dir}/output"

xlsx_file = f'{input_dir}/Page Assignments.xlsx'

def get_file_path(volume, part, page_number):
    return f"{input_dir}/extracted_texts/Vol {volume} Part {part}/extracted_text-{page_number}.docx"

def run_to_html(run):
    html = run.text
    if run.bold:
        html = f'<b>{html}</b>'
    if run.italic:
        html = f'<i>{html}</i>'
    if run.underline:
        html = f'<u>{html}</u>'
    return html

def convert_docx_to_html():
    # Read the Excel file into a DataFrame
    df = pd.read_excel(xlsx_file)

    for volume, part in [(1,1),(1,2),(2,1),(2,2)]:
        starting_column = ((volume - 1) * 8 + (part - 1) * 4)
        dfvp = df.iloc[1:, starting_column:starting_column+3]

        condition = dfvp.iloc[:, 2] == True

        dfvp_completed = dfvp[condition]

        for index, row in dfvp_completed.iterrows():
            page_number = row[0]
            editor = row[1]
            completed = row[2]
            docx_file_path = get_file_path(volume, part, page_number)
            
            print(f"Volume {volume} Part {part}", page_number, editor, completed, docx_file_path)

            formatted_html = []

            doc = docx.Document(docx_file_path)
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    formatted_html.append(run_to_html(run))

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
            formatted_html = re.sub(r'—', '-', formatted_html)
            
            output_file_path = f'{output_dir}/html/Vol {volume} Part {part}/{page_number}.html'
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            with open(output_file_path, 'w') as f:
                f.write(formatted_html)


def convert_html_to_verses():
    text = []
    
    for volume, part in [(1, 2)]:
        for page_number in range(63, 68 + 1):
            
            html_file_path = f'{output_dir}/html/Vol {volume} Part {part}/{page_number}.html'
            with open(html_file_path) as f:
                text.append(f.read())


    text = ' '.join(text)

    pattern = r'(\[(?:CHAP.*?|\d+|\d+-\d+|.*?)..*?\])'
    result = re.split(pattern, text)

    output_text = []

    for block in result:
        if block.startswith('['):
            if "CHAP" in block:
                h = 1
            elif re.search(r'\d+.', block):
                h = 2
            else:
                h = 3
            output_text.append(f'<h{h}>{block}</h{h}>')
        else:
            output_text.append(block)

    with open(f'{output_dir}/test.html', 'w') as f:
        f.write(''.join(output_text))





if __name__ == '__main__':
    convert_docx_to_html()
    convert_html_to_verses()