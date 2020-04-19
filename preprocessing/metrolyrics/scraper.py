from tswift import Artist, Song
import json
import csv
from time import time
from random import shuffle

# Assuming we have the songs we want in the json file
songs_file = open("./db/songs.json", "+r")
songs_obj = json.loads(songs_file.read())  # this is about 22mb so we should be ok to read this into memory
songs_file.close()

songs_with_lyrics = [] * 400000
artist_ids = {}

next_artist_id = 0
length = len(songs_obj)
start = time()

# the tswift api works best when we are using artists as it loads up many songs at once, saving us a ton of time
# thus we are going to get songs by artists first
# Let's gather all of our artists first
for song in songs_obj:
    artist = song["artist"]
    # we need to convert the artist name to a number, so if we haven't seen the artist we add them
    if artist not in artist_ids:
        artist_ids[artist] = next_artist_id
        next_artist_id += 1

print(f"successfully id tagged {len(artist_ids)} artists")

artist_to_tswift = {}
i = 0
songs_loaded = 0
start = time()
# now, use tswift to search for all of these artists
for artist in artist_ids:
    if len(artist_to_tswift) > 1:
        break
    if i % 10 == 0:
        print(f"searched {i} of {len(artist_ids)}, loading {songs_loaded} songs in {time() - start} seconds")

    tswift_artist = Artist(artist.replace(" &", ""))
    if len(tswift_artist.songs) > 0:
        try:
            tswift_artist.load()
        except:
            i +=1
            continue
        songs_loaded += len(tswift_artist.songs)
        artist_to_tswift[artist] = tswift_artist
        i +=1
        continue
    elif artist[0:4] == "The ":
        tswift_artist = Artist(artist[4:])
        try:
            tswift_artist.load()
        except:
            i += 1
            continue            
        songs_loaded += len(tswift_artist.songs)
        artist_to_tswift[artist] = tswift_artist
        i += 1
        continue
    else:
        print(f"unable to load artist {artist}")
        i +=1

# remove duplicate songs
def remove_dups(songs):
    nondups = set()
    for song in songs:
        if not song.title in nondups:
            nondups.add(song.title)
            yield song
        else:
            print("removed dup")


successes = 0
i = 0
start = time()
# now iterate through the artists getting all of the songs
for artist in artist_to_tswift:
    print(f"indexing songs for {artist}")
    tswift_artist = artist_to_tswift[artist]
    if i % 100 == 0:
        print(f"indexed {i} of {songs_loaded} songs in {time() - start} seconds")
    lyrics = None

    for song in remove_dups(tswift_artist.songs):

        if i % 100 == 0:
            print(f"successfully indexed {successes} of {i} out of a "
                  f"total of {songs_loaded} songs in {time() - start} seconds")
        title = song.title
        try:
            lyrics = song.lyrics.replace("\n", "<ENDLINE>")
        except:
            print(f"could not get {title} by {artist}")

        if len(lyrics) == 0:
            i += 1
            continue

        # index, name, text, label
        song_lyric_obj = {"index": successes,
                          "song_title": title.replace(" ", "_") + f"-{i}",
                          "lyrics": lyrics,
                          "artist": artist_ids[artist]}
        songs_with_lyrics.append(song_lyric_obj)
        i += 1
        successes +=1

# now that we have the song/lyric object for all of our songs, we write it to a csv
csv_keys = songs_with_lyrics[0].keys()
output_file = open("./data/lyrics.csv", "+w")
dw = csv.DictWriter(output_file, csv_keys)
dw.writeheader()
dw.writerows(songs_with_lyrics)
output_file.close()

# we also need to write the artist id guide
artist_id_file = open("./data/artists.csv", "+w")
artists = artist_ids.keys()
for artist in artists:
    artist_id_file.write(f"{artist}, {artist_ids[artist]}\n")
