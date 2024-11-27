from bs4 import BeautifulSoup 
import pandas as pd
import requests 
from urllib.parse import urljoin 


def artcle_names_url(soup):
    '''
    Function for extracting the names of the articles and the url of the articles from Finn.no
    '''
    articles = soup.find_all('article')
    articlename_and_url = [] 
    for article in articles:
        name = article.find('a').text
        url = article.find('a')['href']
        articlename_and_url.append((name, url))
    return articlename_and_url


def next_page(soup):
    '''
    Function for finding the next page link on the current page of the Finn.no job search.
    '''
    divs = soup.find_all('div', class_='hidden md:block s-text-link') 
    for div in divs:
        links = [a['href'] for a in div.find_all('a', href=True)]

        for a in div.find_all('a', href=True):
            if 'aria-current' in a.attrs:  # Check for aria-current attribute
                current_page = a  # Store the current page <a> tag
                current_page_index = links.index(a['href'])  # Store the index of the current page
                break  # Stop once we find the current page
            
    absolute_links = [urljoin(url, link) for link in links]
    try:
        next_page_link = absolute_links[current_page_index + 1]  # Get the next page URL
    except:
        return None

    return next_page_link


def sort_jobs_by_key_words(key_words, articlename_and_url):
    '''
    Function for sorting out the articles that contain the key words in the article name.
    '''
    # prepare list of key words
    key_words = [word.lower() for word in key_words]
    key_words = set(key_words)
    key_words = list(key_words)

    # set article names to lower 
    for i, elem in enumerate(articlename_and_url):
        articlename_and_url[i] = (elem[0].lower(), elem[1])

    # sort out the articles that contain the key words
    relevant_articles = []
    for article in articlename_and_url:
        for word in key_words:
            if word in article[0]:
                relevant_articles.append(article)
                break

    return relevant_articles


def scrape(url, key_words):
    '''
    Main function for scraping Finn.no for job postings. 
    '''
    # initiate the scraping
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = artcle_names_url(soup)
    # scrae through all the pages
    while True:
        next_page_link = next_page(soup)
        if next_page_link is None:
            break
        response = requests.get(next_page_link)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs += artcle_names_url(soup)

    # sort out the jobs that contain the key words
    jobs = sort_jobs_by_key_words(key_words, jobs)

    return jobs


# EXAMPLE USAGE
# url = 'https://www.finn.no/job/fulltime/search.html'
# jobs = scrape(url, key_words)
