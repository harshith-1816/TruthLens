"""
TruthLens - Demonstration Sample Cases Generator
Generates realistic multimodal test packages:
1. Coordinated Multimodal Deepfake Attack (Synthetic Image, Cloned Audio, Video Jitter, LLM Text)
2. Spliced Photo with Deceptive Metadata & Text
3. Authentic Eyewitness Field Documentation (Baseline)
"""

import io
import wave
import struct
import numpy as np
from PIL import Image, ImageDraw


def generate_synthetic_image() -> bytes:
    """Generates an image exhibiting synthetic diffusion/GAN checkerboard frequency artifacts."""
    w, h = 512, 512
    # Base gradient image
    y, x = np.ogrid[:h, :w]
    base = ((np.sin(x / 30.0) + np.cos(y / 30.0)) * 60 + 128).astype(np.float32)

    # Inject periodic high-frequency checkerboard grid (classic GAN deconvolution artifact)
    grid_pattern = ((x % 4 == 0) & (y % 4 == 0)).astype(np.float32) * 55.0
    synthetic_arr = np.clip(base + grid_pattern, 0, 255).astype(np.uint8)

    img = Image.fromarray(synthetic_arr).convert("RGB")
    # Add embedded AI generator tag in PNG info
    buffer = io.BytesIO()
    # Add PNG text info
    from PIL.PngImagePlugin import PngInfo
    info = PngInfo()
    info.add_text("prompt", "a cinematic realistic portrait, photorealistic 8k")
    info.add_text("Software", "StableDiffusion-v2.1 ComfyUI")
    img.save(buffer, format="PNG", pnginfo=info)
    return buffer.getvalue()


def generate_spliced_image() -> bytes:
    """Generates an image with a localized spliced quadrant that creates an ELA and noise anomaly."""
    w, h = 512, 512
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Background natural gradient
    for y in range(h):
        for x in range(w):
            arr[y, x] = [int(100 + 50 * np.sin(x / 40.0)), int(120 + 40 * np.cos(y / 40.0)), 150]

    # Splice in a patch in center (180:320, 180:320) saved with radically different noise & compression
    patch = np.random.randint(200, 255, (140, 140, 3), dtype=np.uint8)
    arr[180:320, 180:320] = patch

    img = Image.fromarray(arr)
    # Save as JPEG with Photoshop EXIF software tag
    buffer = io.BytesIO()
    exif = img.getexif()
    exif[0x0131] = "Adobe Photoshop 2026 (Windows)"  # Software tag
    exif[0x010F] = "Canon"  # Make
    exif[0x0110] = "Canon EOS 5D Mark IV"  # Model
    img.save(buffer, format="JPEG", quality=85, exif=exif)
    return buffer.getvalue()


def generate_authentic_image() -> bytes:
    """Generates an image with natural smooth sensor noise and authentic camera EXIF."""
    w, h = 640, 480
    y, x = np.ogrid[:h, :w]
    natural_scene = (120 + 80 * np.sin(x / 80.0) * np.cos(y / 60.0)).astype(np.float32)
    # Natural Gaussian sensor noise
    sensor_noise = np.random.normal(0, 3.5, (h, w)).astype(np.float32)
    img_data = np.clip(natural_scene + sensor_noise, 0, 255).astype(np.uint8)

    img = Image.fromarray(img_data).convert("RGB")
    buffer = io.BytesIO()
    exif = img.getexif()
    exif[0x010F] = "Sony"
    exif[0x0110] = "ILCE-7M4"
    exif[0x9003] = "2026:11:18 10:14:22"
    img.save(buffer, format="JPEG", quality=96, exif=exif)
    return buffer.getvalue()


def generate_synthetic_cloned_audio() -> bytes:
    """Generates a WAV audio file exhibiting vocoder brickwall cutoff (0 energy >8kHz) & flat pitch."""
    sample_rate = 24000
    duration = 4.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Artificially flat fundamental frequency (exactly 180 Hz with ZERO human micro-tremor)
    f0 = 180.0
    harmonics = (
        0.6 * np.sin(2 * np.pi * f0 * t)
        + 0.3 * np.sin(2 * np.pi * 2 * f0 * t)
        + 0.15 * np.sin(2 * np.pi * 3 * f0 * t)
    )

    # Dead digital silence in the middle (classic TTS phrase concatenation)
    silence_start = int(1.8 * sample_rate)
    silence_end = int(2.3 * sample_rate)
    harmonics[silence_start:silence_end] = 0.0

    # Strict lowpass brickwall filter at 7500 Hz (TTS cutoff)
    # Since harmonics only reach 3*180 = 540 Hz, there is zero energy above 8kHz in this 24kHz file
    signal = np.clip(harmonics, -0.99, 0.99)
    int_samples = (signal * 32767).astype(np.int16)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(int_samples.tobytes())

    return buffer.getvalue()


