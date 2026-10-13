import subprocess, threading


# Run the streaming commands for specific amount of time
def run_simulation(command, runtime):
    try:
        subprocess.run(command, shell=False, timeout=runtime)
    except subprocess.TimeoutExpired:
        print(f"Terminated since it run for {runtime} seconds.")


# Concurrent video and audio streaming using threads
if __name__ == "__main__":
    run_time = 14400 # Seconds

    # Streaming cli commands
    video_command = ["ffmpeg","-re","-stream_loop","-1","-i","./video_video_streaming.mp4","-vf","scale=1280:720","-c:v", "libx264","-preset", "ultrafast", "-tune", "zerolatency", "-b:v", "3M", "-maxrate", "4M", "-bufsize", "6M", "-an", "-f", "rtp", "rtp://10.60.0.1:5000"]
    audio_command = ["ffmpeg","-re","-stream_loop","-1","-i","./video_video_streaming.mp4","-vn","-c:a","libopus","-b:a", "128k", "-f", "rtp", "rtp://10.60.0.1:5001"]

    t1 = threading.Thread(target=run_simulation, args=(video_command, run_time))
    t2 = threading.Thread(target=run_simulation, args=(audio_command, run_time))
    
    t1.start()
    t2.start()
    print(f"{run_time} seconds simulation started!")

    t1.join()
    t2.join()
    print(f"{run_time} seconds simulation finished!")


# Video streamed by Maciej from Pixabay