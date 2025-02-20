import os
from pathlib import Path

import httpx
from elevenlabs import ElevenLabs
from pydub import AudioSegment


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
        voice_id=os.environ["ELEVENLABS_VOICE_ID"],  # JeiJo voice
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_192"
    )

    with open(f"{out_dir}/podcast_audio.mp3", "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)

def add_audio_effects(
        audio_file: Path,
        project_root_dir: Path,
        output_dir: Path
):
    podcast = AudioSegment.from_mp3(audio_file)
    intro = AudioSegment.from_mp3(f"{project_root_dir}/resources/podcast_intro_sound.mp3")

    seconds_to_slice = 4.1 * 1000

    result = intro[:seconds_to_slice] + podcast

    result.export(f"{output_dir}/podcast_audio_final_final_v2.mp3", format="mp3", bitrate="192k")