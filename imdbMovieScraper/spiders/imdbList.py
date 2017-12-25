import scrapy
from bs4 import BeautifulSoup
import re
import csv


class Imdblist(scrapy.Spider):
    name = "imdblist"

    def start_requests(self):
        urls = [
            "http://www.imdb.com/list/ls053536561/"
        ]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        soup = BeautifulSoup(response.body, "html.parser")

        handleMissingText = lambda x : x[0].get_text().strip() if len(x)>0 else ""
        handleMissingAttrMult = lambda x,y : x[0].get(y)[-1].strip() if len(x)>0 else ""
        handleMissingAttrSingle = lambda x,y : x[0].get(y).strip() if len(x)>0 else ""

        movies = soup.find_all("div",attrs={"class":"lister-item"})

        # Opening CSV File for writing
        with open("imdb.csv","w", newline="") as file:            
            fieldnames = ["name","img","content",
                          "metascore","length","score_sentiment",
                          "genre","synposis","year",
                          "rating","votes","director",
                          "actors","boxOffice","link"]

            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for movie in movies:
        
                year_with_paran = movie.find("span",attrs={"class":"lister-item-year"}).get_text()
                row = {
                    "name": movie.find("img").get("alt").strip(),
                    "img": movie.find("img").get("src").strip(),
                    "content": movie.select(".certificate")[0].get_text().strip(),
                    "metascore": handleMissingText(movie.select(".metascore")),
                    "length": movie.select(".runtime")[0].get_text().replace("min","").strip(),
                    "score_sentiment": handleMissingAttrMult(movie.select(".metascore"),"class"),
                    "genre": handleMissingText(movie.select(".genre")),
                    "synposis": handleMissingText(movie.select(".ratings-bar + p")),
                    "year": re.findall("\((.*?)\)",year_with_paran)[-1],
                    "rating": handleMissingText(movie.select(".imdb-rating + strong")),
                    "votes": handleMissingText(movie.select(".ratings-bar + p + p + p > span + span")),
                    "director": handleMissingText(movie.select(".ratings-bar + p + p > a")),
                    "boxOffice": handleMissingText(movie.select(".ratings-bar + p + p + p > span:nth-of-type(5)")).replace("$",""),
                    "actors": ",".join([actor.get_text() for actor in movie.select(".ratings-bar + p + p > a")[1:]]),
                    "link": handleMissingAttrSingle(movie.select(".lister-item-header a"),"href")
                }
                print("***************************************************************************")
                print(row)
                # writing row to file
                writer.writerow(row)


