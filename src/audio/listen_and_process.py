from .save_audio import _AudioSaver

def listen_and_process(listen_instance, process_audio_instance):
    """Main loop to record, save, and process audio chunks."""
    audio_saver = _AudioSaver()
    while True:
        try:
            # Record audio until silence is detected
            audio_data = listen_instance.record_until_silence()
            if audio_data:
                # Save audio as OGG file
                ogg_file = audio_saver.save_audio_as_ogg(audio_data, filename='recorded_audio')

                # Call the processing function with the OGG file
                process_audio_instance.process_audio_chunk(ogg_file)

                print("\nReady to listen again...\n")
            else:
                print("No audio data captured.")

        except KeyboardInterrupt:
            print("Program terminated by user.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Continuing to listen...\n")