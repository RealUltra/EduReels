from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, concatenate_audioclips, AudioClip
from moviepy.config import change_settings

import whisperx
import warnings

import random
import os, uuid
import shutil

import pyttsx3

warnings.filterwarnings("ignore")

change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

device = "cuda"
model = whisperx.load_model("large-v2", device)

def get_random_subclip(video, duration_seconds):
    total_duration = int(video.duration)
    start_time = random.randint(0, total_duration)
    end_time = start_time + duration_seconds

    if end_time > total_duration:
        clip1 = video.subclip(start_time, total_duration)
        clip2 = video.subclip(0, (duration_seconds - total_duration + start_time))
        return concatenate_videoclips([clip1, clip2])

    else:
        return video.subclip(start_time, end_time)


def diarize_speech(audio_file):
    batch_size = 16

    result = model.transcribe(audio_file, batch_size=batch_size)

    alignment_model, metadata = whisperx.load_align_model(language_code="en", device=device)

    word_timestamps = whisperx.align(
        result["segments"], alignment_model, metadata, audio_file, device
    )

    diarized_speech = []

    segments = word_timestamps["segments"]

    for i, segment in enumerate(segments):
        text = segment["text"].strip()
        start = segment["start"]
        end = segment["end"] + 0.5

        if i < (len(segments) - 1):
            if end > segments[i + 1]["start"]:
                end = segments[i + 1]["start"]

        diarized_speech.append([text, start, end])

    return diarized_speech

def generate_audio(text, output_file, voice_index=0):
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[voice_index].id)

    engine.setProperty('volume', 1)

    engine.save_to_file(text, output_file)

    engine.runAndWait()


def generate_video(content, bg_video_file, output_file):
    '''
    :param content: [
        (1, "Hello! I'm Person 1"),
        (2, "And I'm Person 2!"),
        (1, "Person 1 again!!")
    ]
    :param bg_video_file: The file path to the background video.
    :param output_file: The file path where the output video will be saved.
    :return: None
    '''

    if not content:
        return

    voice_1 = random.randint(0, 1)
    voice_2 = int(not voice_1)
    voice_indicies = {1: voice_1, 2: voice_2}

    audio_clips = []

    shutil.rmtree('temp', ignore_errors=True)
    os.makedirs('temp', exist_ok=True)

    for person_num, text in content:
        temp_audio_file = f"temp/{uuid.uuid4()}.mp3"
        generate_audio(text, temp_audio_file, voice_indicies[person_num])
        audio_clips.append(AudioFileClip(temp_audio_file))
        audio_clips.append(AudioClip(lambda t: 0, duration=0.5, fps=44100))

    audio: AudioClip = concatenate_audioclips(audio_clips)

    video = VideoFileClip(bg_video_file)
    subclip = get_random_subclip(video, audio.duration)

    clips = [subclip]

    actual_start_time = 0
    for i in range(0, len(audio_clips), 2):
        audio_clip = audio_clips[i]
        person_num, _ = content[i//2]

        temp_audio_file = f"temp/{uuid.uuid4()}.mp3"
        audio_clip.write_audiofile(temp_audio_file)

        color = "yellow" if person_num == 1 else "white"

        diarized_speech = diarize_speech(temp_audio_file)

        for word, start, end in diarized_speech:
            text = TextClip(word,
                            fontsize=100,
                            font="Arial-Bold",
                            color=color,
                            stroke_color="black",
                            stroke_width=4)
            text = text.set_position(("center", "center")).set_start(actual_start_time + start).set_duration(end - start)
            clips.append(text)

        actual_start_time += audio_clip.duration + audio_clips[i+1].duration

    final_video = CompositeVideoClip(clips)
    final_video = final_video.set_audio(audio)

    final_video.write_videofile(output_file, codec="libx264", audio_codec="aac", verbose=True)

if __name__ == '__main__':
    generate_video([
        (1, "Hello! I'm Person 1"),
        (2, "And I'm Person 2!"),
        (1, "Person 1 again!!")
    ], "bg/minecraft.mp4", "output.mp4")