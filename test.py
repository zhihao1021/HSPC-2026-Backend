from asyncio import run as async_run, get_running_loop
from subprocess import Popen

def test():
    process = Popen(["sleep", "5"], stdin=True, stdout=True, stderr=True)
    print("Process started")
    process.communicate(b"Test", timeout=1)
    print("Process completed")
    process.wait(1)
    print("Process exited with code", process.returncode)

async def main():
    loop = get_running_loop()
    await loop.run_in_executor(None, test)
    print("Test completed")

async_run(main())
