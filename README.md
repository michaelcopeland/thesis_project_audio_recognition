![alt text](https://imgs.xkcd.com/comics/silence_2x.png)

# How to:

This fork of DejaVu includes a few improvements to the code, a similarity search feature I call GridHash and a PDF of my master thesis explaining many implementation details.

# MySQL database:

In order to fingerprint audio you need a MySQL database. Add MySQL to your environment variables, then:
<pre> mysql > create database database_name </pre>

Login credentials to the database are stored in the cnf.cnf file. It's a JSON format file that gets parsed by the script every time the program is run.

<pre>
{
    "database": {
        "host": "127.0.0.1",
        "user": "root",
        "passwd": "your pass",
        "db": "database_name",
        "port": 3306
    }
}
</pre>

The entry point is interface.py. The help tag will display the entire command line interface. The database tag will display your credentials from cnf.cnf.
<pre> 
python interface.py -h
python interface.py -db
</pre>

If you want to clear everything in the database and reset your tables run the kill_db tag:

<pre> python interface.py -k </pre>

# Landmark algorithm

In order to fingerprint songs the idea is simple: Put all of your files in one directory and specify how many of them you want added to the database. For instance, to fingerprint 23 songs from the folder my_songs run the following line. You get the idea.

<pre> python interface.py -i my_songs -c 23 </pre>

You can recognize via microphone (sort of) and from a file. Notes on the microphone's issues in a moment.

To recognize from a file you must pass the file path and the number of seconds:
<pre> python interface.py -rf my_songs/everythingiscool.wav -c 4 </pre>

To recognize from the mic you must specify the number of seconds:
<pre> python interface.py -r mic 4 </pre>

# GridHash algorithm

The gridhash algorithm is a similarity calculating tool. It allows you to compare how similar one audio track is to another on a scale of 0 (totally disimilar) to 1 (identical). The algorithm works well on wave files and not so well on mp3s. I'm working on a few improvements.

The algorithm takes audio files from one directory, processes them and then stores corresponding gridhash objects. Meaning that a song called "good times.mp3" from your input folder will result in "good times.grid" in your output folder. You can define the path to your desired folders in the cnf.cnf file:

<pre>
"grid_settings": {
        "time_interval": 100,
        "freq_interval": 100,
        "time_tolerance": 30,
        "freq_tolerance": 30
    },
    "grid_paths":{
        "files_in": "D:\\path\\to\\input\\folder",
        "files_out": "C:\\path\\to\\output\\folder"
}
</pre>

You will have noticed the grid_settings section above. The values refer to the gridhash algorithm and are explained in the theis_paper.pdf. They can be left unchanged.

Once you have defined your folders you can now process your audio files using the command bellow. The number specifies how many files to process. Pass 0 will process all of the files in your directory.

<pre> python interface.py -ex 15 </pre>

Once you are done with creating your gridhash objects, you can check the similarity of files in your grid folder:

<pre> python interface.py -sim your_file.grid </pre>

This will print the similarity, your_file.grid, some_other_file.grid in order of similarity. For example, if I run the command I receive this trace:
<pre>
(0.812, 'c1.grid', 'c2.grid')
(0.211, 'c1.grid', 'cmd.grid')
(0.188, 'c1.grid', 'strm.grid')
(0.156, 'c1.grid', 'RATH - Rain Hard Loop 08.grid')
(0.148, 'c1.grid', 'RATH - Rain on Plastic Outside Loop.grid')
(0.133, 'c1.grid', 'SFX Large Wave Splash on Rocks 21.grid')
(0.125, 'c1.grid', 'SFX Medium Wave Splash on Rocks 12.grid')
(0.117, 'c1.grid', 'AMBIENCE Huge Waves 1m Away From Impact Point 2.grid')
(0.117, 'c1.grid', 'AMBIENCE Huge Waves 2m Away From Impact Point 1.grid')
(0.117, 'c1.grid', 'RATH - Rain and Distant Thunder Loop 01.grid')
(0.094, 'c1.grid', 'estring.grid')
(0.078, 'c1.grid', 'RATH - Rain, Distant Thunder and Bird Loop.grid')
(0.07, 'c1.grid', 'aic.grid')
(0.07, 'c1.grid', 'estring2.grid')
(0.07, 'c1.grid', 'river1.grid')
(0.062, 'c1.grid', 'river2.grid')
</pre>

# Remaining issues:

Microphone functionality is implemented. However, results are terrible. I believe this issue may be due to my laptop mic, but the issue persists even after removal of the in-build noise cancellation. More testing is required.

The experiements.py script is broken due to the heavy refactoring. Slated for fixing. It contains the methods used in testing the above mentioned algorithms.

The gridHash algorithm uses minHash to quickly compute the Jaccard similarity between to grid objects. However, minHash computes an unweighted Jaccard distance. Meaning, that if your songs have many repeating features, then the number of times these repeat does not really matter. Using a weightedMinHash could be a solution to this issue.

Spectrogram peak detection is performed on a constant area of 20 square sample points. This is problematic when you have very short audio snippets since you might not be able to detect anything. Hence, I am considering a scaling function.

# TL;DR

My thesis paper is also available for reference and details. It is in thesis-doc/thesis_paper.pdf in this repo. Hope you find some of this work useful ;)
