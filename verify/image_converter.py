import ffmpeg

from asyncio import run, get_running_loop
from io import BytesIO
from os import makedirs
from subprocess import Popen
from typing import Optional


makedirs("tmp", exist_ok=True)


class ImageConverter():
    @classmethod
    def _convert_to_jpeg(cls, data: bytes) -> bytes:
        input_buffer = BytesIO(data)
        output_buffer = BytesIO()

        process: Popen = ffmpeg.input(
            "pipe:"
        ).output(
            "pipe:",
            format="image2pipe",
            vcodec="mjpeg"
        ).run_async(
            pipe_stdin=True,
            pipe_stdout=True,
            pipe_stderr=True
        )

        stdout, stderr = process.communicate(
            input=input_buffer.read(),
            timeout=3
        )

        if process.returncode != 0:
            raise RuntimeError(f"ffmpeg error: {stderr.decode()}")

        output_buffer.write(stdout)
        return output_buffer.getvalue()

    @classmethod
    async def convert_to_jpeg(cls, data: bytes) -> Optional[bytes]:
        loop = get_running_loop()
        try:
            return await loop.run_in_executor(None, cls._convert_to_jpeg, data)
        except Exception as e:
            print(f"Error converting image: {e}")
            return None
