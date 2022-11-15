# product page parsing
import requests
from bs4 import BeautifulSoup
import json
import csv
import os

def get_url(url, accept="*/*", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"):
    headers = {
        "Accept": f"{accept}",
        "User-Agent": f"{user_agent}"
    }
    return requests.get(url,headers=headers)

# creating a page code file
req = get_url(url="https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie",
              accept="*/*",
              user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")
src = req.text

# save page code and return open document
def create_read_file(name, src):

    with open(f"{name}", "w", encoding="utf-8") as file:
        file.write(src)

    with open(f"{name}", "r", encoding="utf-8") as file:
        src = file.read()

    return src

# creating a folder with the code of all pages
mypath = "data"
if not os.path.isdir(mypath):
   os.mkdir(mypath)

# creating a file with the code of the main page
src = create_read_file(f"{mypath}/index.html", src)

soup = BeautifulSoup(src, "lxml")
all_products_href = soup.find_all(class_= "mzr-tc-group-item-href")

all_categories_dict = {}
for el in all_products_href:
    item_text = el.text
    item_href = "https://health-diet.ru" + el.get("href")
    product_name = el.get("title")
    product_price = el.get("price")
    product_description = el.get("description")
    product_image = el.get("image")
    all_categories_dict[item_text] = item_href

# saving dictionary in json file
with open(f"{mypath}/all_categories_dict.json", "w", encoding="utf-8") as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

# open each page and save to file
with open(f"{mypath}/all_categories_dict.json", encoding="utf-8") as file:
    all_categories = json.load(file)

# page number entry
iteration_count = int(len(all_categories)) - 1
count = 0
print ( f"Total iterations: { iteration_count } " )

for category_name, category_href in all_categories.items():

    # change to _ for convenience
    rep = [",", " ", "-", "'"]
    for item in rep:
        if item in category_name:
            category_name = category_name.replace(item, "_")
    req = get_url(url=category_href)
    src = req.text

    # work with every page
    src = create_read_file(f"{mypath}/{count}_{category_name}.html", src)
    soup = BeautifulSoup(src, "lxml")

    # check for empty page
    alert_block = soup.find(class_="uk-alert-danger")
    if alert_block is not None:
        continue

    # collecting headlines
    table_head = soup.find(class_="mzr-tc-group-table").find("tr").find_all("th")
    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text

    # collect data from subsite
    products_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")
    product_info = []

    for item in products_data:
        product_tds = item.find_all("td")
        title = product_tds[0].find("a").text
        calories = product_tds[1].text
        proteins = product_tds[2].text
        fats = product_tds[3].text
        carbohydrates = product_tds[4].text
        product_info.append(
            {
                "Title": title,
                "Calories": calories,
                "Proteins": proteins,
                "Fats": fats,
                "Carbohydrates": carbohydrates
            }
        )
        # write in csv file
        with open(f"{mypath}/{count}_{category_name}.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    title,
                    calories,
                    proteins,
                    fats,
                    carbohydrates
                )
            )

    with open(f"{mypath}/{count}_{category_name}.json", "a", encoding="utf-8") as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)
    count += 1

    print(f"# Iterate {count}. {category_name} recorded...")
    iteration_count = iteration_count - 1

    if iteration_count == 0:
        print("Job completed")
        break
    print(f"Iterations left: {iteration_count}")