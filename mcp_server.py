# ============================================================================
# MCP SERVER : stdio server implementing audio and video editing tools
# ============================================================================
from fastmcp import FastMCP
import ffmpeg
import yt_dlp
import os
from pathlib import Path

# Initialize FastMCPServer
mcp = FastMCP("AudioVideoEditorMCP", version="1.0.0")

# Output directory for processed files
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@mcp.tool()
def download_youtube_video(url: str, output_name: str = "downloaded_video.mp4") -> str:
    """
    Download a YouTube video 
    Args:
        url (str): YouTube video URL.
        output_name (str): The name of the output file to save to.
    Returns:
        str: The path to the downloaded video file.
    """
    ydl_opts = {
        'outtmpl': str(OUTPUT_DIR / output_name),
        'format': 'best[ext=mp4]',
        'merge_output_format': 'mp4',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return str(OUTPUT_DIR / output_name)
    except Exception as e:
        return f"Error downloading video: {str(e)}"

@mcp.tool()
def trim_video(input_path: str, start_time: str, end_time: str, output_name: str = "trimmed_video.mp4") -> str:
    """
    Trim a video file based on start and end time timestamps.
    Args:
        input_path (str): Path to the input video file.
        start_time (str): Start time in format 'HH:MM:SS' or seconds.
        end_time (str): End time in format 'HH:MM:SS' or seconds.
        output_name (str): The name of the output trimmed video file.
    Returns:
        str: The path to the trimmed video file.
    """
    output_path = OUTPUT_DIR / output_name
    try:
        (
            ffmpeg
            .input(input_path, ss=start_time, to=end_time)
            .output(str(output_path), codec='copy')
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return str(output_path)
    except Exception as e:
        return f"Error trimming video: {str(e)}"

@mcp.tool()
def merge_videos(input_path1: str, input_path2: str, output_name: str = "merged_video.mp4") -> str:
    """
    Merge multiple video files into one single video file.
    Args:
        input_path1 (str): Path to the first input video file.
        input_path2 (str): Path to the second input video file.
        output_name (str): Name of the output merged video file.
    Returns:
        str: The path to the merged video file.
    """
    output_path = OUTPUT_DIR / output_name
    try:
        with open(OUTPUT_DIR / "file_list.txt", "w") as f:
            for path in (input_path1, input_path2):
                f.write(f"file '{path}'\n")
        
        (
            ffmpeg
            .input(str(OUTPUT_DIR / "file_list.txt"), format='concat', safe=0)
            .output(str(output_path), c='copy')
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        os.remove(OUTPUT_DIR / "file_list.txt")
        return str(output_path)
    except Exception as e:
        return f"Error merging videos: {str(e)}"

@mcp.tool()
def extract_audio(input_path: str, output_name: str = "extracted_audio.mp3") -> str:
    """
    Extract audio from a video file.
    Args:
        input_path (str): Path to the input video file.
        output_name (str): The name of the output audio file.
    Returns:
        str: The path to the extracted audio file.
    """
    output_path = OUTPUT_DIR / output_name
    try:
        (
            ffmpeg
            .input(input_path)
            .output(str(output_path), acodec='mp3', vn=True)
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return str(output_path)
    except Exception as e:
        return f"Error extracting audio: {str(e)}"

@mcp.tool()
def trim_audio(input_path: str, start_time: str, end_time: str, output_name: str = "trimmed_audio.mp3") -> str:
    """
    Trim an audio file based on start and end time timestamps.
    Args:
        input_path (str): Path to the input audio file.
        start_time (str): Start time in format 'HH:MM:SS' or seconds.
        end_time (str): End time in format 'HH:MM:SS' or seconds.
        output_name (str): The name of the output trimmed audio file.
    Returns:
        str: The path to the trimmed audio file.
    """
    output_path = OUTPUT_DIR / output_name
    try:
        (
            ffmpeg
            .input(input_path, ss=start_time, to=end_time)
            .output(str(output_path), acodec='mp3')
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return str(output_path)
    except Exception as e:
        return f"Error trimming audio: {str(e)}"

@mcp.tool()
def convert_video_format(input_path: str, output_format: str = "avi", output_name: str = "converted_video") -> str:
    """
    Convert a video file to a different format.
    Args:
        input_path (str): Path to the input video file.
        output_format (str): Desired output video format (e.g., 'avi', 'mkv').
        output_name (str): The name of the output converted video file without extension.
    Returns:
        str: The path to the converted video file.
    """
    output_path = OUTPUT_DIR / f"{output_name}.{output_format}"
    try:
        (
            ffmpeg
            .input(input_path)
            .output(str(output_path))
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return str(output_path)
    except Exception as e:
        return f"Error converting video format: {str(e)}"

@mcp.tool()
def add_watermark(input_path: str, watermark_path: str, position: str = "10:10", output_name: str = "watermarked_video.mp4") -> str:
    """
    Add a watermark to a video file.
    Args:
        input_path (str): Path to the input video file.
        watermark_path (str): Path to the watermark image file.
        position (str): Position of the watermark in 'x:y' format.
        output_name (str): The name of the output watermarked video file.
    Returns:
        str: The path to the watermarked video file.
    """
    output_path = OUTPUT_DIR / output_name
    try:
        (
            ffmpeg
            .input(input_path)
            .input(watermark_path)
            .filter('overlay', position.split(':')[0], position.split(':')[1])
            .output(str(output_path))
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return str(output_path)
    except Exception as e:
        return f"Error adding watermark: {str(e)}"  

@mcp.tool()
def extract_frames(input_path: str, interval: int = 1, output_dir_name: str = "extracted_frames") -> str:
    """
    Extract frames from a video file at specified intervals.
    Args:
        input_path (str): Path to the input video file.
        interval (int): Interval in seconds between extracted frames.
        output_dir_name (str): The name of the output directory to save frames.
    Returns:
        str: The path to the directory containing extracted frames.
    """
    output_dir = OUTPUT_DIR / output_dir_name
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        (
            ffmpeg
            .input(input_path)
            .filter('fps', fps=1/interval)
            .output(str(output_dir / 'frame_%04d.png'))
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return str(output_dir)
    except Exception as e:
        return f"Error extracting frames: {str(e)}"

@mcp.tool()
def change_audio_speed(input_path: str, speed_factor: float, output_name: str = "speed_changed_audio.mp3") -> str:
    """
    Change the speed of an audio file.
    Args:
        input_path (str): Path to the input audio file.
        speed_factor (float): Factor by which to change the speed (e.g., 1.5 for 1.5x speed).
        output_name (str): The name of the output audio file with changed speed.
    Returns:
        str: The path to the audio file with changed speed.
    """
    output_path = OUTPUT_DIR / output_name
    try:
        (
            ffmpeg
            .input(input_path)
            .filter('atempo', speed_factor)
            .output(str(output_path))
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return str(output_path)
    except Exception as e:
        return f"Error changing audio speed: {str(e)}"

@mcp.tool()
def change_video_speed(input_path: str, speed_factor: float, output_name: str = "speed_changed_video.mp4") -> str:
    """
    Change the speed of a video file.
    Args:
        input_path (str): Path to the input video file.
        speed_factor (float): Factor by which to change the speed (e.g., 1.5 for 1.5x speed).
        output_name (str): The name of the output video file with changed speed.
    Returns:
        str: The path to the video file with changed speed.
    """
    output_path = OUTPUT_DIR / output_name
    try:
        (
            ffmpeg
            .input(input_path)
            .filter('setpts', f'{1/speed_factor}*PTS')
            .output(str(output_path))
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return str(output_path)
    except Exception as e:
        return f"Error changing video speed: {str(e)}"

@mcp.tool()
def mute_video_audio(input_path: str, output_name: str = "muted_video.mp4") -> str:
    """
    Mute the audio of a video file.
    Args:
        input_path (str): Path to the input video file.
        output_name (str): The name of the output muted video file.
    Returns:
        str: The path to the muted video file.
    """
    output_path = OUTPUT_DIR / output_name
    try:
        (
            ffmpeg
            .input(input_path)
            .output(str(output_path), an=None, vcodec='copy')
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return str(output_path)
    except Exception as e:
        return f"Error muting video audio: {str(e)}"

@mcp.tool()
def create_gif(input_path: str, start_time: str, duration: str, fps: int = 10, width: int = 480, output_name: str = "output.gif") -> str:
    """
    Create a GIF from a segment of a video file.
    Args:
        input_path (str): Path to the input video file.
        start_time (str): Start time in format 'HH:MM:SS' or seconds.
        duration (str): Duration of the GIF in seconds.
        fps (int): Frames per second for the GIF.
        width (int): Width of the output GIF; height is scaled proportionally i.e. auto calculated.
        output_name (str): The name of the output GIF file.
    Returns:
        str: The path to the created GIF file.
    """
    output_path = OUTPUT_DIR / output_name
    try:
        (
            ffmpeg
            .input(input_path, ss=start_time, t=duration)
            .filter
            .filter('scale', width, -1)
            .output(str(output_path), loop=0)
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return str(output_path)
    except Exception as e:
        return f"Error creating GIF: {str(e)}"

# Run the server
if __name__ == "__main__":
    mcp.run()
