from distutils.core import setup
import py2exe

setup(console=['player.py'],
      data_files=[
          ('_sounddevice_data', ["./_sounddevice_data/libportaudio32bit.dll", "./_sounddevice_data/libportaudio64bit.dll"])
          ],
      options={
        "py2exe": {
            "packages": ["numpy", "encodings"],
            "includes": ["sounddevice"]
            }
        })
