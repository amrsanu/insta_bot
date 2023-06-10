"""to download all the images from midjournery and add a caption"""
import os
import json
import openai
from bs4 import BeautifulSoup
import requests


def download_image(url):
    """download the image from url as png"""

    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    with open(os.path.join("images", url.split("/")[-2] + ".png"), "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


def get_caption(url):
    """To create a caption using openai chatgpt4"""

    openai.api_key = os.getenv("GPT4_KEY")

    prompt = f"Generate a quote related to given image, also add few hashtags for instagram - {url}"

    ai_response = openai.ChatCompletion.create(
        model="gpt-4",  # Specify the ChatGPT-4 model
        messages=[
            {"role": "system", "content": "You are"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=40,
        temperature=0.7,
    )

    summary = ai_response.choices[0].message.content.strip()
    summary = "#".join(summary.split("#")[:-1])
    # print(f"Generated Summary: {summary}")
    return summary


def invoke_midjourney():
    """to invoke midjourney and get all the image links"""
    # Send a GET request to the website
    try:
        url = "https://www.midjourney.com/showcase/recent/"
        response = requests.get(url, timeout=60)

        # Create a BeautifulSoup object
        soup = BeautifulSoup(response.content, "html.parser")
        script_element = soup.find("script", id="__NEXT_DATA__")

        json_content = json.loads(script_element.contents[0])["props"]["pageProps"][
            "jobs"
        ]

        images = []
        if os.path.exists("active_images.json"):
            with open("active_images.json", "r", encoding="utf-8") as file:
                images = json.load(file)

        for element in json_content:
            url = element["image_paths"][0]
            images.append(url)
            # time.sleep(5)
            download_image(element["image_paths"][0])

        with open("active_images.json", "w+", encoding="utf-8") as outfile:
            json.dump(images, outfile, indent=4)
    except Exception as ex:
        raise ValueError(f"Error downloading active images: {ex}")

    return True


if __name__ == "__main__":
    invoke_midjourney()
