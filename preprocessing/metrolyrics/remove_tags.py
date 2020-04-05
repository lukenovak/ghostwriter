"""
Quick change to the lyrics CSV to remove artist IDs. This way we can make it into a line-by-line raw text dataset.
"""
import pandas
from sklearn.model_selection import train_test_split

from config import DATA_DIR

if __name__ == "__main__":
    lyrics_csv = DATA_DIR / "metrolyrics" / "lyrics.csv"
    df = pandas.read_csv(lyrics_csv)
    
    lyrics_col = df["lyrics"].dropna()
    lyrics_col = lyrics_col.apply(lambda lyric: lyric.replace("<ENDLINE>", " "))
    
    lyrics_train, lyrics_test = train_test_split(lyrics_col, train_size=0.8)
    
    with open(DATA_DIR / "metrolyrics.train.raw", "w") as train_f,\
            open(DATA_DIR / "metrolyrics.test.raw", "w") as test_f:
        for lyric in lyrics_train:
            train_f.write(lyric + "\n")
            
        for lyric in lyrics_test:
            test_f.write(lyric + "\n")
