import matplotlib.pyplot as plt
from math import ceil
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
    print(artist)
    artist_ids[artist["id"]] = artist["artist"]

artist_counts = {}
# get the song count per artist
for song in songs_reader:
    artist_name = artist_ids[song["artist"]]
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

print(hist_bins)
fig, ax = plt.subplots()
bars = ax.bar(hist_bins.keys(), hist_bins.values(), 0.5, color = 'green')
ax.set_ylabel("Number of Artists")
ax.set_xlabel("Number of Songs")
ax.set_title("Distribution of songs per artist in dataset")

# autolabler adapted from matplotlib documentation

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