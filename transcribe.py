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

# Path to the PocketSphinx repo
pocketsphinx_repo_path = 'C:/pocketsphinx'

# Path to the WAV file you want to transcribe
audio_file_path = 'C:/Users/ledar/positions/Transcribe/testf.wav'

# Path where the transcription will be saved
output_file_path = 'C:/Users/ledar/positions/Transcribe/my_transcription.txt'


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

# Helper: seconds -> x days hh:mm:ss
def format_time(seconds):
    days = int(seconds // (24 * 3600))  # Convert to integer to avoid float errors
    seconds %= (24 * 3600)
    hours = int(seconds // 3600)  # Convert to integer to avoid float errors
    seconds %= 3600
    minutes = int(seconds // 60)  # Convert to integer to avoid float errors
    seconds = round(seconds % 60)  # Round seconds to the nearest integer

    if days > 0:
        return f"Estimated remaining: {days} days {hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"Estimated remaining: {hours:02d}:{minutes:02d}:{seconds:02d}"

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

# Core function
def transcribe_audio(file_path, output_file_path):
    transcription = ""

    # Initialization information
    with sr.AudioFile(file_path) as source:
        audio_duration = source.DURATION  # Duration in seconds
    
    chunk_size = calculate_chunk_size(audio_duration)
    num_chunks = int(audio_duration // chunk_size) + 1
    
    print(f"\nBeginning transcription of file: {os.path.basename(file_path)}")
    print(f"Transcription will be saved to: {os.path.basename(output_file_path)}")
    print(f"Total Chunks: {num_chunks}")
    print("\nBeginning...\n")
    print(f"Progress: 0.00%")

    # Track start time for estimated completion
    start_time = time.time()

    # Split audio into chunks and process
    for audio_chunk, chunk_index, total_chunks in split_audio(file_path):
        # Transcribe chunk
        try:
            chunk_transcription = recognizer.recognize_sphinx(audio_chunk)
            transcription += chunk_transcription + " "
            
            # Calculate progress
            progress = (chunk_index + 1) / total_chunks * 100

            # Calculate elapsed time and estimated time remaining
            elapsed_time = time.time() - start_time
            avg_time_per_chunk = elapsed_time / (chunk_index + 1)
            remaining_time = avg_time_per_chunk * (total_chunks - (chunk_index + 1))
            
            # Display progress with estimated time remaining in a readable format
            if chunk_index > 0:  # Skip estimated time for the first progress update
                print(f"Progress: {progress:.2f}% - {format_time(remaining_time)}")
            else:
                print(f"Progress: {progress:.2f}%")
        
        except sr.UnknownValueError:
            print(f"Chunk {chunk_index + 1}: PocketSphinx could not understand the audio")
        except sr.RequestError as e:
            print(f"Chunk {chunk_index + 1}: Could not request results from PocketSphinx; {e}")
        except Exception as e:
            print(f"Error in chunk {chunk_index + 1}: {e}")

    # Save transcription to output file
    if transcription:
        with open(output_file_path, 'w') as f:
            f.write(transcription)
        print(f"Transcription successfully saved to: {os.path.basename(output_file_path)}")
    else:
        print("No transcription available.")


transcribe_audio(audio_file_path, output_file_path)
