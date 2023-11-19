from htmldocx import HtmlToDocx

def convert_html_to_docx(html_file_path, docx_file_path):
    new_parser = HtmlToDocx()
    html_string = open(html_file_path, 'r').read()

    docx = new_parser.parse_html_string(html_string)

    docx.save(docx_file_path)
