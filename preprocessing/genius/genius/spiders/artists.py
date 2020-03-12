from csv import writer
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
        
        # Save progress to CSV file
        if WRITE_TEMP_PROGRESS:
            with open(DATA_DIR / f'artists_all_{letter}.csv', "w") as f:
                csv_writer = writer(f)
                for artist_tuple in artist_info:
                    csv_writer.writerow(artist_tuple)
        
        for artist_name, artist_link in artist_info:
            yield scrapy.Request(url=artist_link, callback=ArtistPageSpider.parse,
                                 cb_kwargs={"artist_name": artist_name})


class AritstPageSpider(scrapy.Spider):
    name = "artist"
    
    def parse(self, response, artist_name=None):
        # Pull artist ID from meta tag in artist page
        artist_id = response.xpath('//head/meta[@name="newrelic-resource-path"]/@content')
        artist_id = artist_id.lstrip("/artists/")
        
        # Save progress to text file
        if WRITE_TEMP_PROGRESS:
            with open(DATA_DIR / f'id_{artist_name}.data',  "w") as f:
                f.write(f'{artist_name}, {artist_id}')
        
        # TODO -- hit https://genius.com/api/artists/**/songs?page=1, then paginate
        # TODO -- follow those links via a SongLyric Scraper
