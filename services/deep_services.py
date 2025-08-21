# services/audio_service.py

import os
import statistics
import aiohttp
from deepgram import DeepgramClient, PrerecordedOptions, FileSource, DeepgramClientOptions

DEEPGRAM_API_KEY = "96c9c90aa26cdb74b5d8fc5cf69a0fd82975000f"

async def transcribe_audio(file_path: str):
    """
    Transcribes an audio file into text using Deepgram API.

    Args:
        file_path (str): Path to the audio file (mp3, wav, aac, etc.)
    
    Returns:
        dict: Transcription result with speaker labels and confidence scores
    """
    try:
        # Set a longer timeout (e.g., 900 seconds = 15 minutes)
        timeout = aiohttp.ClientTimeout(total=900)

        # Pass custom aiohttp session into Deepgram client
        async with aiohttp.ClientSession(timeout=timeout) as session:
            deepgram = DeepgramClient(
                api_key=DEEPGRAM_API_KEY,
                config=DeepgramClientOptions(options={"aiohttp_session": session})
            )

            with open(file_path, "rb") as file:
                buffer_data = file.read()

            payload: FileSource = {"buffer": buffer_data}

            options = PrerecordedOptions(
                model="nova-3",   # Deepgram’s latest model
                smart_format=True,
                diarize=True,     # Separate speakers
                utterances=True,
            )

            # Await transcription (important!)
            response =  deepgram.listen.rest.v("1").transcribe_file(payload, options)

            words = response["results"]["channels"][0]["alternatives"][0]["words"]
            speaker_transcripts = []

            current_speaker = words[0]["speaker"]
            current_words = []
            current_confidences = []

            for word_info in words:
                speaker = word_info["speaker"]
                word = word_info["word"]
                confidence = word_info["confidence"]

                if speaker != current_speaker:
                    sentence = " ".join(current_words)
                    avg_conf = statistics.mean(current_confidences)
                    speaker_transcripts.append({
                        "speaker": current_speaker,
                        "confidence": round(avg_conf, 2),
                        "text": sentence
                    })
                    current_words = [word]
                    current_confidences = [confidence]
                    current_speaker = speaker
                else:
                    current_words.append(word)
                    current_confidences.append(confidence)

            if current_words:
                sentence = " ".join(current_words)
                avg_conf = statistics.mean(current_confidences)
                speaker_transcripts.append({
                    "speaker": current_speaker,
                    "confidence": round(avg_conf, 2),
                    "text": sentence
                })

            return {"transcription": speaker_transcripts}

    except Exception as e:
        return {"error": str(e)}
