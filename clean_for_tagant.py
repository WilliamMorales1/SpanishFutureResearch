import os
import re

def remove_interviewer(input_folder, output_folder, interviewee_tags=[]):
    os.makedirs(output_folder, exist_ok=True)

    # Escape tags and join them: (?:I|I\.|B)
    tag_pattern = "|".join(re.escape(t) for t in interviewee_tags)
    # Match an allowed tag, then capture everything until the next any-speaker tag or end
    regex_pattern = rf"(?:{tag_pattern}):\s*(.*?)(?=[A-Z\.]+\s*:|$)"

    for filename in os.listdir(input_folder):
        src_path = os.path.join(input_folder, filename)
        if os.path.isdir(src_path): continue

        with open(src_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Removes: (...) parentheticals, <...> tags, and special bullets
        content = re.sub(r'\(.*?\)|<.*?>|[•·]', '', content, flags=re.DOTALL)
        
        # Find all matches in order
        matches = re.findall(regex_pattern, content, flags=re.DOTALL)
        
        # Clean up internal speaker lines (like E: or A:)
        final_lines = []
        for m in matches:
            clean = " ".join(line.strip() for line in m.splitlines() 
                            if not re.match(r"^[A-Z\.]+\s*:", line.strip()))
            if clean: final_lines.append(clean)

        with open(os.path.join(output_folder, filename), 'w', encoding='utf-8') as f:
            f.write("\n".join(final_lines))

def remove_text(input_folder, num_words_to_remove):
    os.makedirs(input_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        txt_path = os.path.join(input_folder, filename)

        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        word_count = 0
        result_lines = []

        for line in content.splitlines(keepends=True):
            words = line.split()
            if word_count < num_words_to_remove:
                remaining = []
                for w in words:
                    if word_count < num_words_to_remove:
                        word_count += 1
                    else:
                        remaining.append(w)
                if remaining:
                    result_lines.append(" ".join(remaining) + ("\n" if line.endswith("\n") else ""))
            else:
                result_lines.append(line)

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("".join(result_lines))

def _remove_whitespace(text):
    """
    Replaces all forms of whitespace (newlines, tabs, multiple spaces) 
    with a single space character.
    """
    # \s+ matches one or more whitespace characters of any kind
    return re.sub(r'\s+', ' ', text).strip()

def remove_whitespace(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            src_path = os.path.join(input_folder, filename)
            dest_path = os.path.join(output_folder, filename)

            # 1. Read the existing text file
            with open(src_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 2. Clean the content (not the path!)
            cleaned_content = _remove_whitespace(content)

            # 3. Write the cleaned text to the new destination
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(cleaned_content)

if __name__ == "__main__":
    remove_interviewer("private/txt", "private/clean_txt", interviewee_tags=["I", "I.", "B"])
    remove_whitespace("private/clean_txt", "private/clean_txt")
    remove_text("private/clean_txt", 350)