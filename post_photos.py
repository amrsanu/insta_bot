from instabot import Bot
import os
from PIL import Image, ImageOps, ImageFilter
import shutil
import time
import openai
import json
from dotenv import load_dotenv
import midjourney

load_dotenv()

def add_frame(
    image_path, resized_image_path, frame_size=10, zoom_factor=1.2, blur_radius=15
):
    print("Adding frame...")
    # Open the image
    image = Image.open(image_path)

    max_dimension = max(image.width, image.height)
    frame_width = max_dimension + 2 * frame_size
    frame_height = max_dimension + 2 * frame_size
    resized_image = image

    zoomed_image = resized_image.resize(
        (int(max_dimension * zoom_factor), int(max_dimension * zoom_factor))
    )
    blurred_image = zoomed_image.filter(ImageFilter.GaussianBlur(blur_radius))
    framed_image = Image.new(blurred_image.mode, (frame_width, frame_height))

    bg_x_offset = int((frame_width - blurred_image.width) / 2)
    bg_y_offset = int((frame_height - blurred_image.height) / 2)
    framed_image.paste(blurred_image, (bg_x_offset, bg_y_offset))

    img_x_offset = int((frame_width - resized_image.width) / 2)
    img_y_offset = int((frame_height - resized_image.height) / 2)
    framed_image.paste(resized_image, (img_x_offset, img_y_offset))

    framed_image = framed_image.convert("RGB")
    framed_image.save(resized_image_path, "JPEG")


def get_caption(url):
    """To create a caption using openai chatgpt4"""

    print("Get caption for  url: " + url)
    # Add openAI chatgpt4 key below to get the caption
    openai.api_key = os.getenv("GPT4_KEY")

    prompt = f"Generate a quote related to given image, also add few hashtags for instagram - {url}"

    response = openai.ChatCompletion.create(
        model="gpt-4",  # Specify the ChatGPT-4 model
        messages=[
            {"role": "system", "content": "You are"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=40,
        temperature=0.7,
    )

    summary = response.choices[0].message.content.strip()
    summary = "#".join(summary.split("#")[:-1])
    # print(f"Generated Summary: {summary}")
    return summary


def get_image_url():
    """Updates te active_json file by popping one image path
    Updates the uploaded_json file by appending the image path

    returns: image_path"""

    print("Getting image url...")
    images = []
    uploaded_images = []

    with open("active_images.json", "r", encoding="utf-8") as file:
        images = json.load(file)

    image_path = images.pop(0)

    with open("active_images.json", "w", encoding="utf-8") as outfile:
        json.dump(images, outfile, indent=4)

    if os.path.exists("uploaded_images.json"):
        with open("uploaded_images.json", "r", encoding="utf-8") as file:
            uploaded_images = json.load(file)

    uploaded_images.append(image_path)
    with open("uploaded_images.json", "w", encoding="utf-8") as outfile:
        json.dump(uploaded_images, outfile, indent=4)

    return image_path


def post(image_url):
    """Will post a photo on instagram"""

    print("Initiating post on instagram")
    # https://cdn.midjourney.com/015391d8-b2c9-42ab-8521-fa47fce95f30/0_2.png
    image_path = f"{image_url.split('/')[-2]}.png"
    resized_image_path = f"resize_{image_path}"
    image_path = os.path.join("images", image_path)
    try:
        if os.path.exists("config"):
            shutil.rmtree("config")
        if os.path.exists(resized_image_path):
            os.remove(resized_image_path)
        # framed_image.jpg.REMOVE_ME

        bot = Bot()
        bot.login(username="hybridharmony.ai", password="Root@123")

        caption = get_caption(image_url)
        caption = f"{caption} #hybridharmony #ai #creativity"
        print(caption)

        bot.send_message(caption, "amrsanu")
        add_frame(image_path, resized_image_path, 10, 1.2, 5)

        is_uploaded = bot.upload_photo(resized_image_path, caption=caption)
        # print(f"Is Uploaded: {is_uploaded}")
        time.sleep(5)

    except Exception as ex:
        print(f"An error occurred: {ex}")
    finally:
        print("Logging out...")
        bot.logout()
        time.sleep(5)
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(resized_image_path):
            os.remove(resized_image_path)
        if os.path.exists(f"{resized_image_path}.REMOVE_ME"):
            os.remove(f"{resized_image_path}.REMOVE_ME")


if __name__ == "__main__":
    images = []
    if not os.path.exists("images"):
        os.mkdir("images")

    if os.path.exists("active_images.json"):
        with open("active_images.json", "r", encoding="utf-8") as file:
            images = json.load(file)

    if len(images) == 0:
        midjourney.invoke_midjourney()

    image_url = get_image_url()

    post(image_url)
    print("Posted image successfully.")
