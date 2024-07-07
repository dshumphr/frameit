import argparse
import os
import requests
from datetime import datetime
import time
import fal_client

def download_image(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"{save_path}")
    else:
        raise RuntimeError("Failed to download image.")

def generate_timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")

def generate_filename(directory, timestamp, suffix):
    filename = f"{directory}/image_{timestamp}{suffix}"
    return filename

def generate_sonnet(prompt):
    import anthropic

    A_KEY = os.getenv('ANTHROPIC_API_KEY')
    if not A_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")

    client = anthropic.Anthropic(api_key=A_KEY)
    sonnet_prompt = f"""
    Let's fix up some prompts for AI art generation. Here are some examples:
    Input prompt: castle
    Improved prompt: A medieval castle looms, overlooking the sea, painted in the style of Vermeer

    Input prompt: Gandalf, cyberpunk
    Improved prompt: Gandalf the wizard holds his staff glowing staff, cyberpunk robes, Lord of the Rings, realistically rendered, neon lights, futuristic cyberpunk

    Input prompt: Ironman
    Improved prompt: Ironman, closeup, retro poster, shining armour

    Now you try. Improve "{prompt}". Return the new prompt only.
    """

    response = client.messages.create(
        max_tokens=1024,
        model="claude-3-5-sonnet-20240620",
        messages=[
            {"role": "user", "content": sonnet_prompt}
        ]
    )

    sonneted = response.content[0].text.strip()
    return sonneted

# Stolen from reddit: https://www.reddit.com/r/StableDiffusion/comments/xwu5od/about_that_huge_long_negative_prompt_list/
NEG = '((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), out of frame, extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck)))'

def save_prompt(prompt, file_path):
    with open(file_path, 'w') as f:
        f.write(prompt)

def upload_image(image_path):
    with open(image_path, 'rb') as f:
        return fal_client.upload(f, "image/png")

def main():
    parser = argparse.ArgumentParser(description='Download an upscaled image generated from a prompt.')
    parser.add_argument('desc', help='Text description of the image to generate')
    parser.add_argument('--save-path', default=os.path.expanduser("~/drawings/main"), help='Path where the upscaled image will be saved.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging.')
    parser.add_argument('--log-path', default="/tmp/draw_log", help='Path where debugging logs will be saved.')
    parser.add_argument('--autoprompt', choices=['none', 'sonnet'], default='none', help='Enable automatic prompt enhancements. `sonnet` requires Anthropic API key.')
    parser.add_argument('--image-to-image', help='Path to the input image for image-to-image generation.')
    args = parser.parse_args()

    # Your FAL_KEY should be retrieved from an environment variable
    FAL_KEY = os.getenv('FAL_KEY')
    if not FAL_KEY:
        raise ValueError("FAL_KEY environment variable is not set.")

    start_time = time.time()

    # Generate a single timestamp for all files
    timestamp = generate_timestamp()

    # Step 0: Optimize prompt
    original_prompt = args.desc
    prompt = original_prompt
    if args.autoprompt == 'sonnet':
        prompt = generate_sonnet(prompt)

    # Step 1: Generate an image using Stable Diffusion
    generate_image_url = 'https://fal.run/fal-ai/fast-sdxl'
    headers = {
        'Authorization': f'Key {FAL_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'prompt': prompt,
        'negative_prompt': NEG,
        'sync_mode': True,
        'image_size': 'landscape_16_9',
    }

    if args.image_to_image:
        generate_image_url = 'https://fal.run/fal-ai/fast-sdxl/image-to-image'
        image_url = upload_image(args.image_to_image)
        data['image_url'] = image_url

    generate_response = requests.post(generate_image_url, headers=headers, json=data)
    generate_response_json = generate_response.json()
    if args.verbose:
        print("Image generation response:", generate_response_json)

    # Extract the generated image URL
    generated_image_url = generate_response_json['images'][0]['url']
    if args.verbose:
        print("Generated Image URL:", generated_image_url)

    # Step 2: Upscale the generated image using ESRGAN
    upscale_image_url = 'https://fal.run/fal-ai/esrgan'
    upscale_data = {
        'image_url': generated_image_url,
    }

    upscale_response = requests.post(upscale_image_url, headers=headers, json=upscale_data)
    upscale_response_json = upscale_response.json()
    if args.verbose:
        print("Upscaling response:", upscale_response_json)

    # Extract the file name of the upscaled image
    upscaled_image_url = upscale_response_json['image']['url']
    if args.verbose:
        print("Upscaled Image URL:", upscaled_image_url)

    # Download and save the upscaled image
    image_file_path = generate_filename(args.save_path, timestamp, ".png")
    download_image(upscaled_image_url, image_file_path)

    # Save original prompt
    original_prompt_file = generate_filename(args.save_path, timestamp, ".txt")
    save_prompt(original_prompt, original_prompt_file)

    # Save reprompt if it was used
    if args.autoprompt == 'sonnet':
        reprompt_file = generate_filename(args.save_path, timestamp, "_reprompt.txt")
        save_prompt(prompt, reprompt_file)

    end_time = time.time()
    duration = end_time - start_time
    log_message = f"Total time taken: {duration} seconds\n"
    with open(args.log_path, 'a') as log_file:
        log_file.write(log_message)
        if args.verbose:
            print("Total time logged to: ", args.log_path)

if __name__ == '__main__':
    main()