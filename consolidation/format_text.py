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
    
    return re.match(r'^[“‘=+\(\[]$', text) != None

def punc_needs_space_after(text):
    if text == None:
        return False
    return re.match(r'^[’”.,=+?;:\)\]]$', text) != None

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

def format_text(text):
    all_text = text

    # Space normalization for punctuation: 
    tokens = re.findall(r'<[^>]+>|\w+|[^\w\s]', all_text) # Tags, words, and punctuation.

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

    # Second round of substitutions to fix special case punctuation spacings.
    subs = [
        (r'([^\s]+?) *- *([^\s]+?)', r'\1-\2'), # Force hyphens to not have spaces.
        (r'(\d+) *[\-–—] *(\d+)', r'\1–\2'), # Force dashes between number to be en dashes with no space.
        (r' ([A-Za-z])\. ([A-Za-z])\.', r' \1.\2.'), # Control spacing for special cases: i.e. e.g. A.V.
        (r'(\w[’\']) (s[^\w])', r'\1\2'), # Force apostrophes to remove surrounding spaces.
        (r'&e', '&c'), # &e should be &c meaning etc
        (r'snch', 'such'), # common typo
        (r'([^\w])iu([^\w])', r'\1in\2'), # common typo
        (r'snbjective', 'subjective'), # common typo
        (r'([^\w])vy([^\w])', r'\1vv\2'), # common typo
        (r'([^\w])sce([^\w])', r'\1see\2'), # common typo
        (r'([^\w])meu([^\w])', r'\1men\2'), # common typo
        (r'([^\w])ouly([^\w])', r'\1only\2'), # common typo
        (r'([^\w])ef([^\w])', r'\1cf\2'), # common typo
        (r'([^\w])Judea([^\w])', r'\1Judæa\2'), # common typo
        (r'([^\w])Liicke([^\w])', r'\1Lücke\2'), # common typo
    ]

    for find, replace in subs:
        all_text = re.sub(find, replace, all_text)

    return all_text


if __name__ == '__main__':
    # Example usage
    input_text = "—A similar expression with regard to Israel is found in Exod. iv. 22, 23.<br><br><b>that it might be fulfilled</b> must not be explained away: it never denotes the event or mere result, but always the <i>purpose</i>.<h2><u><b>16.</b>]</u></h2> Josephus makes no mention of this slaughter; nor is it likely that he would have done. Probably no great number of children perished in so small a place as Bethlehem and its neighbourhood. The modern objections to this narrative may be answered best by remembering the monstrous character of this tyrant, of whom Josephus asserts, “a dark choler seized on him, maddening him against all.’ i. e. hello account \n\n\nof her. What about Rahab’s and Abraham’s sceptre or Isaac's?"
    normalized_text = format_text(input_text)
    print(normalized_text)
