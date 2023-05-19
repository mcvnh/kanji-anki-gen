from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import os.path
from bs4 import BeautifulSoup
import pandas as pd

options = webdriver.ChromeOptions()
options.add_argument('--headless')

driver = webdriver.Chrome(options=options)
driver.get("https://mazii.net/en-US/search/word/javi/私")

time.sleep(3)

words = list(pd.read_csv("output.csv").iloc[:, 1])
search = driver.find_element(By.ID, "search-text-box")


for word in words:
  try:

    file_path = "./mazii/" + word + ".html"

    if not os.path.isfile(file_path):
      search.clear()
      search.send_keys(word)
      search.send_keys(Keys.ENTER)
      time.sleep(2)

      element = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.CLASS_NAME, "box-main-word"))
      )

      soup = BeautifulSoup(element.get_attribute('innerHTML'), 'html.parser')
      soup = soup.select('.example-container')

      f = open(file_path, "w")
      for item in soup:
        f.write(str(item))

      f.close()

  finally:
    print("Done", word)
