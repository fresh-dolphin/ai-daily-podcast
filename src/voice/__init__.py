import os
from datetime import datetime
from pathlib import Path

import httpx
from elevenlabs import play, ElevenLabs, VoiceSettings


def generate_audio_from(text_to_speech: str, out_dir: Path):
    timeout = httpx.Timeout(15.0, read=30.0)
    client = httpx.Client(timeout=timeout)

    eleven_labs_client = ElevenLabs(
        api_key=os.environ["ELEVENLABS_API_KEY"],
        httpx_client=client
    )

    print(f'Saving audio result...')

    audio = eleven_labs_client.text_to_speech.convert(
        text=text_to_speech,
        voice_id="PBaBRSRTvwmnK1PAq9e0", # JeiJo voice
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_192"
    )

    with open(f"{out_dir}/podcast-audio.mp3", "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)