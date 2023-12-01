import pdfkit

def convert_html_to_pdf(html_file, output_pdf):
    options = {
        'no-images': '',  # To disable loading of images (optional)
        # 'quiet': '',  # To suppress wkhtmltopdf command line output (optional)
        'print-media-type': '',  # Use print media type instead of screen (optional)
        'disable-smart-shrinking': '',  # Disable the intelligent shrinking strategy (optional)
        'page-size': 'Letter',  # Specify the page size (optional)
        'margin-top': '1in',  # Set top margin (optional)
        'margin-right': '1in',  # Set right margin (optional)
        'margin-bottom': '1in',  # Set bottom margin (optional)
        'margin-left': '1in',  # Set left margin (optional)
        # 'header-left': '',  # Set left header (optional)
        # 'header-right': '[title]',  # Set right header (optional)
        # 'footer-left': '',  # Set left footer (optional)
        # 'footer-right': '[page]',  # Set right footer (optional)
        'footer-center': '[page]',  # Set center footer (optional)
        'footer-font-name': 'Caslon',
        'footer-font-size': '10',
        'encoding': 'utf-8',  # Specify encoding (optional)
        'custom-header': [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
            ('Accept-Encoding', 'gzip')
        ],
        'disable-javascript': '',
        'enable-local-file-access': '',
        'allow': 'consolidation/', 
    }

    pdfkit.from_file(html_file, output_pdf, options=options)


if __name__ == '__main__':
    # Example usage:
    html_file = 'consolidation/output/alford-processed.html'
    output_pdf = 'consolidation/output/alford.pdf'

    convert_html_to_pdf(html_file, output_pdf)