"""
Generates the data assets necessary to integrate the Genius data into the Metrolyrics code and the
Hugging-Face wrappers.

Written by Michael Wheeler.
"""
from os import PathLike
from pandas import DataFrame
from re import search
from typing import List, Tuple

from config import DATA_DIR


def generate_dataframe_from_files() -> Tuple[DataFrame, List]:
    """
    Iterates over the DATA_DIR and extracts the lyrics
    :return:
    """
    data = []
    failed_files = []
    
    for item in DATA_DIR.iterdir():
        if item.suffix != ".txt":
            continue
        try:
            artist_id, artist_name, song_id, song_lyrics = extract_info_from_lyrics_file(item)
            data.append([song_id, song_lyrics, artist_id, artist_name])
            if len(data) % 10000 == 0:
                print(f'SUCCESS: {len(data)}')
        except RuntimeWarning as e:
            failed_files.append(str(e))
            if len(failed_files) % 1000 == 0:
                print(f'ERROR: {len(failed_files)}')
            continue
    
    data = [{"song_id": obs[0],
             "song_lyrics": obs[1],
             "artist_id": obs[2],
             "artist_name": obs[3]} for obs in data]
    
    return DataFrame.from_dict(data), failed_files
    

def extract_info_from_lyrics_file(lyric_filepath: PathLike) -> Tuple[str, str, str, str]:
    with open(lyric_filepath, "r") as f:
        try:
            artist_id_line = next(f)
            song_id_line = next(f)
            song_lyrics = next(f)
        except StopIteration:
            raise RuntimeWarning(f'{lyric_filepath}')
        
        artist_match = search("Artist: (.+?) \((\d+)\)", artist_id_line)
        artist_name = artist_match.group(1)
        artist_id = artist_match.group(2)
        song_id = search("\((\d+)\)", song_id_line).group(1)
        return artist_id, artist_name, song_id, song_lyrics
    

if __name__ == "__main__":
    df, failures = generate_dataframe_from_files()

    df.to_pickle(DATA_DIR / "genius_dataframe.pickle")
    
    with open(DATA_DIR / "genius_fauled_files.txt", "w") as f:
        for path_ in failures:
            f.write(path_)
    
    unique_artists_mapping = df[["artist_id", "artist_name"]].drop_duplicates()
    unique_artists_mapping.to_pickle(DATA_DIR / "genius_artist_id_map.pickle")
