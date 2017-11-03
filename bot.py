import praw
import requests
import urllib.request
import time
import operator
from bs4 import BeautifulSoup
from lxml import html
from datetime import datetime
BannedUsers = []

todayDatetime = datetime.today()
integerDate = datetime.weekday(todayDatetime)

gmedate = ""
gmetime = ""
hometeam = ""
awayteam = ""
newTable = True

GameList = []
reddit = praw.Reddit(username = "",
					password = "",
					client_id = "",
					client_secret = "",
					user_agent = "")

class GameInformation(object):
		Home = ""
		Away = ""
		GameDate = ""
		GameTime = ""
		AlreadyPosted = 0
		
		def __init__(self, Home, Away, Gamedate, Gametime, alreadyPosted):
			self.Home = Home
			self.Away = Away
			self.GameDate = Gamedate
			self.GameTime = Gametime
			self.AlreadyPosted = alreadyPosted

def determineName(string):
	return {
        'team-90-21'    : 'Toronto Maple Leafs',
        'team-90-28'    : 'Winnipeg Jets',
        'team-90-19'    : 'St. Louis Blues',
        'team-90-16'    : 'Pittsburgh Penguins',
        'team-90-3'     : 'Calgary Flames',
        'team-90-6'     : 'Edmonton Oilers',
        'team-90-15'    : 'Philadelphia Flyers',
        'team-90-18'    : 'San Jose Sharks',
        'team-90-27'    : 'Nashville Predators',
        'team-90-1'     : 'Boston Bruins',
        'team-90-10'    : 'Montreal Canadiens',
        'team-90-2'     : 'Buffalo Sabres',
        'team-90-17'    : 'Colorado Avalanche',
        'team-90-13'    : 'New York Rangers',
        'team-90-23'    : 'Washington Capitals',
        'team-90-14'    : 'Ottawa Senators',
        'team-90-30'    : 'Minnesota Wild',
        'team-90-5'     : 'Detroit Red Wings',
        'team-90-4'     : 'Chicago Blackhawks',
        'team-90-24'    : 'Arizona Coyotes',
        'team-90-25'    : 'Anaheim Ducks',
        'team-90-8'     : 'Los Angeles Kings',
        'team-90-12'    : 'New York Islanders',
        'team-90-29'    : 'Columbus Blue Jackets',
        'team-90-26'    : 'Florida Panthers',
        'team-90-20'    : 'Tampa Bay Lightning',
        'team-90-37'    : 'Las Vegas Golden Knights',
        'team-90-11'    : 'New Jersey Devils',
        'team-90-7'     : 'Carolina Hurricanes',
        'team-90-22'    : 'Vancouver Canucks',
        'team-90-9'     : 'Dallas Stars',
    }.get(string, 'Team Undef') 

def findAllowedPosters():
	subreddit = reddit.get_subreddit("NHLStreaming")
	posts = subreddit.getposts()
				
def getTodaysGames():
	page = requests.get('http://www.espn.com/nhl/schedule')
	htmlText = page.text
	Soup = BeautifulSoup(htmlText, 'html.parser')
	
	tables = Soup.findAll("table", {"class": "tablehead"})
	for table in tables:
		if(time.strftime("%A") in table.text):
			rows = table.findAll('tr')
			for row in rows:
				if(time.strftime("%A") in row.text):
					gmedate = row.text
				else:					
					rowClassValue = row.get('class')					
					tds = row.findAll('td')
					if("oddrow" in rowClassValue) or ("evenrow" in rowClassValue):						
						awayteam = determineName(rowClassValue[1])
						hometeam = determineName(rowClassValue[2])
						tds = row.findAll('td')
						for td in tds:
							if(":" in td.text) or ("PM" in td.text):
								gmetime = td.text
								createGame(hometeam, awayteam, gmedate, gmetime)

def generateTitle(GameInformation):
	#Generate Post Title
	post_title = GameInformation.GameDate + ', 2017 | ' + GameInformation.Away + ' @ ' 
	post_title += GameInformation.Home + " [" + GameInformation.GameTime + " EST]"
	return post_title
	
def generateBody(GameInformation):
	post_text = '**' + GameInformation.Away + ' @ ' + GameInformation.Home + '**\n\n'
	post_text += 'Game Start: ' + GameInformation.GameTime + ' EST\n\n'
	post_text += 'Please limit streams to YouTube or Ad-Free sites only -- All others will be removed'
	return post_text

def submitPost(Title, Body):
	#Submits post to NHLStreaming Subreddit
	reddit.subreddit('NHLStreaming').submit(title=Title, selftext=Body)

def createGame(Home, Away, GDate, Gametime):
	game = GameInformation(Home, Away, GDate, Gametime, 0)
	GameList.append(game)

#FOR TESTING PUT STUFF HERE
getTodaysGames()

#CORRECT ALGORITHM
while True:
	if(integerDate == 6):
		print('sunday')
	
	currentTime = time.strftime("%H%M")
	currentTimeInteger = int(currentTime)
	if(currentTimeInteger == 0000):
		getTodaysGames()
	else:
		for Game in GameList:
			publishHour = Game.GameTime.partition(":")[0]
			publishHourInteger = int(publishHour)
			publishHourInteger = publishHourInteger - 1
			publishHourInteger = publishHourInteger + 12
			
			publishMinute = Game.GameTime.partition(":")[2]
			publishMinute = publishMinute.split()[0]
			publishMinuteInteger = int(publishMinute)
			if(publishHourInteger < 10):
				if(publishMinuteInteger == 0):
					publishTimeString = str(0) + str(publishHourInteger) + str(publishMinuteInteger) + str(0)
				else:
					publishTimeString = str(0) + str(publishHourInteger) + str(publishMinuteInteger)
			else:	
				if(publishMinuteInteger == 0):
					publishTimeString = str(0) + str(publishHourInteger) + str(publishMinuteInteger) + str(0)
				else:
					publishTimeString = str(publishHourInteger) + str(publishMinuteInteger)	
	
			if(publishTimeString == time.strftime("%H%M") and Game.AlreadyPosted == 0):
				Game.AlreadyPosted = 1
				PostTitle = generateTitle(Game)
				PostBody = generateBody(Game)
				submitPost(PostTitle, PostBody)
				
				
