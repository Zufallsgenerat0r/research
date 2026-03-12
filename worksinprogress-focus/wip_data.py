"""
Works in Progress Magazine - Comprehensive Article & Author Dataset
Compiled from web searches of worksinprogress.co (March 2026)
"""

# Each article: (issue_number, title, authors_list, topic_tags, year)
# Topics are inferred from article descriptions

ARTICLES = [
    # Issue 1 - State Capacity (2020)
    (1, "Epidemic disease and the state", ["Mark Koyama"], ["state capacity", "health", "history"], 2020),
    (1, "How to build a state", ["Anton Howes"], ["state capacity", "history", "governance"], 2020),
    (1, "The entrepreneurial state", ["David Schönholzer"], ["state capacity", "economics", "governance"], 2020),
    (1, "How Mexico built a state", ["Jeffrey Mason"], ["state capacity", "history", "development"], 2020),
    (1, "Build state capacity by building charter cities", ["Mark Lutter"], ["state capacity", "cities", "development"], 2020),
    (1, "The story of Viktor Zhdanov", ["Saloni Dattani"], ["health", "history", "science"], 2020),
    (1, "Innovation is not linear", ["Jason Crawford"], ["innovation", "science", "metascience"], 2020),

    # Issue 2 (2020)
    (2, "The case for less philanthropy", ["Sam Bowman"], ["economics", "policy", "development"], 2020),
    (2, "How Rome fell", ["Peter Turchin"], ["history", "governance"], 2020),
    (2, "Understanding progress", ["Tyler Cowen"], ["economics", "innovation", "metascience"], 2020),

    # Issue 3 (2020)
    (3, "The rise of the high-rise", ["Brian Potter"], ["housing", "architecture", "construction"], 2020),
    (3, "Why hasn't progress been made on homelessness?", ["Salim Furth"], ["housing", "economics", "policy"], 2020),
    (3, "Flying cars", ["Tamara Winter"], ["transport", "innovation", "technology"], 2020),

    # Issue 4 (2021)
    (4, "The housing theory of everything", ["Sam Bowman", "John Myers", "Ben Southwood"], ["housing", "economics", "policy"], 2021),
    (4, "Are we in a permanent productivity slowdown?", ["Eli Dourado"], ["economics", "innovation", "technology"], 2021),
    (4, "Nanotechnology", ["Eli Dourado"], ["technology", "science", "innovation"], 2021),

    # Issue 5 (2021)
    (5, "The future of weight loss", ["Stephan J. Guyenet"], ["health", "science", "medicine"], 2021),
    (5, "Asteroid risk", ["Tom Chivers"], ["science", "space", "risk"], 2021),
    (5, "Nuclear power", ["Jack Devanney"], ["energy", "nuclear", "technology"], 2021),
    (5, "Where is my flying car?", ["Tamara Winter"], ["technology", "innovation", "transport"], 2021),

    # Issue 6 (2021)
    (6, "Progress unmoored", ["Jason Crawford"], ["innovation", "metascience", "economics"], 2021),
    (6, "Building back faster", ["Ben Southwood"], ["construction", "policy", "infrastructure"], 2021),
    (6, "The long road to electric cars", ["Virginia Postrel"], ["transport", "energy", "technology"], 2021),

    # Issue 7 (2022)
    (7, "Why Britain doesn't build", ["Sam Bowman"], ["housing", "construction", "policy"], 2022),
    (7, "The maintenance race", ["Stewart Brand"], ["infrastructure", "construction", "innovation"], 2022),
    (7, "Ending acid rain", ["Hannah Ritchie"], ["environment", "policy", "energy"], 2022),

    # Issue 8 (2022)
    (8, "The magic of milk", ["Virginia Postrel"], ["agriculture", "history", "science"], 2022),
    (8, "Nuclear federalism", ["John Myers"], ["energy", "nuclear", "policy"], 2022),
    (8, "Career and family", ["Xander Balwit"], ["demographics", "economics", "policy"], 2022),

    # Issue 9 (2022)
    (9, "The case for the suburbs", ["Samuel Hughes"], ["housing", "cities", "architecture"], 2022),
    (9, "How to speed up science", ["Benjamin Reinhardt"], ["metascience", "science", "innovation"], 2022),
    (9, "Indoor air quality", ["Gavriel Kleinwaks"], ["health", "environment", "technology"], 2022),
    (9, "Why progress is not inevitable", ["Stephen Davies"], ["innovation", "economics", "history"], 2022),

    # Issue 10 (2023)
    (10, "France's baby bust", ["Guillaume Blanc"], ["demographics", "history", "economics"], 2023),
    (10, "Building infrastructure without environmental costs", ["Samuel Watling"], ["infrastructure", "environment", "policy"], 2023),
    (10, "The fear of plutonium", ["Jack Devanney"], ["energy", "nuclear", "risk"], 2023),
    (10, "Learning to see through prey's eyes", ["Sarah Perry"], ["science", "biology", "innovation"], 2023),

    # Issue 11 (2023)
    (11, "Olivine and climate change", ["Cody Moser"], ["environment", "science", "technology"], 2023),
    (11, "Planning reform in Britain", ["Samuel Watling"], ["housing", "policy", "governance"], 2023),
    (11, "GLP-1 agonists revolution", ["Stephan J. Guyenet"], ["health", "medicine", "science"], 2023),
    (11, "Fertility technology", ["Ruxandra Teslo"], ["demographics", "health", "technology"], 2023),

    # Issue 12 (2023)
    (12, "The malaria vaccine", ["Saloni Dattani", "Rachel Glennerster", "Siddhartha Haria"], ["health", "medicine", "development"], 2023),
    (12, "The beauty of concrete", ["Samuel Hughes"], ["architecture", "construction", "aesthetics"], 2023),
    (12, "Houston's gentle density revolution", ["Emily Hamilton"], ["housing", "cities", "policy"], 2023),
    (12, "The Baby Boom and today's fertility bust", ["Lyman Stone"], ["demographics", "economics", "history"], 2023),
    (12, "The world's growing demand for copper", ["Brian Potter"], ["materials", "technology", "economics"], 2023),

    # Issue 13 (2024)
    (13, "How mathematics built the modern world", ["Bo Malmberg", "Hannes Malmberg"], ["science", "history", "innovation"], 2024),
    (13, "Asbestos: miracle material with horrific downsides", ["Tom Ough"], ["materials", "health", "history"], 2024),
    (13, "Geothermal energy", ["Ulkar Aghayeva"], ["energy", "technology", "environment"], 2024),
    (13, "Hidden knowledge in scientific papers", ["Ulkar Aghayeva"], ["metascience", "science", "innovation"], 2024),
    (13, "New Zealand's upzoning reforms", ["Marko Garlick", "Eleanor West"], ["housing", "policy", "cities"], 2024),
    (13, "Why high-cost cities have more homelessness", ["Mano Majumdar"], ["housing", "cities", "economics"], 2024),
    (13, "Madrid tripled its metro in 12 years", ["David Schönholzer"], ["transport", "infrastructure", "cities"], 2024),
    (13, "Cruise ships: what can still be built", ["Peter Suderman"], ["construction", "innovation", "technology"], 2024),

    # Issue 14 (2024)
    (14, "Unwinding Russian serfdom", ["Samuel Watling"], ["history", "economics", "governance"], 2024),
    (14, "Organ donation reform", ["Jason Hausenloy", "Duncan McClements"], ["health", "medicine", "policy"], 2024),
    (14, "Human challenge trials for Zika", ["Keller Scholl"], ["health", "medicine", "science"], 2024),
    (14, "Israeli housing reform", ["Tal Alster"], ["housing", "policy", "economics"], 2024),
    (14, "Cut-and-cover vs tunnel boring", ["Brian Potter"], ["construction", "infrastructure", "technology"], 2024),
    (14, "Silk: stronger than steel", ["Hiawatha Bray"], ["materials", "science", "technology"], 2024),
    (14, "SGLT2 inhibitors", ["Natália Coelho Mendonça"], ["health", "medicine", "science"], 2024),

    # Issue 15 (2024)
    (15, "Deterrence and crime: the campaign against drunk driving", ["Samuel Watling"], ["policy", "governance", "history"], 2024),
    (15, "Prediction markets", ["Nick Whitaker", "J. Zachary Mazlish"], ["economics", "technology", "policy"], 2024),
    (15, "Congestion pricing in New York", ["Ben Adler"], ["transport", "cities", "policy"], 2024),
    (15, "Why modern buildings are simple and austere", ["Samuel Hughes"], ["architecture", "aesthetics", "construction"], 2024),
    (15, "New materials: from invention to mass production", ["Benjamin Reinhardt"], ["materials", "technology", "innovation"], 2024),
    (15, "Britain's 1970s house price surge", ["Samuel Watling"], ["housing", "economics", "history"], 2024),
    (15, "Japan's approach to neighborhood replanning", ["Samuel Hughes"], ["housing", "cities", "policy"], 2024),
    (15, "Animal drugs vs human drug approval", ["Nick Cowen"], ["medicine", "policy", "science"], 2024),

    # Issue 16 (2025)
    (16, "Gene drives against malaria mosquitoes", ["Saloni Dattani"], ["health", "science", "technology"], 2025),
    (16, "Synthetic diamonds", ["Judge Glock"], ["materials", "technology", "economics"], 2025),
    (16, "Calculating inflation", ["Carola Conces Binder"], ["economics", "policy", "metascience"], 2025),
    (16, "Rediscovering lost ancient texts", ["Ed Conway"], ["history", "science", "innovation"], 2025),
    (16, "Advance Market Commitments", ["Rachel Glennerster", "Anya Martin"], ["economics", "development", "policy"], 2025),
    (16, "Materials libraries", ["Anya Martin"], ["materials", "science", "innovation"], 2025),
    (16, "Architecture and public opinion", ["Samuel Hughes"], ["architecture", "aesthetics", "cities"], 2025),
    (16, "Governance and economic growth", ["Robin Grier"], ["economics", "governance", "development"], 2025),
    (16, "Competition measurement in regulation", ["Anvar Sarygulov"], ["economics", "policy", "governance"], 2025),
    (16, "Pour-over coffee innovation", ["Phoebe Arslanagic-Little"], ["innovation", "technology", "economics"], 2025),

    # Issue 17 (2025)
    (17, "Why high-cost cities have more homelessness", ["Mano Majumdar"], ["housing", "cities", "economics"], 2025),
    (17, "Madrid's metro expansion", ["David Schönholzer"], ["transport", "infrastructure", "cities"], 2025),
    (17, "Cruise ships as engineering marvels", ["Peter Suderman"], ["construction", "innovation", "technology"], 2025),
    (17, "Asbestos history", ["Tom Ough"], ["materials", "health", "history"], 2025),
    (17, "New Zealand upzoning backlash", ["Marko Garlick", "Eleanor West"], ["housing", "policy", "cities"], 2025),
    (17, "Mathematics and the modern world", ["Bo Malmberg", "Hannes Malmberg"], ["science", "history", "innovation"], 2025),

    # Issue 18 (2025)
    (18, "Life in the state of nature", ["Mathias Kirk Bonde"], ["history", "science", "risk"], 2025),
    (18, "Land value taxes destroy the Liberal Party", ["Nick Whitaker"], ["economics", "policy", "history"], 2025),
    (18, "China towers vs American mid-rise regulation", ["Javid Lakha"], ["housing", "architecture", "policy"], 2025),
    (18, "Measuring inflation over time", ["Carola Conces Binder"], ["economics", "metascience", "policy"], 2025),
    (18, "Climate change and solar geoengineering", ["Justin Germain"], ["environment", "science", "technology"], 2025),
    (18, "The fabric of civilization update", ["Virginia Postrel"], ["history", "technology", "innovation"], 2025),
    (18, "Creating advance market commitments guide", ["Nan Ransohoff"], ["economics", "development", "policy"], 2025),

    # Issue 19 (2025)
    (19, "Prediction markets legal but unpopular", ["Nick Whitaker", "J. Zachary Mazlish"], ["economics", "technology", "policy"], 2025),
    (19, "Congestion pricing after 60 years", ["Ben Adler"], ["transport", "cities", "policy"], 2025),
    (19, "Why modern buildings are austere", ["Samuel Hughes"], ["architecture", "aesthetics", "construction"], 2025),
    (19, "New materials to mass production", ["Benjamin Reinhardt"], ["materials", "technology", "innovation"], 2025),
    (19, "British house price growth in the 1970s", ["Samuel Watling"], ["housing", "economics", "history"], 2025),
    (19, "Japan neighborhood replanning", ["Samuel Hughes"], ["housing", "cities", "policy"], 2025),
    (19, "Animal drug approval model for humans", ["Nick Cowen"], ["medicine", "policy", "science"], 2025),
    (19, "Lead elimination in developing world", ["Anya Martin"], ["health", "development", "environment"], 2025),

    # Issue 20 (2025)
    (20, "Unwinding Russian serfdom", ["Samuel Watling"], ["history", "economics", "governance"], 2025),
    (20, "Organ donation reform", ["Jason Hausenloy", "Duncan McClements"], ["health", "medicine", "policy"], 2025),
    (20, "Human challenge trials", ["Keller Scholl"], ["health", "medicine", "science"], 2025),
    (20, "Israeli housing reform", ["Tal Alster"], ["housing", "policy", "economics"], 2025),
    (20, "Cut-and-cover construction", ["Brian Potter"], ["construction", "infrastructure", "technology"], 2025),
    (20, "Silk applications", ["Hiawatha Bray"], ["materials", "science", "technology"], 2025),
    (20, "SGLT2 inhibitors for diabetes", ["Natália Coelho Mendonça"], ["health", "medicine", "science"], 2025),
    (20, "Germicidal ultraviolet light", ["Gavriel Kleinwaks"], ["health", "technology", "environment"], 2025),

    # Issue 21 (2025)
    (21, "The Great Downzoning", ["Samuel Hughes"], ["housing", "cities", "policy"], 2025),
    (21, "The dishwasher revolution", ["Aled Maclean-Jones"], ["technology", "demographics", "innovation"], 2025),
    (21, "Wider roads for developing world cities", ["Veera Rajagopal"], ["transport", "cities", "development"], 2025),
    (21, "How English prose became clearer", ["Henry Oliver"], ["history", "innovation", "aesthetics"], 2025),
    (21, "Microbial evolution in real time", ["Angadh Nanjangud"], ["science", "biology", "innovation"], 2025),
    (21, "Competition as holy grail of regulation", ["Erin Braid"], ["economics", "policy", "governance"], 2025),
    (21, "Using genomes for drug development", ["Saarthak Gupta"], ["health", "medicine", "technology"], 2025),
    (21, "Charles Darwin and evolution revisited", ["Kevin Blake"], ["science", "history", "biology"], 2025),
]

