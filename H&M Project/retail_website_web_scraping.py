import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException

# Final version of the code.

# Set up Chrome browser options to start maximized
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options)

# Open the main page of the retail website
driver.get("the website link I used")

# Lists to store main category URLs and names
main_cat_urls = []
main_cat_names = []

# Find and store the main categories (the upper categories on the website)
main_cat_name_xpath = "//ul[@class='MLEL']//li/a[@class='CGae __9y2v vEfo']"
main_cat_elements = driver.find_elements(By.XPATH, main_cat_name_xpath)[3:4]

# Iterate through each element found to get the main category URLs and names
for element in main_cat_elements:
    main_cat_url = element.get_attribute("href")
    main_cat_name = element.get_attribute("innerText")
    main_cat_urls.append(main_cat_url)
    main_cat_names.append(main_cat_name)

# Visit each main category page
for main_cat_url, main_cat_name in zip(main_cat_urls, main_cat_names):

    driver.get(main_cat_url)
    time.sleep(0.5)

    # Gather subcategory names and URLs from each main category
    cat_urls = []
    cat_names = []
    cat_elements_xpath = "//ul[@class='oD6_']/li/a"
    cat_elements = driver.find_elements(By.XPATH, cat_elements_xpath)[2:4]

    for element in cat_elements:
        cat_url = element.get_attribute("href")
        cat_name = element.get_attribute("innerText")
        cat_urls.append(cat_url)
        cat_names.append(cat_name)

    # Check if there are subcategories or extra subcategories and collect their links
    all_urls = []
    all_cat_names = []
    all_sub_cat_names = []
    all_extra_sub_cat_names = []

    for cat_url, cat_name in zip(cat_urls, cat_names):
        driver.get(cat_url)

        # XPath to find extra subcategories if available
        extra_sub_cat_xpath = "//ul[@class='oD6_']/li/a[@class='CGae mYRh vEfo C7LF ntl6']/following-sibling::ul/li/ul/li/a"
        extra_sub_cat_elements = driver.find_elements(By.XPATH, extra_sub_cat_xpath)

        inner_index = 0

        if extra_sub_cat_elements:

            # Loop through extra subcategories and collect their URLs and names
            for e in extra_sub_cat_elements:
                extra_sub_cat_url = e.get_attribute("href")
                extra_sub_cat_name = e.get_attribute("innerText")

                all_urls.append(extra_sub_cat_url)
                all_extra_sub_cat_names.append(extra_sub_cat_name)

                all_cat_names.append(cat_name)

                sub_cat_xpath = "//ul[@class='oD6_']/li/a[@class='CGae mYRh vEfo C7LF ntl6']/following-sibling::ul/li/a"
                sub_cat_elements = driver.find_elements(By.XPATH, sub_cat_xpath)

                # Keep track of the inner subcategory index
                while inner_index < len(sub_cat_elements):
                    x = []

                    # Collect subcategory names and URLs
                    sub_cat_element = sub_cat_elements[inner_index]
                    sub_cat_url = sub_cat_element.get_attribute("href")
                    sub_cat_name = sub_cat_element.get_attribute("innerText")

                    x.append(sub_cat_name)

                    for name in x:
                        category_xpath = f"//a[text()='{name}']/following-sibling::ul/li"

                        sub_categories = driver.find_elements(By.XPATH, category_xpath)

                        sub_cat_count = len(sub_categories)

                        # Append subcategory names to the list based on the count of extra subcategories
                        all_sub_cat_names.extend([sub_cat_name] * sub_cat_count)

                        inner_index += 1
                        break
                    break

        else:
            # If no extra subcategories, handle regular subcategories
            sub_cat_xpath = "//ul[@class='oD6_']/li/a[@class='CGae mYRh vEfo C7LF ntl6']/following-sibling::ul/li/a"
            sub_cat_elements = driver.find_elements(By.XPATH, sub_cat_xpath)

            if sub_cat_elements:
                for el in sub_cat_elements:
                    sub_cat_url = el.get_attribute("href")
                    sub_cat_name = el.get_attribute("innerText")

                    all_urls.append(sub_cat_url)
                    all_cat_names.append(cat_name)
                    all_sub_cat_names.append(sub_cat_name)
                    all_extra_sub_cat_names.append("-")
            else:
                all_urls.append(cat_url)
                all_cat_names.append(cat_name)
                all_sub_cat_names.append("-")
                all_extra_sub_cat_names.append("-")

    # Get the maximum number of pages for each category
    max_pages = []
    max_pages_dict = {}

    for url in all_urls:
        driver.get(url)
        time.sleep(0.5)

        last_page_xpath = "//ul[@class='ed2eb5']//li/following-sibling::li[position() = last() -1]"
        max_pagex = driver.find_elements(By.XPATH, last_page_xpath)

        if len(max_pagex) == 0:
            max_page = "1"
            max_pages.append(int(max_page))
        else:
            for element in max_pagex:
                page_name = element.get_attribute("innerText")
                max_pages.append(int(page_name))

    # Create a list to store the scraped data
    data = []

    for url, max_pagee, sub_cat_name, all_cat_name, extra_sub_cat_name in zip(all_urls, max_pages, all_sub_cat_names,
                                                                              all_cat_names, all_extra_sub_cat_names):

        for i in range(1, max_pagee + 1):

            driver.get(url + f"?page={i}")
            time.sleep(0.5)

            # XPath for finding the list of products
            max_product_xpath = "//ul[@class='c654b4 df4579 da88ea ef6a17 bd967e e78762 c02801 a72393 XuCf']/li"
            max_product_elements = driver.find_elements(By.XPATH, max_product_xpath)

            for a in range(0, len(max_product_elements) + 1):

                try:
                    # Click the next button to go through the images of products
                    next_button = driver.find_elements(By.XPATH, "//button[@aria-label='Next']")[a]
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    next_button.click()
                    time.sleep(0.5)

                    # Get the image source of the product
                    img_tag_xpath = "//li[@class='splide__slide is-active is-visible']//img"
                    img_tag = driver.find_elements(By.XPATH, img_tag_xpath)[a]
                    img_src = img_tag.get_attribute("src")

                    # Get the color of the product
                    parent_xpath = "//div[@class='b86b62 ec329a']"
                    middle_xpath = ".//div[@class='dd8e72 d458b9']"
                    child_xpath = ".//ul//li[1]"

                    parent_elements = driver.find_elements(By.XPATH, parent_xpath)[a]

                    middle_element = parent_elements.find_elements(By.XPATH, middle_xpath)
                    if middle_element:
                        for mid_element in middle_element:
                            li_elements = mid_element.find_elements(By.XPATH, child_xpath)
                            if li_elements:
                                product_colors = li_elements[0].get_attribute("innerText")
                            else:
                                product_colors = "-"
                    else:
                        product_colors = "-"

                    # Get the name of the product
                    product_name_xpath = "//div[@class='b86b62 ec329a']//h2"
                    product_name_elements = driver.find_elements(By.XPATH, product_name_xpath)[a]
                    product_names = product_name_elements.get_attribute("innerText")

                    # Extract the price and convert it to float
                    costs_element_xpath = "//div[@class='b86b62 ec329a']//span[@class='aeecde ac3d9e b19650']"
                    costs_elements = driver.find_elements(By.XPATH, costs_element_xpath)[a]
                    costs = costs_elements.get_attribute("innerText")
                    costs = re.sub(r'[^\d,]', '', costs).replace(",", ".")
                    costs = float(costs)

                    # Add the data to the list
                    data.append([product_names, img_src, product_colors, main_cat_name, all_cat_name, sub_cat_name,
                                 extra_sub_cat_name, costs])

                    dict_x = {
                        "name": product_names,
                        "img": img_src,
                        "main_cat_name": main_cat_name,
                        "cat_name": all_cat_name,
                        "sub_cat_name": sub_cat_name,
                        "extra_sub_cat_name": extra_sub_cat_name,
                        "product_color": product_colors,
                        "costs": costs,
                    }
                    print(dict_x)
                except:
                    break

    # Convert the data to a DataFrame and export it to a CSV file
    df = pd.DataFrame(data, columns=["Product Name", "Image", "Color", "Main Category", "Category", "Subcategory",
                                     "Extra Subcategory", "Price"])
    df.to_csv("all_data.csv", index=False)

# Quit the browser
driver.quit()
