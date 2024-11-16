import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import spacy
from itertools import chain
import wikipediaapi
import random

nlp = spacy.load("en_core_web_sm")

wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent="JISEBI-Scraper/1.0 (https://example.com; contact@example.com)"
)

def get_page_content(url, retries=3, timeout=30):
    """Retrieve web page content with retries on timeout."""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:  
                wait_time = 2 ** attempt + random.uniform(0, 1)  
                print(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed to retrieve content from {url} after {retries} attempts.")
                return None

def is_term_in_wikipedia(term, retries=3, timeout=10):
    """Check if a term exists on Wikipedia with retries on timeout."""
    for attempt in range(retries):
        try:
            page = wiki_wiki.page(term)
            return page.exists()
        except requests.exceptions.ReadTimeout:
            if attempt < retries - 1:  
                wait_time = 2 ** attempt + random.uniform(0, 1) 
                print(f"Timeout for term '{term}'. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed to verify term '{term}' on Wikipedia after {retries} attempts.")
                return False

def extract_terms(text, pos_filters, phrase_types=None):
    """Extract specific terms from text based on POS and phrase filters."""
    doc = nlp(text)
    matched_terms = [token.text for token in doc if token.pos_ in pos_filters]

    if phrase_types:
        words = [token.text for token in doc]
        bigrams = zip(words, words[1:])
        trigrams = zip(words, words[1:], words[2:])
        
        for ngram in chain(bigrams, trigrams):
            phrase = " ".join(ngram)
            if all(nlp(word)[0].pos_ in phrase_types for word in ngram):
                matched_terms.append(phrase)

    matched_terms = list(set(matched_terms))
    validated_terms = [term for term in matched_terms if is_term_in_wikipedia(term)]
    return validated_terms

def parse_abstract(abstract_text):
    """Split abstract text into sections based on patterns."""
    patterns = {
        'Background': r'(Background|Introduction):(.*?)(Objective:|Methods:|Results:|Conclusion:|$)',
        'Objective': r'(Objective|Purpose):(.*?)(Methods:|Results:|Conclusion:|$)',
        'Methods': r'(Methods|Approach|Procedure):(.*?)(Results:|Conclusion:|$)',
        'Results': r'(Results|Findings):(.*?)(Conclusion:|$)',
        'Conclusion': r'(Conclusion|Summary):(.*?)(Keywords:|$)',
    }

    sections = {}
    for section, pattern in patterns.items():
        match = re.search(pattern, abstract_text, re.DOTALL)
        sections[section] = match.group(2).strip() if match else 'N/A'

    if sections.get('Background', 'N/A') != 'N/A':
        sections['Background'] = extract_terms(sections['Background'], pos_filters=['NOUN'], phrase_types=['ADJ', 'NOUN'])
    if sections.get('Objective', 'N/A') != 'N/A':
        sections['Objective'] = extract_terms(sections['Objective'], pos_filters=['VERB', 'NOUN'], phrase_types=['ADJ', 'NOUN'])
    if sections.get('Methods', 'N/A') != 'N/A':
        sections['Methods'] = extract_terms(sections['Methods'], pos_filters=['VERB', 'NOUN'])
    if sections.get('Results', 'N/A') != 'N/A':
        sections['Results'] = extract_terms(sections['Results'], pos_filters=['NOUN'], phrase_types=['ADJ', 'NOUN'])
    if sections.get('Conclusion', 'N/A') != 'N/A':
        sections['Conclusion'] = extract_terms(sections['Conclusion'], pos_filters=['VERB', 'NOUN'])

    return sections

def scrape_article_page(url):
    """Scrape information from an individual article page."""
    content = get_page_content(url)
    if content is None:
        return None

    soup = BeautifulSoup(content, 'html.parser')
    abstract_tag = soup.find('section', class_='abstract text-justify')

    if abstract_tag:
        abstract_sections = parse_abstract(abstract_tag.text.strip())
    else:
        abstract_sections = {
            'Background': 'N/A', 'Objective': 'N/A', 
            'Methods': [], 'Results': 'N/A', 
            'Conclusion': 'N/A', 'Keywords': 'N/A'
        }

    authors_tag = soup.find('ul', class_='authors')
    authors = ', '.join([author.find('a').text.strip() for author in authors_tag.find_all('li')]) if authors_tag else 'N/A'

    year_tag = soup.find('div', class_='published')
    year = year_tag.text.strip() if year_tag else 'N/A'

    pdf_link = 'N/A'
    pdf_tag = soup.select_one('ul.galleys_links li a.obj_galley_link.pdf')
    if pdf_tag and 'href' in pdf_tag.attrs:
        pdf_url = pdf_tag['href']
        pdf_link = pdf_url if pdf_url.startswith('http') else 'https://e-journal.unair.ac.id' + pdf_url

    return {
        'Background': abstract_sections['Background'],
        'Objective': abstract_sections['Objective'],
        'Methods': abstract_sections['Methods'],
        'Results': abstract_sections['Results'],
        'Conclusion': abstract_sections['Conclusion'],
        'Authors': authors,
        'Year': year,
        'PDF Link': pdf_link
    }

def scrape_journal_page(url):
    """Scrape articles from a journal issue page."""
    content = get_page_content(url)
    if content is None:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    articles = soup.find_all('div', class_='obj_article_summary')
    journal_data = []

    for article in articles:
        title_tag = article.find('h3', class_='title').find('a')
        if title_tag and title_tag['href']:
            title = title_tag.text.strip()
            article_url = title_tag['href']
            if not article_url.startswith('http'):
                article_url = 'https://e-journal.unair.ac.id' + article_url

            print(f"Scraping article: {article_url}")
            article_data = scrape_article_page(article_url)
            if article_data:
                article_data['Title'] = title
                journal_data.append(article_data)

            time.sleep(2)

    return journal_data

def scrape_multiple_pages(limit=12):
    """Scrape multiple journal archive pages."""
    base_url = 'https://e-journal.unair.ac.id/JISEBI/issue/archive'
    content = get_page_content(base_url)

    if content is None:
        print("Failed to load archive page.")
        return

    soup = BeautifulSoup(content, 'html.parser')
    issues = soup.find_all('a', href=True, class_='title')
    all_journal_data = []

    for i, issue in enumerate(issues):
        if i >= limit:
            break

        issue_url = issue['href']
        if not issue_url.startswith('http'):
            issue_url = 'https://e-journal.unair.ac.id' + issue_url

        print(f"Scraping issue: {issue_url}")
        journal_data = scrape_journal_page(issue_url)
        all_journal_data.extend(journal_data)

    if all_journal_data:
        df = pd.DataFrame(all_journal_data)
        df.to_csv('journal_data_filtered.csv', index=False)
        print("Scraping completed and saved to journal_data_filtered.csv")
    else:
        print("No data scraped.")

if __name__ == '__main__':
    scrape_multiple_pages(limit=12)
