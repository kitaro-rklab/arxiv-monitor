import requests
import json
from bs4 import BeautifulSoup

URL = "https://www.deepl.com/ja/glossary/1d131f55-d047-4207-a58c-53fb269646c2"

def fetch_html(url):
	headers = {
		"User-Agent": "Mozilla/5.0"
	}
	response = requests.get(url, headers=headers, timeout=10)
	response.raise_for_status()
	return response.text

def extract_dictionary(html):
	soup = BeautifulSoup(html, "html.parser")

	results = []

	for div in soup.find_all("div"):
		item_div = div.find("div", class_="items-center")
		EN = item_div.find("span", class_="px-2.5").get_text()
		print(EN)
		JA = EN.find("span", class_="px-2.5").get_text()
		results.append({
			"english": EN,
			"japanese": JA
		})
	return results

def main():
	print(extract_dictionary(fetch_html(URL)))

if __name__ == "__main__":
    main()