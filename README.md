<p align="center">
  <img src="diVineredirecticon.jpg" alt="diVine Redirect Icon" width="512" height="512">
</p>

<h1 align="center">diVineRedirect</h1>



---
Requirements: A Windows computer running Windows 8.1 or later, Python from https://www.python.org/ , FFmpeg n5.1.5 win64 gpl 5.1 from https://github.com/BtbN/FFmpeg-Builds/releases?page=4 .
Ok so to install the necessary Python dependencies, run:

```bash
pip install flask requests websocket-client
```
ok so now after that you want to make a new folder now put the main.py in that folder than put your ffmpeg in that folder
```IMPORTANT
make sure your directory looks like ffmpeg\bin\ffmpeg.exe not ffmpeg\ffmpeg\bin\ffmpeg.exe or ffmpeg-n5.1.5-win64-gpl-5.1\bin\ffmpeg.exe
```
now after that right click main.py then click open with and then more options then notepad then look for
```pythin
MY_IP = "insertyouriphere"
```
and insert your ip address where insertyouriphere is now save the file and open it now prepare your vine app patcher.
working/tested vine app versions are 1.1.2 1.4.5 1.4.8 5.7.0 .
working stuff is non-placeholder home/new videos feed and non-placeholder video playback rest is to be implemented maybe in the future.
