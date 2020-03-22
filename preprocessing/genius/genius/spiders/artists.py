from csv import writer
from json import loads
import scrapy
from string import ascii_lowercase

from config import DATA_DIR, WRITE_TEMP_PROGRESS


class ArtistsDirectorySpider(scrapy.Spider):
    name = "artists-directory"

    def start_requests(self):
        characters = list(ascii_lowercase)
        characters.append("0")
        urls = [f'https://genius.com/artists-index/{char}' for char in characters]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        letter = response.url[-1]
        artists = response.xpath('//*[@id="main"]').css(".artists_index_list").xpath("./li/a")
        artist_names = artists.xpath("./text()").getall()
        artist_links = artists.xpath("./@href").getall()
        artist_info = zip(artist_names, artist_links)
        
        for artist_name, artist_link in artist_info:
            yield scrapy.Request(url=artist_link, callback=self.parse_artist_id,
                                 cb_kwargs={"artist_name": artist_name})

    def parse_artist_id(self, response, artist_name):
        # Pull artist ID from meta tag in artist page
        artist_id = response.xpath('//head/meta[@name="newrelic-resource-path"]/@content').get()
        artist_id = artist_id.lstrip("/artists/")
        page = 1
    
        yield scrapy.Request(url=f'https://genius.com/api/artists/{artist_id}/songs?page={page}',
                             callback=self.pull_songs_by_artist_ids, cb_kwargs={"artist_name": artist_name,
                                                                                "artist_id": artist_id,
                                                                                "page": page})
        
    def pull_songs_by_artist_ids(self, response, artist_name, artist_id, page):
        songs_by_artist_resp = loads(response.body)["response"]
        artist_songs = songs_by_artist_resp["songs"]
        
        artist_song_urls = [(song.get("id"), song.get("title"), song.get("url")) for song in artist_songs]
        
        for id, title, url in artist_song_urls:
            yield scrapy.Request(url=url, callback=self.pull_song_lyrics,
                                 cb_kwargs={"artist_name": artist_name,
                                            "artist_id": artist_id,
                                            "song_name": title,
                                            "song_id": id})
        
        next_page = songs_by_artist_resp["next_page"]
        if next_page is not None:
            yield scrapy.Request(url=f'https://genius.com/api/artists/{artist_id}/songs?page={next_page}',
                                 callback=self.pull_songs_by_artist_ids, cb_kwargs={"artist_id": artist_id,
                                                                                    "page": next_page})
            
    def pull_song_lyrics(self, response, song_name, song_id, artist_name, artist_id):
        lyrics_par = response.xpath("//div[@class='lyrics']/p")
        lyrics_el_text = lyrics_par.xpath("./text() | ./*/text()").getall()
        lyrics = [s.strip("\n") for s in lyrics_el_text]
        with open(DATA_DIR / f'{artist_id}_{song_id}.txt', "w") as f:
            f.write(f'Artist: {artist_name} ({artist_id})\n')
            f.write(f'Song: {song_name} ({song_id})\n')
            for lyric in lyrics:
                f.write(lyric + " ")
