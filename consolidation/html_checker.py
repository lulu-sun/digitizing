import re




def get_output_file_path(name):
    return f'consolidation/output/check-{name}.txt'

def write_to_output_file(name, text):
    open(get_output_file_path(name), 'w').write(text)

# e.g. "X.", "IV."
def is_roman_numeral(numeral):
    """Controls that the userinput only contains valid roman numerals"""
    if not numeral or numeral[-1] != '.' or numeral == '.':
        return False
    numeral = numeral[:-1]
    validRomanNumerals = ["M", "D", "C", "L", "X", "V", "I"]
    valid = True
    for letters in numeral:
        if letters not in validRomanNumerals:
            valid = False
            break
    return valid


def contains_roman_numeral(input_string):
    def clean(text):
        text = re.sub(r'<.+?>', '', text)
        # text = re.sub(r'[^\w]+', '', text)

        return text

    parts = list(map(clean, input_string.split()))

    for part in parts:
        if is_roman_numeral(part):
            print(input_string, part)
            return True
    
    return False

if __name__ == '__main__':
    raw_html = open('consolidation/output/2_alford.html').read()
    processed_html = open('consolidation/output/3_alford-processed.html').read()


    long_tags = []
    chap_tags = []
    dash_tags = []

    pattern = r'<br><br>([^<>\[\]]*(?:(?!<br>|\[.*\]).)*?\])'
    for i, result in enumerate(re.findall(pattern, processed_html)):
        if len(result) >= 70:
            long_tags.append(result)

        if contains_roman_numeral(result):
            chap_tags.append(result)

        if "-" in result or "–" in result or "—" in result:
            dash_tags.append(result)


    write_to_output_file('long-tags', '\n\n'.join(long_tags))
    write_to_output_file('chap-tags', '\n\n'.join(chap_tags))
    write_to_output_file('dash-tags', '\n\n'.join(dash_tags))




