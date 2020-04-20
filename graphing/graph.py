import matplotlib.pyplot as plt
from math import ceil, floor
from statistics import median
import csv

# load the data and read it into a dict
data_location = "../data/metrolyrics"
songs_file = open(f"{data_location}/lyrics.csv", "r")
artists_file = open(f"{data_location}/artists.csv", "r")
songs_reader = csv.DictReader(songs_file)
artists_reader = csv.DictReader(artists_file)

artist_ids = {}
# get the translation from number to artist
for artist in artists_reader:
    artist_ids[artist["id"]] = artist["artist"]

unigram_counts = {}
word_count = 0
# Gets a unigram word count from the given list of words
def add_unigram_counts(lyrics):
    cleaned_song = lyrics.replace("<ENDLINE>", " ")
    cleaned_song = cleaned_song.upper()
    simple_tokens = cleaned_song.split(" ")
    length = len(simple_tokens)
    for token in simple_tokens:
        if token in unigram_counts:
            unigram_counts[token] += 1
        else:
            unigram_counts[token] = 1
    return length

# get the length of the song in tokens (words)
def get_song_length(song):
    cleaned_song = song.replace("<ENDLINE>", " ")
    simple_tokens = cleaned_song.split(" ")
    return len(simple_tokens)

song_lens = []
artist_counts = {}
# get the song count per artist and lyric length data
for song in songs_reader:
    artist_name = artist_ids[song["artist"]]
    lyrics = song["lyrics"]
    song_lens.append(get_song_length(lyrics))
    word_count += add_unigram_counts(lyrics)
    if artist_name in artist_counts:
        artist_counts[artist_name] += 1
    else:
        artist_counts[artist_name] = 1

# gather count bins for a histogram
hist_bins = {}
for artist in artist_counts:
    bin = artist_counts[artist]
    if bin > 30:
        continue
    if bin in hist_bins:
        hist_bins[bin] += 1
    else:
        hist_bins[bin] = 1

fig, ax = plt.subplots()
bars = ax.bar(hist_bins.keys(), hist_bins.values(), 0.5, color = 'green')
ax.set_ylabel("Number of Artists")
ax.set_xlabel("Number of Songs")
ax.set_title("Distribution of songs per artist in dataset")

# autolabler adapted from matplotlib documentation
# (source https://matplotlib.org/gallery/api/barchart.html)
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(bars)
fig.tight_layout()
plt.savefig("./graphs/songs_per_artist_dist.png", dpi=200)

# remove bottom and top 1% of lengths as outliers
song_lens = sorted(song_lens)
cleaned_song_lens = []
for song in song_lens[floor(0.01 * len(song_lens)):ceil(0.99 * len(song_lens))]:
    if song > 1:
        cleaned_song_lens.append(song)

# plot the uncleaned song length data
fig, ax = plt.subplots()
ax.hist(song_lens[floor(0.01 * len(song_lens)):ceil(0.99 * len(song_lens))], bins=20, color='red', edgecolor='maroon')
ax.set_xlabel("Song Length")
ax.set_ylabel("Number of Songs")
ax.set_title("Distribution of Song Length (in space separated tokens), Pre-Cleaning")
fig.tight_layout() # this line ensures nothing is cut off from the graph
plt.savefig("./graphs/song_length_dist_dirty.png", dpi=200)

# plot the cleaned song length data
fig, ax = plt.subplots()
ax.hist(cleaned_song_lens, bins=20, color='red', edgecolor = 'maroon')
ax.set_xlabel("Song Length")
ax.set_ylabel("Number of Songs")
ax.set_title("Distribution of Song Length (in space separated tokens)")
fig.tight_layout()
plt.savefig("./graphs/song_length_dist.png", dpi=200)


# print median probabity unigram
word_probs = []
print(word_count)
for unigram in unigram_counts:
    word_probs.append(unigram_counts[unigram]/word_count)
print(f"Median word probability is {median(word_probs)}")
print(f"Max word probability is {max(word_probs)}")
