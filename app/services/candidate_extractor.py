import re
 
 
def extract_email(text: str) -> str | None:
    """
    Extracts the first email address found.
    """
 
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
 
    match = re.search(pattern, text)
 
    if match:
        return match.group(0)
 
    return None
 
 
def extract_phone(text: str) -> str | None:
    """
    Extracts a phone number while avoiding years and date
    ranges like '2024 - 2023'.
    """
 
    patterns = [
        # International numbers:
        # +1 415 555 0132
        # +44 20 7946 0958
        r"\+\d{1,3}[\s.-]?(?:\d[\s.-]?){7,12}",
 
        # Local numbers with a leading 0:
        # 020 7946 0958
        r"\b0\d{2}[\s.-]?(?:\d[\s.-]?){6,9}\b",
 
        # Generic format like 123-456-7890 or 123.456.7890
        r"\b\d{3}[\s.-]\d{3}[\s.-]\d{4}\b"
    ]
 
    for pattern in patterns:
        matches = re.findall(pattern, text)
 
        for match in matches:
 
            # Cleanup
            phone = re.sub(r"\s+", " ", match).strip()
 
            # Count digits only
            digits = re.sub(r"\D", "", phone)
 
            # A real phone number generally has at least
            # 9 digits.
            if len(digits) >= 9:
 
                # Avoid years/date ranges
                if re.fullmatch(r"\d{4}\s*[-–]\s*\d{4}", phone):
                    continue
 
                return phone
 
    return None
 
 
def extract_name(text: str) -> str | None:
    """
    Attempts to extract the candidate's name.
 
    This function first looks for lines containing explicit
    indicators like 'Name', 'Full Name', etc.
 
    If no indicator is found, it falls back to a heuristic
    based on the first lines of the resume.
    """
 
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]
 
    # --------------------------------------------------
    # 1. Explicit search
    # --------------------------------------------------
 
    name_patterns = [
        r"^(?:name|full name)\s*[:\-]\s*(.+)$",
    ]
 
    for line in lines[:30]:
 
        for pattern in name_patterns:
 
            match = re.search(
                pattern,
                line,
                re.IGNORECASE
            )
 
            if match:
                name = match.group(1).strip()
 
                if is_valid_name(name):
                    return name
 
    # --------------------------------------------------
    # 2. Heuristic on the first lines
    # --------------------------------------------------
 
    ignored_keywords = [
        "curriculum",
        "curriculum vitae",
        "resume",
        "cv",
        "profile",
        "summary",
        "professional summary",
        "about me",
        "objective",
        "career objective",
        "skills",
        "technical skills",
        "education",
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "software development",
        "web development",
        "mobile development",
        "contact",
        "contact information",
        "languages",
        "projects",
        "certifications",
        "achievements",
        "references",
        "interests",
        "hobbies"
    ]
 
    candidates = []
 
    window = lines[:20]
    i = 0
 
    while i < len(window):
 
        line = window[i]
 
        # Skip lines containing an email
        if "@" in line:
            i += 1
            continue
 
        # Skip lines containing digits
        if re.search(r"\d", line):
            i += 1
            continue
 
        # Skip lines that are too long
        if len(line) > 50:
            i += 1
            continue
 
        normalized = line.lower().strip()
 
        # Skip known section titles
        if normalized in ignored_keywords:
            i += 1
            continue
 
        # Skip lines containing keywords
        if any(
            keyword in normalized
            for keyword in ignored_keywords
        ):
            i += 1
            continue
 
        words = line.split()
 
        # Normal case: the line already has 2 to 4 words
        if 2 <= len(words) <= 4:
 
            if is_valid_name(line):
                candidates.append(line)
                break
 
        # Case where the name is split across two lines
        # (e.g. "Andrea" on one line, "Sanchez" on the
        # next, due to the resume's layout)
        elif len(words) == 1 and i + 1 < len(window):
 
            next_line = window[i + 1]
            merged = f"{line} {next_line}"
 
            if is_valid_name(merged):
                candidates.append(merged)
                break
 
        i += 1
 
    if candidates:
        return candidates[0]
 
    return None
 
 
def is_valid_name(name: str) -> bool:
    """
    Checks whether a string can reasonably represent a
    person's name.
    """
 
    if not name:
        return False
 
    if len(name) < 3 or len(name) > 60:
        return False
 
    # No digits
    if re.search(r"\d", name):
        return False
 
    # No email
    if "@" in name:
        return False
 
    words = name.split()
 
    if not 2 <= len(words) <= 4:
        return False
 
    # Words that are normally not part of a person's name
    forbidden = {
        "software",
        "web",
        "mobile",
        "developer",
        "development",
        "engineer",
        "engineering",
        "curriculum",
        "vitae",
        "profile",
        "summary",
        "objective",
        "education",
        "experience",
        "skills",
        "contact",
        "projects",
        "certifications",
        "references"
    }
 
    for word in words:
 
        if word.lower().strip(".,:;-") in forbidden:
            return False
 
    return True
 
 
def extract_candidate_info(text: str) -> dict:
    """
    Extracts the candidate's main information.
    """
 
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text)
    }
 