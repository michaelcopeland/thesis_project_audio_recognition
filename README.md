![alt text](https://imgs.xkcd.com/comics/silence_2x.png)

# How to:

This fork of DejaVu includes a few improvements to the code, a similarity search feature I call GridHash and a PDF of my master thesis explaining many implementation details.

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

In order to fingerprint songs the idea is simple. Put all of your files in one directory and specify how many of them you want added to the database. For instance, to fingerprint 23 songs from the folder my_songs run the following line. You get the idea.

<pre> python interface.py -i my_songs -c 23 </pre>

You can recognize via microphone (sort of) and from a file. Notes on the microphone's issues in a moment.

To recognize from a file you must pass the file path and the number of seconds:
<pre> python interface.py -rf my_songs/everythingiscool.wav -c 4 </pre>

To recognize from the mic you must specify the number of seconds:
<pre> python interface.py -r mic 4 </pre>

# Remaining issues:

Microphone functionality is implemented. However, results are terrible. I believe this issue may be due to my laptop mic, but the issue persists even after removal of the in-build noise cancellation. More testing is required.

Additinally, the gridHash functionality is not included in the CLI yet. That's going to be on the next commit. It will involve its own config file and number of small changes.

Also, the experiements.py script is broken due to the heavy refactoring. Slated for fixing.

Check the PDF in thesis-doc for the TL;DR