# Topic categories for higher-level grouping
TOPIC_CATEGORIES = {
    "Housing & Urban Planning": ["housing", "cities", "architecture", "aesthetics"],
    "Science & Innovation": ["science", "innovation", "metascience", "biology"],
    "Health & Medicine": ["health", "medicine"],
    "Energy & Environment": ["energy", "nuclear", "environment"],
    "Economics & Policy": ["economics", "policy", "governance", "development"],
    "History": ["history"],
    "Technology & Materials": ["technology", "materials"],
    "Infrastructure & Transport": ["transport", "infrastructure", "construction"],
    "Demographics": ["demographics"],
    "Risk & Space": ["risk", "space"],
    "Agriculture": ["agriculture"],
}

# Author affiliations/bios
AUTHOR_BIOS = {
    "Sam Bowman": "Founding editor, Mercatus Center board member",
    "Saloni Dattani": "Founding editor, PhD psychiatric genetics, Scientific Discovery newsletter",
    "Ben Southwood": "Founding editor, head of housing at Policy Exchange",
    "Nick Whitaker": "Founding editor",
    "Samuel Hughes": "Editor, philosopher, Oxford researcher",
    "Virginia Postrel": "Author, Bloomberg/Atlantic/NYT columnist",
    "Samuel Watling": "Regular contributor, housing & history",
    "Brian Potter": "Construction Physics newsletter",
    "Hannah Ritchie": "Our World in Data deputy editor",
    "Stewart Brand": "Author, Maintenance: Of Everything",
    "Benjamin Reinhardt": "Science & materials researcher",
    "Anton Howes": "Economic historian, Arts and Minds author",
    "Eli Dourado": "Technology & productivity researcher",
    "Stephan J. Guyenet": "Neuroscience & obesity researcher, The Hungry Brain author",
    "Jason Crawford": "The Roots of Progress author",
    "Tom Chivers": "Science journalist",
    "Xander Balwit": "Editor in chief, Asimov Press",
    "Emily Hamilton": "Housing policy researcher",
    "Rachel Glennerster": "Development economist",
    "Mark Koyama": "Economic historian",
    "John Myers": "London YIMBY co-founder",
    "Jack Devanney": "ThorCon nuclear engineer",
    "Tom Ough": "Science journalist",
    "David Schönholzer": "Economist, public goods",
    "Peter Suderman": "Journalist",
    "Carola Conces Binder": "Associate professor, UT Austin",
    "Ruxandra Teslo": "PhD student, genomics, Sanger Institute",
    "Bo Malmberg": "Researcher, mathematics & industry",
    "Hannes Malmberg": "Researcher, mathematics & industry",
    "Angadh Nanjangud": "Lecturer, spacecraft engineering, Queen Mary",
    "Anya Martin": "Regular contributor",
}

# Editorial team
EDITORIAL_TEAM = [
    "Sam Bowman", "Saloni Dattani", "Ben Southwood", "Nick Whitaker",
    "Samuel Hughes", "Virginia Postrel", "Pieter Garicano",
    "Rachel Edwards", "Aria Babu", "Alex Chalmers"
]
