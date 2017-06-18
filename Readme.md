# Audio Transmitter

Transmit audio through windows driver to other device
The driver ist created through the Windows Driver Kit (7600.16385.1). Therefore the *msvad* driver has been manipulated to fit the requirements.
The data is transmitted as in WAVE-format through bare sockets


# Dependencies
- python (>=3.4)
- numpy (http://www.numpy.org/)
- sounddevice (https://python-sounddevice.readthedocs.io/en/0.3.7/)


# Installation
1. Allow test signed drivers

    bcdedit.exe -set TESTSIGNING ON

2. Reboot PC to aktivate testsigning
3. Create Dir *C:\STREAM\* (destination directory for stream files)
3. Install driver in Windows (currently only availabe for Windows 7 x64):

  1. Open Admnistrative Command line
  2. Change to driver directory
  3. Install the driver through devcon

    > devcon install msvad.inf *MSVADAudioTransmitter
 
4. Now you can select "AudioTransmitter" as Playback Device in Windows and all audio will be saved under *C:\STREAM\#*
5. To start the audio server simply start */server/server.py* with the desired arguments
6. You can then connect through player.py or player.exe (/player/dist/player.exe) and connect to the host and start streaming your audio data
