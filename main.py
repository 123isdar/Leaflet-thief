import requests
from bs4 import BeautifulSoup
from subprocess import call


def extract_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True)]
        return links
    except Exception as e:
        print(f"Error: {e}")
        return []

def sort_and_remove_duplicates(links, target_word):
    unique_links = list(set(links))  # Remove duplicates
    sorted_links = sorted([link for link in unique_links if target_word.lower() in link.lower()])
    return sorted_links

def remove_old_links(sorted_links, old_links_filename):
    try:
        with open(old_links_filename, 'r') as old_links_file:
            old_links = set(line.strip() for line in old_links_file)
        sorted_links = [link for link in sorted_links if link not in old_links]
    except Exception as e:
        print(f"Error reading old links file: {e}")
    return sorted_links

def save_to_text_file(links, filename):
    with open(filename, 'w') as file:
        for link in links:
            file.write(link + '\n')

def append_to_old_links(links, old_links_filename):
    try:
        with open(old_links_filename, 'a') as old_links_file:
            for link in links:
                old_links_file.write(link + '\n')
    except Exception as e:
        print(f"Error appending to old links file: {e}")

if __name__ == "__main__":
    target_url = "https://kaotic.com"  # Replace with your desired URL
    word_to_sort_by = ""  # Replace with the word you want to sort links by
    output_filename = "sorted_unique_links.txt"
    old_links_filename = "old_links.txt"  # Replace with the old links file name

    all_links = extract_links(target_url)
    sorted_unique_links = sort_and_remove_duplicates(all_links, word_to_sort_by)
    sorted_unique_links = remove_old_links(sorted_unique_links, old_links_filename)

    save_to_text_file(sorted_unique_links, output_filename)
    append_to_old_links(sorted_unique_links, old_links_filename)

    print(f"Unique links containing '{word_to_sort_by}' (excluding old links) have been sorted and saved to '{output_filename}'.")
    print(f"Links have been added to '{old_links_filename}'.")


file_path = 'sorted_unique_links.txt'

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

num_lines = len(lines)
if num_lines!=0 :
    print("run")
else:
    print("Done")
