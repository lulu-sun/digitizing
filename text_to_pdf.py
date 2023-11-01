import textwrap
from fpdf import FPDF

def text_to_pdf(text_files, output_file):
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = int(a4_width_mm / character_width_mm)

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_font('DejaVu', '', 'DejaVuSansMono.ttf', uni=True)
    pdf.set_font('DejaVu', '', fontsize_pt)

    for text_file in text_files:
        with open(text_file, 'r', encoding='utf-8') as file:
            text = file.read()

            pdf.add_page()
            splitted = text.split('\n')

            for line in splitted:
                lines = textwrap.wrap(line, width_text)

                if len(lines) == 0:
                    pdf.ln()

                for wrap in lines:
                    pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(output_file, 'F')
    
    
if __name__ == '__main__':
    import os
    folder_path = 'extract_dir_2'
    file_list = sorted([f'{folder_path}/{f}' for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))], key=lambda x: int(x.split('-')[1].split('.')[0]))
    # print(file_list)
    text_to_pdf(file_list, "output.pdf")