# Bitcointalk scrapper

## What is this ?
This script produces a JSON file in the data/ folder.  
This file contains data on users of Bitcointalk forum.
More precisely, it gets the data of a user if this user have entered a bitcoin adress in its profile.  

The JSON file have this structure :   
`` {   
      'bitcoin_address' : { 'Name': 'your_name', 'Age': 'your_age', ... },  
      ...  
   }  
``  

The file name follow this pattern : start-stop.json  
Where start is the id of the first user in the file and stop the last.

The script can be launched at different times i.e. you can scrap users 1 to 1000 in the morning and then scrap 1000 to 2000 in the evening. The script will ask you where to begin and to stop at launch.
Be sure you always start with the id you've ended on last time.  

## Getting started

### Prerequisites

This is a Python 3 script.  
`` sudo apt-get install python3.6 ``  
  
So you need Python 3, but also cfscrape, BeautifulSoup and requests  
`` pip install cfscrape``   
`` pip install bs4``   
`` pip install requests``  
 
### Installation
Just clone this repository.  
`` git clone https://github.com/vdtdg/bitcointalkscrapper.git  ``

### How to use
Launch it by command line **directly in the folder src**  
`` python3 scrapper.py``  
Don't
`` python3 src/scrapper.py``  

The script will ask you from where to start and when to stop.  
With the script is supplied the first 760150 users, so you can start with this value.  
If you want a short demo run, put 760200 into the stop value.

The script will also ask you for a proxy, if you don't have one, put "no". The proxy functionnality has not been fully tested, so be careful

## Authors
Valérian de THEZAN de GAUSSAN  
Université Claude Bernanrd Lyon 1
