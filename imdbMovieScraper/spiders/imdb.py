import scrapy
from bs4 import BeautifulSoup
import re
import csv


class Imdb(scrapy.Spider):
    name = "imdb"

    def start_requests(self):
        urls = [
            "http://www.imdb.com/search/title?year=2017&title_type=feature&view=simple"
        ]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]

        soup = BeautifulSoup(response.body, "html.parser")
        movies = soup.find_all('div',attrs={'class':'lister-item'})

        # Opening CSV File for writing
        with open('imdb.csv','w', newline='') as file:            
            fieldnames = ['name', 'img', 'year', 'rating', 'votes', 'director', 'actors']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for movie in movies:
        
                # These values needs cleaning
                year_with_paran = movie.find('span',attrs={'class':'lister-item-year'}).get_text()
                total_rating = movie.select('.col-imdb-rating strong')[0].get('title')
                people = movie.select('div.col-title > span > span + span')[0].get('title').split(',')

                print("********************************************************************")

                row = {
                    'name':  movie.find('img').get('alt'),
                    'img': movie.find('img').get('src'),
                    'year': re.findall('\((.*?)\)',year_with_paran)[-1],
                    'rating': total_rating.split(" base on ")[0],
                    'votes': total_rating.split("base on ")[1].replace(" votes",""),
                    'director': people[0].replace("(dir.)",""),
                    'actors': ",".join(people[1:])
                }

                # writing row to file
                writer.writerow(row)
                print(row)


