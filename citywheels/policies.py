from pathlib import Path
 
POLICIES_PATH = Path(__file__).parent.parent / "data" / "policies"


STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "do", "does", "can", "could", "would",
    "will", "i", "my", "me", "we", "you", "your", "it", "of", "to", "in", "on",
    "at", "for", "and", "or", "how", "what", "when", "which", "who",
    "there", "this", "that", "with", "if", "be", "have", "has", "get",
    "why", "did", "our", "had", "was", "were", "from", "their", "they",
    "them", "its", "but", "please", "tell", "want", "need",
}

def load_policy_sections(path = POLICIES_PATH):
    sections = []

    for file in sorted(Path(path).glob("*.md")):
        lines = file.read_text(encoding="utf-8").splitlines()
        title = file.stem
        text_lines = []

        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
            elif line.startswith("## "):
                text = "\n".join(text_lines).strip()
                if text:
                    sections.append({
                        "source": file.name,
                        "title": title,
                        "text": text,
                    })

                title = line[3:].strip()
                text_lines = []
            else:
                text_lines.append(line)

        text = "\n".join(text_lines).strip()
        if text:
            sections.append({
                "source": file.name,
                "title": title,
                "text": text,
            })

    return sections


def get_keywords(text):
    clean = ""
    for char in text.lower():
        if char.isalnum():
            clean += char
        else:
            clean += " "

    keywords = set()
    for word in clean.split():
        if word in STOPWORDS:
            continue
        if len(word) < 3 and word != "no":
            continue
        if word.endswith("s"):
            word = word[:-1]
        keywords.add(word[:4])
    return keywords


def get_points(section):
    return section["points"]

def search_policies(query, top = 3):
    if not isinstance(query, str) or not query.strip():
        return {
            "found": False,
            "results": [],
            "message": "No query was given"
        }
    query_words = get_keywords(query)
    
    results = []

    for section in load_policy_sections():
        title_words = get_keywords(section["title"])
        text_words = get_keywords(section["text"])

        points = 0
        for word in query_words:
            if word in title_words:
                points += 2
            if word in text_words:
                points += 1

        if points > 0:
            section["points"] = points
            results.append(section)

    results.sort(key=get_points, reverse=True)
    results = results[:top]

    if len(results) == 0:
        return {
            "found": False,
            "results": [],
            "message": f"No relevant information was found. Please contact the staff for assistance"
        }
    return {
        "found": True,
        "results": results
    }