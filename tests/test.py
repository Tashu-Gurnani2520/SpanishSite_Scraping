from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from google.cloud import translate_v2 as translate
from dotenv import load_dotenv
from collections import Counter
import re

# Load the environment variables from the .env file
load_dotenv()

# Set up Selenium
options = ChromeOptions()
options.set_capability('sessionName', 'BStack Sample Test')
driver = webdriver.Chrome(options=options)

# Navigate to the page 
main_page_url = "https://elpais.com/"  
driver.get(main_page_url)

# Wait until article links are visible (with extended waiting time)
WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
)

# Find all article links (inside <h2> )
article_links = driver.find_elements(By.XPATH, "//h2[@class='c_t c_t-i ']/a")

# Extract the URLs that end with .html
urls = [link.get_attribute("href") for link in article_links if link.get_attribute("href") and link.get_attribute("href").endswith(".html")]

# List of URLs (replace 'urls' with the actual list of article URLs)
article_urls = urls[:5]

# List to store article titles
article_titles = []

# Iterate through each article URL
for url in article_urls:
    print(f"Processing URL: {url}")
    driver.get(url)

    try:
        # Wait for the title element to load and extract the text
        title_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > article > header > div.a_e_txt._df"))  # Adjust selector as needed
        )
        article_title = title_element.text
        article_titles.append(article_title)
        print(f"Title extracted: {article_title}")

        article_content = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.a_c.clearfix[data-dtm-region='articulo_cuerpo']"))
        )
        article1_content = driver.execute_script("return arguments[0].textContent;", article_content)
    except Exception as e:
        print(f"Failed to extract title or content from {url}: {e}")

# Function to handle translation using Google Cloud Translation API
def translate_titles(article_titles):
    # Initialize the Cloud Translation client
    client = translate.Client()

    translated_titles = []
    for title in article_titles:
        # Translate each title
        result = client.translate(title, target_language='en', source_language='es')
        translated_titles.append(result['translatedText'])

    return translated_titles

# Call the function and print the translated titles
translated_titles = translate_titles(article_titles)
print("Translated Titles:")
for translated_title in translated_titles:
    # Log the translated title to the browser's console
    driver.execute_script(f'console.log("Translated Title: {translated_title}");')

# Function to analyze word frequencies
def analyze_repeated_words(titles):
    # Combine all titles into a single string
    all_text = " ".join(titles)
    
    # Use regex to split the text into words and normalize them to lowercase
    words = re.findall(r'\b\w+\b', all_text.lower())
    
    # Count the frequency of each word
    word_count = Counter(words)
    print(word_count)
    # Filter out words that appear more than twice
    repeated_words = {word: count for word, count in word_count.items() if count > 2}
    
    return repeated_words

# Analyze repeated words
repeated_words = analyze_repeated_words(translated_titles)

# Print the repeated words and their count
print("Repeated Words:")
for word, count in repeated_words.items():
    driver.execute_script(f'console.log("Repeated words:- {word} - {count}");')
# Close the browser
driver.quit()
