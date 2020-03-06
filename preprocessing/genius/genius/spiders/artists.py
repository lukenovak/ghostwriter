from csv import writer
import scrapy
from string import ascii_lowercase

from config import DATA_DIR


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
        with open(DATA_DIR / f'artists_all_{letter}.csv', "w") as f:
            csv_writer = writer(f)
            for artist_tuple in artist_info:
                csv_writer.writerow(artist_tuple)
        # TODO -- follow the artists links via ArtistPageSpider


class AritstPageSpider(scrapy.Spider):
    name = "artist"
    
    def parse(self, response):
        # TODO -- get meta content="/artists/***" with name="newrelic-resource-path
        # TODO -- hit https://genius.com/api/artists/**/songs?page=1, then paginate
        # TODO -- follow those links via a SongLyric Scraper
        pass
