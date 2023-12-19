import re
import roman
from new_testament_books import books, book_chapters
from html_checker import is_roman_numeral


def remove_tags(input_string):
    clean_text = re.sub(r'<.*?>', '', input_string)
    return clean_text

def insert_chapters_from_to_file(input_file_path, output_file_path):
    html_text = open(input_file_path).read()
    new_html_text = insert_chapters(html_text)
    open(output_file_path, 'w').write(new_html_text)

def insert_chapters(html_text):
    skipped = 0
    current_book = ''
    current_chapter = 0

    all_text = []
    
    for block in html_text.split('<br><br>'):
        block_copy = block
        match_obj = re.search(r'<h1 class="new-page" id="([\w\s]+)"> ([\w\s]+)</h1>', block)
        if match_obj:
            new_book = match_obj.group(1)
            
            # print("New book found:", new_book)
            
            if not current_book or book_chapters[current_book] == current_chapter:
                current_book = new_book
                current_chapter = 0
            else:
                raise Exception(f"New book found but chapters of previous book not finished. Current chapter: {current_book} {current_chapter}")

        if ']' not in block:
            all_text.append(block + '<br><br>')
            continue

        tag = block.split(']')[0]
        if tag.count('[') > tag.count(']'):
            # not a tag because of opening bracket.
            all_text.append(block + '<br><br>')
            continue

        tag = remove_tags(tag)

        match_obj = re.search(r' ([IVX]+\.)', tag)

        if match_obj:
            roman_numeral = match_obj.group(1)

            # ignore roman_numerals after dashes
            dash_in_tag = re.search(r'[\-–—]', tag)
            if dash_in_tag and dash_in_tag.start() < tag.find(roman_numeral):
                all_text.append(block + '<br><br>')
                continue

            if is_roman_numeral(roman_numeral):
                # print(potential_tag, tag_portion)

                roman_numeral = roman_numeral[:-1]
                number = roman.fromRoman(roman_numeral)
                if number == current_chapter + 1 and number <= book_chapters[current_book]:
                    current_chapter = number
                    # print(f"Current chapter: {current_book} {current_chapter}")

                    # Add new page for each chapter
                    # new_page = "class=\"new-page\"" if current_chapter > 1 else ""

                    # Don't add new page for each chapter
                    new_page = ""
                    all_text.append(f"<h2 {new_page} id=\"{current_book} {current_chapter}\"><i>{current_book}: Chapter {current_chapter}</i></h2>")

                    skipped = 0
                else:
                    # Sometimes Alford repeats current chapter.
                    if number == current_chapter:
                        all_text.append(block + '<br><br>')
                        continue 

                    # print(f"Unexpected chapter number found! Tag: {tag}. Current chapter: {current_book} {current_chapter}; Chapter found: {number}")

                    # current_chapter = number
                    if skipped == 2:
                        raise Exception(f"Too many unexpected chapters. Current chapter: {current_book} {current_chapter}; Chapter found: {number}")
                    skipped += 1

        all_text.append(block + '<br><br>')


    final_html = ''.join(all_text)
    return final_html


if __name__ == '__main__':
    output_dir = f"consolidation/output"
    insert_chapters_from_to_file(f'{output_dir}/3_alford-processed.html', f'{output_dir}/4_alford-chap-inserted.html')