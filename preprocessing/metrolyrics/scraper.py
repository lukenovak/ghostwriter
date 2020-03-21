from tswift import Song
import json

# Assuming we have the songs we want in the json file
songs_file = open("./db/songs.json", "+r")
songs_obj = json.loads(songs_file.read())  # this is about 22mb so we should be ok to read this into memory
songs_file.close()

for song in songs_obj:
    new_query = Song(song["song"], song["artist"])
    try:
        new_query.load()
        print(new_query.lyrics)
    except:
        print(f"Unable to find lyrics for {song['song']} by {song['artist']}")
