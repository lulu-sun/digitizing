# import spacy
import string
import re
from gensim.utils import tokenize

# Load SpaCy English model
# nlp = spacy.load("en_core_web_sm")

# def normalize_spacing_correctly(text):
#     # Process the text using SpaCy
#     doc = nlp(text)

#     # Reconstruct the text with normalized spacing
#     normalized_text = " ".join(
#         token.text if not token.is_punct else f" {token.text} "
#         for token in doc
#     ).strip()

#     return normalized_text

def is_word(text):
    if text == None:
        return False
    return re.match(r'^\w+$', text) != None

def is_punc(text):
    if text == None:
        return False
    return not is_word(text) and not is_tag(text)

def punc_needs_space_before(text):
    if text == None:
        return False
    
    return re.match(r'^[“‘=+\-–—\(\[]$', text) != None

def punc_needs_space_after(text):
    if text == None:
        return False
    return re.match(r'^[’”.,=+\-–—?;:\)\]]$', text) != None

def punc_needs_space_in_between(previous, current):
    if previous == None:
        return False
    
    if punc_needs_space_before(current):
        return True
    
    if is_punc(previous) and is_punc(current):
        return False
    
    return not (previous, current) in [
        (':', '—'), # em dash
        (':', '–'), # en dash
        (':', '-'), # hyphen
    ]
    



def is_tag(text):
    return re.match(r'^<[^>]+>$', text) != None

def needs_space(previous, current):
    return (
        is_word(previous) and is_word(current) or
        is_punc(previous) and is_word(current)
    )

def normalize_spacing(text):
    tokens = re.findall(r'<[^>]+>|\w+|[^\w|^\s]', text)

    all_text = []
    previous = None
    for i, current in enumerate(tokens):
        if is_tag(current):
            all_text.append(current)

        elif is_word(current):
            if is_word(previous):
                all_text.append(' ')
            elif is_punc(previous) and punc_needs_space_after(previous):
                all_text.append(' ')

            all_text.append(current)
            previous = current
        elif is_punc(current):
            if is_word(previous):
                if punc_needs_space_before(current):
                    all_text.append(' ')
            
            elif is_punc(previous) and punc_needs_space_in_between(previous, current):
                all_text.append(' ')

            all_text.append(current)
            previous = current
        else:
            raise Exception(f"Token not recognized: {current}")

    all_text = ''.join(all_text)
    all_text = re.sub(r'\s+', ' ', all_text)

    # Force hyphens to not have spaces.
    all_text = re.sub(r'([^\s]+?) - ([^\s]+?)', r'\1-\2', all_text)

    # Force dashes between number to be en dashes with no space.
    all_text = re.sub(r'(\d+) [\-–—] (\d+)', r'\1–\2', all_text)

    # Control spacing for special cases: i.e. e.g. A.V.
    # all_text = re.sub(r'i\. e\.', 'i.e.', all_text)
    # all_text = re.sub(r'e\. g\.', 'e.g.', all_text)
    # all_text = re.sub(r'A\. V\.', 'A.V.', all_text)
    # all_text = re.sub(r'E\. V\.', 'E.V.', all_text)
    # all_text = re.sub(r'N\. T\.', 'N.T.', all_text)
    # all_text = re.sub(r'O\. T\.', 'O.T.', all_text)
    all_text = re.sub(r' (\d)\. (\d)\.', r' \1\.\2\.', all_text)

    return all_text

if __name__ == '__main__':
    # Example usage
    input_text = "—A similar expression with regard to Israel is found in Exod. iv. 22, 23.<br><br><b>that it might be fulfilled</b> must not be ex- plained away: it never denotes the event or mere result, but always the <i>purpose</i>.<h2><u><b>16.</b>]</u></h2> Josephus makes no mention of this slaughter; nor is it likely that he would have done. Probably no great number of children perished in so small a place as Bethlehem and its neighbourhood. The modern objections to this narrative may be answered best by remembering the monstrous character of this tyrant, of whom Josephus asserts, “a dark choler seized on him, maddening him against all.’"
    normalized_text = normalize_spacing(input_text)
    print(normalized_text)
