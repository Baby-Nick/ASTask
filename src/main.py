import os
import random
import re
import time
from typing import Optional

import requests
import uuid
from bs4 import BeautifulSoup

OUTPUT_FILENAME = "output.html"
DOWNLOAD_IMAGES = False


def remove_numbered_elements(data: str) -> list:
    result = []
    try:
        for item in data:
            if not re.match(r'^\[.*\]$', item):
                result.append(item)
    except Exception as e:
        print(f"An error occurred in remove_numbered_elements: {e}")
    return result


def remove_words_in_parentheses(input_string: str) -> str:
    try:
        return re.sub(r'\([^)]*\)', '', input_string)
    except Exception as e:
        print(f"An error occurred in remove_words_in_parentheses: {e}")
        return input_string  # Return the input string unaltered


def clean_string_from_numbers(input_string: str) -> str:
    try:
        return re.sub(r'\s*\[\d+\]\s*', '', input_string)
    except Exception as e:
        print(f"An error occurred in clean_string_from_numbers: {e}")
        return input_string  # Return the input string unaltered


def html_table_to_dict(table) -> list:
    headers = [header.text.strip() for header in table.find_all('th')]
    rows = table.find_all('tr')[1:]
    print(f"Got {len(headers)} columns")
    print(f"Got {len(rows)} rows")

    data = []

    for row in rows:
        cells = row.find_all('td')
        row_data = {}
        if not cells:
            # case when we have an empty line
            continue
        for i in range(len(headers)):
            if i < len(cells):  # check for case when we have more column headers than columns itself
                if i == 0:  # case when we need to get data from the first row
                    try:
                        row_data[headers[i]] = cells[i].find("a")["href"].replace("/wiki/", "")
                    except (TypeError, KeyError) as e:
                        print(f"An error occurred while getting data from the first row: {e}")
                        row_data[headers[i]] = "_"
                    continue
                if "<br/>" in str(cells[i]):  # case when we have multiple line data
                    cell_strs = list(cells[i].strings)
                    row_data[headers[i]] = [word.strip() for word in cell_strs if word.strip()]
                    row_data[headers[i]] = remove_numbered_elements(row_data[headers[i]])
                else:
                    row_data[headers[i]] = remove_words_in_parentheses(clean_string_from_numbers(cells[i].text.strip()))
        data.append(row_data)
    return data


def get_animal_image(animal_name: str) -> str:
    url = f"https://en.m.wikipedia.org/wiki/{animal_name}"

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, "html.parser")
    images = soup.find_all("img")
    img_src = ""
    if len(images) >= 2:
        found_img = False
        count = 0
        while not found_img and count <= len(images):
            img_src = images[count]["src"][2:]
            if not ".svg" in img_src:
                found_img = True
            count += 1
    if img_src:
        img_src = f"https://{img_src}"
    return img_src


def dict_to_html_table(data: dict) -> str:
    table_html = "<table>"

    # Create table headers
    table_html += "<tr>"
    for key in data[0].keys():
        table_html += f"<th>{key}</th>"
    table_html += "</tr>"

    # Populate table rows
    for row_data in data:
        table_html += "<tr>"
        for value in row_data.values():
            if type(value) is list:
                value = " ".join(value)
            table_html += f"<td>{value}</td>"
        table_html += "</tr>"

    table_html += "</table>"
    return table_html


def download_file(url: str) -> Optional[str]:
    def __get_filetype(input_string):
        last_dot_index = input_string.rfind('.')
        if last_dot_index != -1:
            return input_string[last_dot_index + 1:]
        else:
            return ".jpg"

    def __get_with_retry(url, max_retries=3, timeout_inc=3):
        timeout = 3
        for _ in range(max_retries):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return response
                else:
                    print(f"Received status code {response.status_code}. Retrying...")
            except Exception as e:
                print(f"An error occurred: {e}")

            # Wait for a short period before retrying
            time.sleep(timeout)
            timeout += timeout_inc

        print(
            f"Failed to retrieve data from {url} after {max_retries} retries. {response.status_code}")
        return None

    response = __get_with_retry(url)

    if response:
        filename = f"/tmp/{str(uuid.uuid4())[:8]}.{__get_filetype(url)}"
        with open(filename, 'wb') as file:
            file.write(response.content)
        return filename
    else:
        print(f"Failed to download file from {url}")
        return None


def save_file(data: str, filename: str) -> bool:
    print(f"Saving file {filename}...")
    try:
        tmp_folder = '/tmp/'

        # Ensure the tmp folder exists, create it if necessary
        if not os.path.exists(tmp_folder):
            os.makedirs(tmp_folder)

        file_path = os.path.join(tmp_folder, filename)

        with open(file_path, 'w') as file:
            file.write(data)
            print(f"File '{filename}' saved successfully.")
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def display_animals(data: list):
    for table in data:
        for obj in table:
            animal_name = obj[list(obj.keys())[0]]
            print(f"Processing {animal_name}...")
            if type(obj['Collateral adjective']) is list:
                for adj in obj['Collateral adjective']:
                    print(f"{adj} {animal_name}")
            else:
                print(f"{obj['Collateral adjective']} {animal_name}")
            if DOWNLOAD_IMAGES:
                pic_url = get_animal_image(animal_name=animal_name)
                if not pic_url:
                    print(f"No image url for {animal_name}. Skipping")
                    continue
                else:
                    filename = download_file(url=pic_url)
                    print(f'file://{filename}')
                time.sleep(random.randint(1, 4))  # we need this sleep to decrease chance to get 403 from wiki


if __name__ == '__main__':

    page_link = "https://en.wikipedia.org/wiki/List_of_animal_names"

    print(f"Getting page: {page_link}")
    page = requests.get(url=page_link).content

    print("Loading page to BS")
    soup = BeautifulSoup(page, "html.parser")
    tables = soup.find_all("table")

    print(f"Got {len(tables)} tables")
    output = []
    for i, table in enumerate(tables):
        print(f"Table: #{i}")
        res = html_table_to_dict(table=table)
        if res:
            output.append(res)
    display_animals(output)

    # build html table
    save_file(
        data="\n".join([dict_to_html_table(table) for table in output]),
        filename=OUTPUT_FILENAME
    )
