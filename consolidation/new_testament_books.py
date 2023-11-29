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

books = [
    'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians',
    '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians',
    '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus',
    'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter', '1 John', '2 John',
    '3 John', 'Jude', 'Revelation'
]

book_chapters = {
    'Matthew': 28,
    'Mark': 16,
    'Luke': 24,
    'John': 21,
    'Acts': 28,
    'Romans': 16,
    '1 Corinthians': 16,
    '2 Corinthians': 13,
    'Galatians': 6,
    'Ephesians': 6,
    'Philippians': 4,
    'Colossians': 4,
    '1 Thessalonians': 5,
    '2 Thessalonians': 3,
    '1 Timothy': 6,
    '2 Timothy': 4,
    'Titus': 3,
    'Philemon': 1,
    'Hebrews': 13,
    'James': 5,
    '1 Peter': 5,
    '2 Peter': 3,
    '1 John': 5,
    '2 John': 1,
    '3 John': 1,
    'Jude': 1,
    'Revelation': 22
}

book_formal_names = {
    "Matthew": "The Gospel According To Matthew",
    "Mark": "The Gospel According To Mark",
    "Luke": "The Gospel According To Luke",
    "John": "The Gospel According To John",
    "Acts": "The Acts Of The Apostles",
    "Romans": "The Epistle Of Paul The Apostle To The Romans",
    "1 Corinthians": "The First Letter Of Paul The Apostle To The Corinthians",
    "2 Corinthians": "The Second Letter Of Paul The Apostle To The Corinthians",
    "Galatians": "The Epistle Of Paul The Apostle To The Galatians",
    "Ephesians": "The Epistle Of Paul The Apostle To The Ephesians",
    "Philippians": "The Epistle Of Paul The Apostle To The Philippians",
    "Colossians": "The Epistle Of Paul The Apostle To The Colossians",
    "1 Thessalonians": "The First Letter Of Paul The Apostle To The Thessalonians",
    "2 Thessalonians": "The Second Letter Of Paul The Apostle To The Thessalonians",
    "1 Timothy": "The First Letter Of Paul The Apostle To Timothy",
    "2 Timothy": "The Second Letter Of Paul The Apostle To Timothy",
    "Titus": "The Epistle Of Paul To Titus",
    "Philemon": "The Epistle Of Paul To Philemon",
    "Hebrews": "The Epistle To The Hebrews",
    "James": "The General Epistle Of James",
    "1 Peter": "The First Epistle General Of Peter",
    "2 Peter": "The Second Epistle General Of Peter",
    "1 John": "The First Epistle General Of John",
    "2 John": "The Second Epistle Of John",
    "3 John": "The Third Epistle Of John",
    "Jude": "The General Epistle Of Jude",
    "Revelation": "The Revelation Of John",
}

# (volume, part, page) -> google drive link
links = {}

for v in range(1, 3):
    for p in range(1, 3):
        with open(f"consolidation/v{v}p{p}links.txt", 'r') as f:
            for i, link in enumerate(f.readlines()):
                links[(v, p, i + 1)] = link

# print(links)