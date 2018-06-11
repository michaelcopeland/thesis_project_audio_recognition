![alt text](https://imgs.xkcd.com/comics/silence_2x.png)

# Built currently unstable

Working on a stable command line interface

# How to:

This fork of DejaVu includes a few improvements to the code, a similarity search feature I call GridHash and a PDF of a master thesis explaining many implementation details.

In order to fingerprint audio you require a MySQL database and a local folder where you store a number of audio tracks.

Inlcude the database name of your database to: <pre> database.py </pre>

Include the path to the directory where you store your audio in: <pre> exportData.py </pre>

In order to fingerprint and add tracks to the database run the main method of fingerprintWorker.py and modify the number of songs you want indexed.

In order to recognize a specific song run the main method of experiments.py and modify the path.

# Your patience is appreciated:

I will integrate microphone recognition and the possibility to pass arguments from the command line as soon as possible.
That will eleminate the current hurdles. Thank you.

In the mean time, the thesis-doc folder of this repo contains a Master thesis document detailing this implementation and the differences from DejaVu.
