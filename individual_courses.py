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

# Initialize webdriver
service = Service(executable_path=ChromeDriverManager().install())
browser = webdriver.Chrome(service=service)

# Navigate to the specified page
url = "https://curriculum.law.georgetown.edu/course-search/?keyword=the&?term=202410"
browser.get(url)
time.sleep(10)  # give the page some time to load

# Find all elements with class "result result--group-start"
results = browser.find_elements(By.CSS_SELECTOR, ".result.result--group-start")

# To extract data for the first 5 results (or all if there are less than 5)
data = []
for result in results:
    result.click()
    time.sleep(2)

    # Once clicked, wait for the details panel to appear
    panel_div = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".panel.panel--2x.panel--kind-details.panel--visible"))
    )

    # Extracting the data from the specified divs
    section_content = get_text(panel_div, ".section__content")
    course_id = get_text(panel_div, ".text.col-3.detail-code.text--semibold.text--huge")
    course_name = get_text(panel_div, ".text.col-8.detail-title.text--huge")
    course_limit = get_text(panel_div, ".text.detail-enroll_proj")
    prerequisite = get_text(panel_div, ".text.detail-prereqs.margin--default")
    note = get_text(panel_div, ".text.detail-course_note.margin--default")
    recommended = get_text(panel_div, ".text.detail-recommended.margin--default")
    mutually_excluded_courses = get_text(panel_div, ".text.detail-mutually_exclusive.margin--default")
    time_info = get_text(panel_div, ".meet")  # Updated selector

    # Extract professors
    instructors = panel_div.find_elements(By.CSS_SELECTOR, ".instructor-detail")
    professor_names = [""] * 3
    professor_links = [""] * 3
    for i, instructor in enumerate(instructors[:3]):
        professor_names[i] = instructor.text
        try:
            professor_links[i] = instructor.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            professor_links[i] = ""

    data.append({
        "Section Content": section_content,
        "Course ID": course_id,
        "Course Name": course_name,
        "Course Limit": course_limit,
        "Prerequisite": prerequisite,
        "Note": note,
        "Recommended": recommended,
        "Mutually Excluded Courses": mutually_excluded_courses,
        "Professor_1": professor_names[0],
        "Professor_1 Link": professor_links[0],
        "Professor_2": professor_names[1],
        "Professor_2 Link": professor_links[1],
        "Professor_3": professor_names[2],
        "Professor_3 Link": professor_links[2],
        "Time": time_info
    })

# Convert list of dictionaries to DataFrame
df = pd.DataFrame(data)

# Export to CSV
df.to_csv("courses_data.csv", index=False)

# Close the browser after extraction
browser.quit()
