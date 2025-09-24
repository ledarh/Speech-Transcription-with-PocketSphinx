# ------------------------------------------------------------------------------
# Author: Kelly Higgins - @ledarh
# GitHub: https://github.com/ledarh
#
# Script Overview:
# This script transcribes audio files using the PocketSphinx model from CMU Sphinx.
# It processes the audio in chunks and outputs a transcription in a .txt file.
# The script includes progress reporting and estimated remaining time.
#
# IMPORTANT: Before running the script, make sure to replace the `pocketsphinx_repo_path`
# variable with the correct path to the PocketSphinx repo on your local machine.
# ------------------------------------------------------------------------------

import os
import speech_recognition as sr
import time
import concurrent.futures

# Path to the PocketSphinx repo
pocketsphinx_repo_path = '[path to pocketsphinx repo]'

# Path to the WAV file you want to transcribe
audio_file_path = '[.wav file path]'

# Path where the transcription will be saved
output_file_path = 'my_transcription.txt'



recognizer = sr.Recognizer()

# Determine number of chunks
def calculate_chunk_size(duration):
    if duration <= 300:  # 5 minutes or less
        return 30  # ~30s/chunk
    elif duration <= 900:  # up to 15 minutes
        return 60  # ~1m/chunk
    elif duration <= 1800:  # up to 30 minutes
        return 120  # ~2m/chunk
    else:  # >30 minutes
        return 300  # ~5m/chunk

# Helper to split the audio into smaller chunks based on the duration
def split_audio(file_path):
    with sr.AudioFile(file_path) as source:
        # Get the total duration of the audio file
        audio_duration = source.DURATION  # Duration in seconds
        chunk_size = calculate_chunk_size(audio_duration)  # Calculate chunk size based on duration
        num_chunks = int(audio_duration // chunk_size) + 1  # Total number of chunks
        
        # Yield chunks of audio data
        for i in range(num_chunks):
            duration = min(chunk_size, audio_duration - (i * chunk_size))
            audio_chunk = recognizer.record(source, duration=duration)
            yield audio_chunk, i, num_chunks

# Transcribe a chunk of audio
def transcribe_chunk(audio_chunk, chunk_index):
    try:
        chunk_transcription = recognizer.recognize_sphinx(audio_chunk)
        return chunk_transcription, chunk_index
    except sr.UnknownValueError:
        return f"Chunk {chunk_index + 1}: PocketSphinx could not understand the audio", chunk_index
    except sr.RequestError as e:
        return f"Chunk {chunk_index + 1}: Could not request results from PocketSphinx; {e}", chunk_index
    except Exception as e:
        return f"Error in chunk {chunk_index + 1}: {e}", chunk_index

# Core function to parallelize transcription
def transcribe_audio(file_path, output_file_path):
    transcription = [None] * 100  # Reserve space for chunk transcription (max 100 chunks)
    chunks_processed = 0  # Counter for processed chunks
    
    # Initialization information
    with sr.AudioFile(file_path) as source:
        audio_duration = source.DURATION  # Duration in seconds
    
    chunk_size = calculate_chunk_size(audio_duration)
    num_chunks = int(audio_duration // chunk_size) + 1
    
    print(f"\nBeginning transcription of file: {os.path.basename(file_path)}")
    print(f"Transcription will be saved to: {os.path.basename(output_file_path)}")
    print(f"Total Chunks: {num_chunks}")
    print("\nBeginning...\n")
    
    # Split audio into chunks and process in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_chunk = {executor.submit(transcribe_chunk, audio_chunk, chunk_index): (audio_chunk, chunk_index) 
                           for audio_chunk, chunk_index, _ in split_audio(file_path)}
        
        for future in concurrent.futures.as_completed(future_to_chunk):
            chunk_transcription, chunk_index = future.result()
            transcription[chunk_index] = chunk_transcription  # Store result in the correct order

            # Increment the processed chunk counter
            chunks_processed += 1

            # Calculate overall progress based on chunks processed
            overall_progress = (chunks_processed / num_chunks) * 100

            # Display progress for each chunk completed
            print(f"Chunk {chunk_index + 1} Complete - {overall_progress:.2f}%")

    # Save transcription to output file
    complete_transcription = " ".join([t for t in transcription if t is not None])
    if complete_transcription:
        with open(output_file_path, 'w') as f:
            f.write(complete_transcription)
        print(f"Transcription successfully saved to: {os.path.basename(output_file_path)}")
    else:
        print("No transcription available.")

transcribe_audio(audio_file_path, output_file_path)
