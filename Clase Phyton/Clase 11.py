import bs4
import requests



url_base: "https://www.innovasport.com/top-sellers-casual/c/top-sellers-casual?q=%3Arelevance&page={}"

for n  in range (1,5):
    print (url_base.format(n))


