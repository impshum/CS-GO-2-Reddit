from requests import get
from datetime import datetime
from bs4 import BeautifulSoup
import praw
import schedule
import tweepy
from time import sleep

# DO NOT EDIT ABOVE THIS LINE

twitter_on = 1 # post to twitter
consumer_key = 'XXXX'
consumer_secret = 'XXXX'
access_key = 'XXXX'
access_secret = 'XXXX'

reddit_on = 1 # post to reddit
client_id = 'XXXX'
client_secret = 'XXXX'
reddit_user = 'XXXX'
reddit_pass = 'XXXX'

target_subreddit = 'XXXX' # subreddit to post to
target_team = 'XXXX' # case sensitive

schedule_time = '07:30' # 24hr format

test_mode = 1 # flip the switch

# DO NOT EDIT BELOW THIS LINE

if not test_mode:
    if reddit_on:
        reddit = praw.Reddit(user_agent='CS:GO 2 Reddit (by /u/impshum)'',
                             client_id=client_id, client_secret=client_secret,
                             username=reddit_user, password=reddit_pass)
    if twitter_on:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)
else:
    print('\nTEST MODE\n')


def lovely_soup(url):
    headers = {
        "referer": "https://www.hltv.org/stats",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    return BeautifulSoup(get(url, headers=headers).text, "lxml")


def database(line):
    with open('done.txt', 'r') as f:
        data = f.read()

    if line not in data:
        with open('done.txt', 'a') as f:
            f.write(line + '\n')
        return False
    else:
        return True


def get_matches():
    matches = lovely_soup('http://www.hltv.org/matches/')
    matches_list = []
    upcomingmatches = matches.find('div', {'class': 'upcoming-matches'})
    matchdays = upcomingmatches.find_all('div', {'class': 'match-day'})

    for match in matchdays:
        matchDetails = match.find_all('table', {'class': 'table'})

        for getMatch in matchDetails:
            matchObj = {}

            matchObj['date'] = match.find(
                'span', {'class': 'standard-headline'}).text
            matchObj['time'] = getMatch.find(
                'td', {'class': 'time'}).text.strip()

            if (getMatch.find('td', {'class': 'placeholder-text-cell'})):
                matchObj['event'] = getMatch.find(
                    'td', {'class': 'placeholder-text-cell'}).text
            elif (getMatch.find('td', {'class': 'event'})):
                matchObj['event'] = getMatch.find(
                    'td', {'class': 'event'}).text
            else:
                matchObj['event'] = None

            if (getMatch.find_all('td', {'class': 'team-cell'})):
                matchObj['team1'] = getMatch.find_all(
                    'td', {'class': 'team-cell'})[0].text.strip()
                matchObj['team2'] = getMatch.find_all(
                    'td', {'class': 'team-cell'})[1].text.strip()
            else:
                matchObj['team1'] = None
                matchObj['team2'] = None

            matches_list.append(matchObj)

    return matches_list


def main():
    for match in get_matches():
        team1 = match['team1']
        team2 = match['team2']

        if team1 == target_team or team2 == target_team:
            event = match['event']
            time = match['time']
            date = datetime.strptime(match['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            title = "{} {} | {} vs {} | {}".format(
                date, time, team1, team2, event)

            if not database(title):
                print(title)

                if not test_mode:
                    if reddit_on:
                        reddit.subreddit(target_subreddit).submit(
                            title=title, selftext='')
                    if twitter_on:
                        api.update_status(status=title)


if __name__ == '__main__':
    main()
    schedule.every().day.at('07:30').do(main)
    while True:
        schedule.run_pending()
        sleep(1)
