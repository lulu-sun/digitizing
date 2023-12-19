import re
from new_testament_books import books, book_chapters
from chap_finder import remove_tags
import roman
from html_checker import is_roman_numeral
from bibleref import BibleRange
import os
import shutil

BOOKS = [BibleRange(b) for b in [
        "Matthew",
        "Mark",
        "Luke",
        "John",
        "Acts",
        "Romans",
        "1 Corinthians",
        "2 Corinthians",
        "Galatians",
        "Ephesians",
        "Philippians",
        "Colossians",
        "1 Thessalonians",
        "2 Thessalonians",
        "1 Timothy",
        "2 Timothy",
        "Titus",
        "Philemon",
        "Hebrews",
        "James",
        "1 Peter",
        "2 Peter",
        "1 John",
        "2 John",
        "3 John",
        "Jude",
        "Revelation",
        ]]


def remove_inserted_tags(html_text):
    tags_to_remove = ['head', 'div', 'h1', 'h2', 'table']
    for t in tags_to_remove:
        html_text = re.sub(fr'<{t}[^>]*?>.*?</{t}>', '', html_text)

    return html_text

def parse_commentary(html_file):
    
    html_text = open(html_file).read()

    commentary = {}

    def insert_commentary(book, chapter, verse, verse_commentary):
        if chapter <= 0 or verse <= 0 or not book in book_chapters:
            raise Exception(f"Invalid Verse: {book} {chapter}:{verse}")
        
        key = (current_book, current_chapter, current_verse) 
        if key not in commentary:
            commentary[key] = []

        commentary[key].append(verse_commentary)

    verse_ranges = {}
    verse_singles = {}

    skipped = 0
    current_book = ''
    current_chapter = 0
    current_verse = 0

    queue = html_text.split('<br><br>')

    while queue:
        block = queue.pop(0)

        match_obj = re.search(r'<h1 class="new-page" id="([\w\s]+)"> ([\w\s]+)</h1>', block)
        if match_obj:

            if match_obj.start() == 0:
                new_book = match_obj.group(1)  
                
                print("New book found:", new_book)
                
                if not current_book or book_chapters[current_book] == current_chapter:
                    current_book = new_book
                    current_chapter = 0
                    current_verse = 0
                else:
                    raise Exception(f"New book found but chapters of previous book not finished. Current chapter: {current_book} {current_chapter}")
            
            else:
                b1 = block[:match_obj.start()]
                b2 = block[match_obj.start():]                
                queue.insert(0, b2)
                queue.insert(0, b1)

            continue
            
        tag = block.split(']')[0]

        # Not a tag.
        if ']' not in block or tag.count('[') > tag.count(']'):
            match_obj = re.search(r'{\d+}', block)
            if match_obj:
                split_items = re.split(r'{(\d+)}', block)
                
                for i, it in enumerate(split_items):
                    if re.match(r'^\d+$', it):
                        current_verse = int(it)
                        verse_commentary = split_items[i + 1]

                        insert_commentary(current_book, current_chapter, current_verse, verse_commentary)
            else:
                if current_chapter > 0 and current_verse > 0:
                    insert_commentary(current_book, current_chapter, current_verse, block)
            continue

        tag = remove_tags(tag)

        match_obj = re.search(r' ([IVX]+\.)', tag)

        # Chapter tag
        if match_obj:
            roman_numeral = match_obj.group(1)

            # ignore roman_numerals after dashes
            dash_in_tag = re.search(r'[\-–—]', tag)
            if dash_in_tag and dash_in_tag.start() < tag.find(roman_numeral):
                continue

            if is_roman_numeral(roman_numeral):
                # print(potential_tag, tag_portion)

                roman_numeral = roman_numeral[:-1]
                number = roman.fromRoman(roman_numeral)
                if number == current_chapter + 1 and number <= book_chapters[current_book]:
                    current_chapter = number
                    current_verse = 0
                    print(f"Current chapter: {current_book} {current_chapter}")

                    # Add new page for each chapter
                    # new_page = "class=\"new-page\"" if current_chapter > 1 else ""

                    # Don't add new page for each chapter

                    skipped = 0
                else:
                    # Sometimes Alford repeats current chapter.
                    if number == current_chapter:
                        continue 

                    # print(f"Unexpected chapter number found! Tag: {tag}. Current chapter: {current_book} {current_chapter}; Chapter found: {number}")

                    # current_chapter = number
                    if skipped == 2:
                        raise Exception(f"Too many unexpected chapters. Current chapter: {current_book} {current_chapter}; Chapter found: {number}")
                    skipped += 1

        # Verse Range tag
        match_obj1 = re.search(r'(\d+)–(\d+)', tag)
        match_obj2 = re.search(r'(\d+), (\d+)', tag)
        if match_obj1 or match_obj2:
            match_obj = match_obj1 if match_obj1 else match_obj2
            low, high = match_obj.group(1), match_obj.group(2)
            # print(low, high)

            if (current_book, current_chapter) not in verse_ranges:
                verse_ranges[(current_book, current_chapter)] = []

            verse_ranges[(current_book, current_chapter)].append((low, high))
        
            # search for custom tags in range
            verse_commentary = ''

            match_obj = re.search(r'{\d+}', block)
            if match_obj:
                split_items = re.split(r'{(\d+)}', block)
                
                for i, it in enumerate(split_items):
                    if re.match(r'^\d+$', it):
                        current_verse = int(it)
                        verse_commentary = split_items[i + 1]

                        insert_commentary(current_book, current_chapter, current_verse, verse_commentary)
            else: # there's no {\d+} in this block
                # current_verse = int(low)

                # key = (current_book, current_chapter, current_verse)
                # if key not in commentary:
                #     commentary[key] = []
                
                # commentary[key].append(verse_commentary)
                pass
                

        # Individual Verse Tag
        else:
            match_obj = re.search(r'[^{](\d+)[^}]', tag)

            if match_obj:
                v = match_obj.group(1)
                current_verse = int(v)
                
                if (current_book, current_chapter) not in verse_singles:
                    verse_singles[(current_book, current_chapter)] = []

                verse_singles[(current_book, current_chapter)].append(current_verse)

                insert_commentary(current_book, current_chapter, current_verse, block)
                
            else: # Is a tag but not a verse tag or chapter tag
                match_obj = re.search(r'{\d+}', block)
                if match_obj:
                    split_items = re.split(r'{(\d+)}', block)
                    
                    for i, it in enumerate(split_items):
                        if re.match(r'^\d+$', it):
                            current_verse = int(it)
                            verse_commentary = split_items[i + 1]

                            insert_commentary(current_book, current_chapter, current_verse, verse_commentary)
                else:
                    if current_verse > 0:
                        insert_commentary(current_book, current_chapter, current_verse, block)     


    empty_keys = []

    # filter out whitespace or empty items
    for k, v in commentary.items():
        commentary[k] = list(filter(lambda x: x and not x.isspace(), v))
        if not commentary[k]:
            empty_keys.append(k)
        else:
            commentary[k] = remove_inserted_tags('<br><br>'.join(commentary[k]))

    for k in empty_keys:
        del commentary[k]

    return commentary



    # Find out:
    # 1. How many verse singles are there, and how many verses are not individually tagged?
    # 2. How many verse ranges are there, and how many verses do they cover?
    # 3. How many verses not individually tagged are covered by verse ranges?
    # 4. How many verse ranges do not have ANY verse singles within the range?

    # total_verses_by_book = {}
    # for book in BOOKS:
    #     total_verses_by_book[str(book)] = 0
    #     for verse in book:
    #         total_verses_by_book[str(book)] += 1

    # verses_covered_by_ranges = {}

    # verses_tagged_by_range_only_set = set()
    # total_verses = sum(total_verses_by_book.values())
    # verse_singles_count = 0
    # verse_singles_count_by_book = {}
    # verse_ranges_count = 0
    # verse_covered_by_ranges_count_by_book = {}
    # for book, num_chapters in book_chapters.items():
    #     verse_singles_count_by_book[book] = 0
    #     verse_covered_by_ranges_count_by_book[book] = 0
        

    #     for i in range(1, num_chapters + 1):
    #         verses_covered_by_ranges[(book, i)] = set()

    #         if (book, i) in verse_singles:
    #             verse_singles_count += len(verse_singles[(book, i)])
    #             verse_singles_count_by_book[book] += len(verse_singles[(book, i)])

    #         if (book, i) in verse_ranges:
    #             verse_ranges_count += len(verse_ranges[(book, i)])
    #             for l, h in verse_ranges[(book, i)]:
    #                 l = int(l)
    #                 h = int(h)
    #                 verse_covered_by_ranges_count_by_book[book] += h - l + 1
    #                 for j in range(l, h + 1):
    #                     if not (book, i) in verses_covered_by_ranges:
    #                         verses_covered_by_ranges[(book, i)] = set()
    #                     verses_covered_by_ranges[(book, i)].add(j)

    #                     # This doesn't work, I don't know what this is doing:
    #                     if ((book, i) not in verse_singles or j not in verse_singles[(book, i)]) and ((book, i) in verses_covered_by_ranges and j in verses_covered_by_ranges[(book, i)]):
    #                         verses_tagged_by_range_only_set.add((book, i, j))


    # # verse_ranges_expanded = {}
    # unique_verse_ranges = {}
    # unique_verse_ranges_expanded = {}
    # for book, chapter_num in book_chapters.items():
    #     for chap in range(1, chapter_num + 1):
    #         # if book == 'Matthew' and chap == 1:
    #         #     print(verse_singles[(book, chap)])
    #         #     print(verse_ranges[(book, chap)])
    #         #     input()
    #         unique_verse_ranges[(book, chap)] = []
    #         unique_verse_ranges_expanded[(book, chap)] = set()

    #         if (book, chap) in verse_ranges:
    #             verses = set(map(int, verse_singles[(book, chap)])) if (book, chap) in verse_singles else set()

    #             for l, h in verse_ranges[(book, chap)]:
    #                 l = int(l)
    #                 h = int(h)
    #                 range_expanded = set(range(l, h + 1))
    #                 if not (range_expanded & verses):
    #                     unique_verse_ranges[(book, chap)].append((l, h))
    #                     unique_verse_ranges_expanded[(book, chap)] |= set(range(l, h + 1))
            
    #         # unique_verse_ranges_expanded[(book, chap)]


    # percentage_verse_singles_by_book = {}
    # for book in BOOKS:
    #     book = str(book)
    #     percentage_verse_singles_by_book[book] = round(100 * verse_singles_count_by_book[book] / total_verses_by_book[book], 2)

    # print(total_verses_by_book)
    # print(verse_singles_count_by_book)
    # print(percentage_verse_singles_by_book)
    # print(verse_singles_count)
    # print()

    # print('[Summary]')
    # print(f'• Out of {total_verses} verses in the NT, {verse_singles_count} are individually tagged by Alford ({round(100 * verse_singles_count / total_verses, 2)}%). Therefore {total_verses - verse_singles_count} are not individually tagged.')
    # print(f'• The following is an ordered list of NT books and how many verses are individually tagged:')
    # for book, percentage in sorted(percentage_verse_singles_by_book.items(), key=lambda x:x[1]):
    #     print(f'  • {verse_singles_count_by_book[book]}/{total_verses_by_book[book]} ~= {percentage}%\t({book})')

    # # print(f'• There are {verse_ranges_count} sections tagged with a range of verses, covering {sum(verse_covered_by_ranges_count_by_book.values())} verses in total. Since there are only {total_verses} verses in the NT, there seems to be quite a bit of overlap in these ranges of verses.')

    # untagged_verse_count = total_verses - verse_singles_count
    # tagged_only_by_ranges_count = sum(len(v) for v in unique_verse_ranges_expanded.values())
    # ranges_count = sum(len(v) for v in unique_verse_ranges.values())
    
    # # print(untagged_verse_count, tagged_only_by_ranges_count)

    # print(f'• Out of the {untagged_verse_count} verses not tagged individually, {tagged_only_by_ranges_count} of them are included uniquely in {ranges_count} verse range tags. (In other words, there is a verse range where NONE of the verses in the range are tagged individually.) Below are all such verse ranges:')

    # for book_chap, verses in sorted(unique_verse_ranges_expanded.items(), key=lambda x:len(x[1])):
    #     if not verses:
    #         continue
    #     book, chap = book_chap
    #     vrange = unique_verse_ranges[(book, chap)]
    #     print(f'  • {len(verses)} verses: {sorted(vrange)} ({book} {chap})')

    # print('[Verse Singles]')
    # for book_chap, verses in verse_singles.items():
    #     print(book_chap, verses)

    # print('[Verse Ranges]')
    # for book_chap, verses in verse_ranges.items():
    #     print(book_chap, verses)

    # print('[Ranges Expanded]')
    # for book_chap, verses in verse_ranges_expanded.items():
    #     print(book_chap, verses)

def write_commentary_to_folder(output_folder, commentary):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    os.makedirs(output_folder)

    for loc, verse_commentary in commentary.items():
        book, chapter, verse = loc
        file_path = f'{output_folder}/{book}/Chapter {chapter}/Verse {verse}.txt'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as file:
            file.write(verse_commentary)


def parse_and_write_commentary(input_file_path, output_folder_path):
    commentary = parse_commentary(input_file_path)
    write_commentary_to_folder(output_folder_path, commentary)


if __name__ == '__main__':
    commentary = parse_commentary('consolidation/output/3_alford-processed-with-verse-tags.html')

    with open('consolidation/output/alford_verse_commentary.txt', 'w') as out_file:
        for k,v in commentary.items():
            out_file.write(str(k) + '\n\t')
            out_file.write(v + '\n\n')

    write_commentary_to_folder(f'consolidation/output/Henry Alford/', commentary)