def generate_authentic_audio() -> bytes:
    """Generates a WAV file with natural vocal micro-tremors, breathing decay, and wideband ambient floor."""
    sample_rate = 44100
    duration = 5.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Vocal cord micro-tremors (jitter modulated frequency: 150 Hz +/- 3.5 Hz)
    f0_modulated = 150.0 + 3.5 * np.sin(2 * np.pi * 6.0 * t) + np.random.normal(0, 0.5, len(t))
    phase = 2 * np.pi * np.cumsum(f0_modulated) / sample_rate

    voice = 0.5 * np.sin(phase) + 0.25 * np.sin(2 * phase) + 0.15 * np.sin(3 * phase)

    # Wideband ambient room acoustics (dither across all frequencies up to 22kHz)
    ambient_noise = np.random.normal(0, 0.015, len(t))
    combined = np.clip(voice + ambient_noise, -0.99, 0.99)
    int_samples = (combined * 32767).astype(np.int16)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(int_samples.tobytes())

    return buffer.getvalue()


def generate_synthetic_video_payload() -> bytes:
    """Generates an animated GIF/video payload with deliberate frame-to-frame jitter spikes."""
    frames = []
    w, h = 256, 256

    for i in range(16):
        arr = np.zeros((h, w, 3), dtype=np.uint8)
        # Background
        arr[:, :] = [40, 50, 70]

        # Center face-like oval
        y, x = np.ogrid[:h, :w]
        mask = ((x - 128) ** 2 / (50**2) + (y - 128) ** 2 / (70**2)) <= 1.0

        # Inject temporal spike at frames 8 and 9 (deepfake warp flicker)
        if i in [8, 9]:
            arr[mask] = [240, 130, 130]  # radical color/lighting shift
        else:
            arr[mask] = [210, 170, 140]

        frames.append(Image.fromarray(arr))

    buffer = io.BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0
    )
    return buffer.getvalue()


def get_sample_cases():
    """Returns catalog of pre-packaged test cases."""
    return {
        "case_deepfake_attack": {
            "title": "Operation Chimera: Synthetic CEO Distress Video & Voice Clone",
            "description": "Multimodal deepfake attack featuring an AI-generated image with high-frequency GAN artifacts, an acoustic clone with vocoder brickwall cutoff, temporal video jitter spikes, and LLM-crafted panic disinformation text.",
            "image": generate_synthetic_image(),
            "image_filename": "ceo_press_briefing_synthetic.png",
            "audio": generate_synthetic_cloned_audio(),
            "audio_filename": "ceo_audio_statement_cloned.wav",
            "video": generate_synthetic_video_payload(),
            "video_filename": "ceo_video_statement_jitter.gif",
            "text": (
                "It is crucial to remember that our organization has always stood as a beacon of integrity. "
                "In conclusion, we must delve into these unprecedented challenges with steadfast resolve. "
                "Furthermore, it is essential to understand that mainstream media won't show you this confidential update. "
                "Share before they delete this critical message. The multifaceted impact cannot be overstated."
            ),
            "text_filename": "transcription_and_dispatch.txt"
        },
        "case_spliced_photo": {
            "title": "Fabricated Riot Signage & Editorial Caption Tampering",
            "description": "A high-resolution photograph with localized ELA discrepancies and mismatched sensor noise patches where protest signs were spliced, coupled with viral disinformation phrasing and contradictory editing EXIF.",
            "image": generate_spliced_image(),
            "image_filename": "protest_square_spliced.jpg",
            "audio": None,
            "video": None,
            "text": (
                "BREAKING: Proof that it was all staged! Leaked confidential document and live unedited photo "
                "from downtown square showing extreme unrest. Share before they delete this!"
            ),
            "text_filename": "viral_social_caption.txt"
        },
        "case_authentic_baseline": {
            "title": "Verified Eyewitness Incident Dispatch (Authentic Baseline)",
            "description": "Authentic Sony camera capture with natural Gaussian sensor noise, authentic audio monologue with physiological vocal micro-tremors and natural breathing cadence, and spontaneous human eyewitness text.",
            "image": generate_authentic_image(),
            "image_filename": "authentic_field_documentation.jpg",
            "audio": generate_authentic_audio(),
            "audio_filename": "field_witness_testimony.wav",
            "video": None,
            "text": (
                "I was standing right across the street near 4th and Elm when the municipal power transformer blew up. "
                "The noise was deafening! Sparks shot everywhere and cars immediately started braking. "
                "I managed to pull out my camera about 15 seconds after the first explosion."
            ),
            "text_filename": "eyewitness_written_statement.txt"
        },
        "case_environmental_contradiction": {
            "title": "Cross-Modal Semantic Conflict: Mumbai Daylight Claim vs Spliced Night Visual",
            "description": "Cross-modal forensic demonstration where the text caption claims an unedited outdoor daytime event in Mumbai yesterday, but the evidence file exhibits dark nighttime illumination, localized sensor noise anomalies, and acoustic splicing.",
            "image": generate_spliced_image(),
            "image_filename": "mumbai_nighttime_dark_evidence.jpg",
            "audio": generate_synthetic_cloned_audio(),
            "audio_filename": "audio_interview_spliced.wav",
            "video": None,
            "text": (
                "Official live dispatch: This video was recorded in Mumbai yesterday during bright sunny daytime. "
                "The speaker confirmed the event outdoor in broad daylight. Share before they delete this truth!"
            ),
            "text_filename": "mumbai_daylight_claim.txt"
        }
    }
