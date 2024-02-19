# FrameIt

FrameIt is a Python command-line tool that automates the generation and upscaling of images based on textual descriptions. Leveraging Stable Diffusion XL over `fal.ai`, it provides a seamless way to create images with minimal effort. I run this tool on a Pi Zero W connected to a Frame TV - in combination with an iOS shortcut, I can frame new AI-generated art anytime for < $0.01 (as of writing).

## Prerequisites

- Python 3.6+
- An active `fal.ai` API key set as the `FAL_KEY` environment variable.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/dshumphr/frameit.git
   cd frameit
   ```

2. **Setup Environment Variable**

   Ensure the `FAL_KEY` environment variable is set with your `fal.ai` API key.

   ```bash
   export FAL_KEY='your_fal_api_key_here'
   ```

3. **Install FrameIt**

   ```bash
   pip install .
   ```

## Usage

After installation, you can use the `frameit` command to generate and upscale images:

```bash
frameit "Your image description here"
```

- See `--help` for more options.

- **iOS Shortcut Integration**: FrameIt can be integrated with an iOS shortcut for remote execution. [View Shortcut](https://www.icloud.com/shortcuts/4d191b52f6664dbda2a5f9c2533c2575) This will require installing `fbi` on your device and enabling ssh.


## Notes
Image upscaling is the bottleneck and may take over 60s to run. I'm looking into options for speeding this up, and would be open to suggestions.
Prompting well is outside of the scope here, but more details about style, medium, etc are generally helpful. Perhaps a future extension will leverage LLM to enhance prompts.
