import requests
import json
import deepl
import time

from dotenv import load_dotenv
load_dotenv()

import os
translator = deepl.Translator(os.environ["DEEPL_API_KEY"])

from bs4 import BeautifulSoup

from datetime import date
today = date.today().strftime("%Y/%m/%d")

URL = "https://arxiv.org/list/gr-qc/new"
AUTHORS = [l.strip() for l in os.environ["AUTHORS"].split(",")]
TEAMS_WEBHOOK_URL = os.environ["TEAMS_WEBHOOK_URL"]

count = 0

def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text

def extract_elements(html, keywords):
    soup = BeautifulSoup(html, "html.parser")

    results = [{"number": ""}]

    for dd in soup.find_all("dd"):
        authors_div = dd.find("div", class_="list-authors")

        for a in authors_div.find_all("a"):

            for keyword in keywords:
                if keyword in a.get_text(strip=True) and not "Replacement" in dd.find_previous_sibling("h3").get_text(strip=True):

                    global count
                    count = count + 1

                    dt = dd.find_previous_sibling("dt")
                    number = dt.find("a", title="Abstract").get("id")
                    title = dd.find("div", class_="list-title").get_text(strip=True).replace("Title:", "")
                    authors = dd.find("div", class_="list-authors").get_text()
                    abstract_0 = dd.find("p", class_="mathjax").get_text(strip=True)
                    abstract = format_doc(abstract_0)
                    abstract_translated = translate(abstract)

                    for k in range(count):
                        if not number in results[k]['number']:
                            results.append({
                                "number": number,
                                "title": title,
                                "authors": authors,
                                "abstract": abstract,
                                "abstract_translated": abstract_translated
                            })  
                        else:
                            count = count - 1

    return results

def format_doc(content):
    content_fin = []
    content_1 = content.replace('- ','-')\
                .replace('et al. ', 'et al., ').replace('et al.\n','et al., ')\
                .replace('e.g. ','e.g.,').replace('c.f. ','c.f.,')\
                .replace('Eq. ','Eq.').replace('Eqs. ','Eqs.')\
                .replace('Fig. ','Fig.').replace('Figs. ','Figs.').replace('FIG. ','FIG.')\
                .replace('Ref. ','Ref.').replace('Ref.\n','Ref.').replace('Refs. ','Refs.')\
                .replace('Sec. ','Sec.')\
                .replace('∇iRjk',' ∇iRjk ').replace('∇i',' ∇i ')\
                .replace('Abstract\n', 'Abstract_kaigyo')\
                .replace('~Introduction\n', '~Introduction_kaigyo')\
                .replace('~Conclusions\n', '~Conclusions_kaigyo')
    content_2 = content_1.replace('\n', ' ').replace('\r', ' ')\
                .replace('\\par', '%%%%').replace('%%%% ', '%%%%\n\n')\
                .replace('_kaigyo', '\n\n')

    list = content_2.split('. ')
    content_fin = ".\n\n".join(list)
    return content_fin

def translate(sentences):
    sentenses_translated = translator.translate_text(sentences, source_lang='EN', target_lang='JA', glossary='164afdfb-db5e-4f93-82b5-ce54311e1c32').text
    return sentenses_translated

def main():

    html = fetch_html(URL)
    elements = extract_elements(html, AUTHORS)

    initial_message = {
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "msteams": {"width": "Full"},
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "↓ " + " " + today + " " + " ↓",
                                "wrap": True,
                                "weight": "Bolder",
                                "size": "Large"
                            }
                        ],
                    },
                }
            ]
        }
    
    requests.post(
            url=TEAMS_WEBHOOK_URL,
            data=json.dumps(initial_message),
            headers={"Content-Type": "application/json"},
    )

    time.sleep(5)

    for i in range(count):
        message = {
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "msteams": {"width": "Full"},
                        "version": "1.4",
                        "body": [
                            {
                                "type": "ActionSet",
                                "actions": [
                                    {
                                        "type": "Action.OpenUrl",
                                        "title": 'arXiv:' + elements[i+1]['number'],
                                        "url": 'https://arxiv.org/abs/' + elements[i+1]['number']                                    }
                                ]
                            },
                            {
                                "type": "TextBlock",
                                "text": elements[i+1]['title'],
                                "size": "Large",
                                "weight": "Bolder",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": elements[i+1]['authors'],
                                "color": "Accent",
                                "wrap": True,
                            },
                            {
                                "type": "TextBlock",
                                "text": elements[i+1]['abstract'],
                                "wrap": True,
                                "spacing": "ExtraLarge",
                                "separator": True
                            },
                            {
                                "type": "TextBlock",
                                "text": elements[i+1]['abstract_translated'],
                                "wrap": True,
                                "spacing": "ExtraLarge",
                                "separator": True
                            }
                        ],
                    },
                }
            ]
        }

        requests.post(
            url=TEAMS_WEBHOOK_URL,
            data=json.dumps(message),
            headers={"Content-Type": "application/json"},
        )

if __name__ == "__main__":
    main()