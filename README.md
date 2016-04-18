# radio-astronomy-fftw

**This is version 3 of my radio-astronomy data collection and dissemination project.**  
**It is based on [a modified version of rtl_power_fftw](https://github.com/mariocannistra/rtl-power-fftw) originally written by Klemen Blokar and Andrej Lajovic.**  

**All the programs have been modified to produce and manage binary data files instead of .csv ones for improved performance and reduced storage size.**  

A diagram showing the interactions between the various programs is available [here](https://raw.githubusercontent.com/mariocannistra/radio-astronomy-fftw/master/doc/observ-sw-diagram.png)  

Full documentation of the software setup and config for the various programs and tools is [here](doc/sw-setup.pdf)  

**All this sw has been changed/written, built and tested on a Raspberry PI 2 and then installed and re-tested on a Raspberry PI 3.**  

See project website at https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617  

A system targeted to amateur radio-astronomers for received radio data collection and dissemination. Radio emissions from sky sources like Sun and Jupiter can be received and converted to digital domain for processing. Data and/or processing results are pushed to AWS for storage and dissemination. Multiple low-cost receiver-processors are envisioned around the globe connecting centrally to distribute to any interested subscriber with an IoT like approach. An open science initiative with a strong collaborative approach to large scale measurement of natural events.  

Hardware used:  
Raspberry PI 3 (2 works fine obviously), RTL SDR radio receiver, dipole antenna and other radio accessories  

AWS authentication, messaging gateway plus other processing and storage services (IoT, S3, ..)  
