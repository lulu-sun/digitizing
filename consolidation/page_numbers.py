# Book -> Volume, Part, Start, End

page_starts = {
    "Matthew": (1, 1, 68, 284),
    "Mark": (1, 1, 285, 357),
    "Luke": (1, 1, 358, 519),
    "John": (1, 2, 63, 254),
    "Acts": (1, 2, 255, 449),
    "Romans": (2, 1, 153, 286),
    "1 Corinthians": (2, 1, 287, 400),
    "2 Corinthians": (2, 1, 401, 470),
    "Galatians": (2, 1, 471, 513),
    "Ephesians": (2, 1, 514, 565),
    "Philippians": (2, 1, 566, 593),
    "Colossians": (2, 1, 594, 625),
    "1 Thessalonians": (2, 1, 626, 648),
    "2 Thessalonians": (2, 1, 649, 660),
    "1 Timothy": (2, 1, 661, 704),
    "2 Timothy": (2, 1, 705, 730),
    "Titus": (2, 1, 731, 743),
    "Philemon": (2, 1, 744, 748),
    "Hebrews": (2, 2, 249, 402),
    "James": (2, 2, 403, 439),
    "1 Peter": (2, 2, 440, 482),
    "2 Peter": (2, 2, 483, 504),
    "1 John": (2, 2, 505, 571),
    "2 John": (2, 2, 572, 576),
    "3 John": (2, 2, 577, 580),
    "Jude": (2, 2, 581, 591),
    "Revelation": (2, 2, 592, 754),
}

new_testament_books = [
    'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians',
    '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians',
    '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus',
    'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter', '1 John', '2 John',
    '3 John', 'Jude', 'Revelation'
]

# (volume, part, page) -> google drive link
links = {}

for v in range(1, 3):
    for p in range(1, 3):
        with open(f"consolidation/v{v}p{p}links.txt", 'r') as f:
            for i, link in enumerate(f.readlines()):
                links[(v, p, i + 1)] = link

# print(links)