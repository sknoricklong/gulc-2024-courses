import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# Function to safely get text from an element by CSS selector
def get_text(element, selector):
    try:
        return element.find_element(By.CSS_SELECTOR, selector).text
    except:
        return ""


# initialize webdriver
service = Service(executable_path=ChromeDriverManager().install())
browser = webdriver.Chrome(service=service)

# navigate to the specified page
url = "https://curriculum.law.georgetown.edu/course-search/"
browser.get(url)
time.sleep(3)  # give the page some time to load

# locate the text input by its ID and type "the" into it
input_element = browser.find_element(By.ID, "crit-keyword")
input_element.send_keys("the")
time.sleep(10)  # wait for 10 seconds

wait = WebDriverWait(browser, 20)  # increased the wait time to 20 for better reliability

# Extract the group divs
group_divs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".result.result--group-start")))

# Extract details for each group div
data = []
for div in group_divs:
    code = get_text(div, ".result__code")
    title = get_text(div, ".result__title")
    time_ = get_text(div, ".flex--grow")
    professor = get_text(div, ".result__flex--9.text--right")

    data.append({
        'Code': code,
        'Title': title,
        'Time': time_,
        'Professor': professor
    })

# Create a dataframe
df = pd.DataFrame(data)

# Remove "Meets:" from the Time column and "Instructor:" from the Professor column
df['Time'] = df['Time'].str.replace("Meets:", "").str.strip()
df['Professor'] = df['Professor'].str.replace("Instructor:", "").str.strip()

# Close the browser after extraction
browser.quit()

# If you want to save the dataframe to a CSV
df.to_csv("results.csv", index=False)
