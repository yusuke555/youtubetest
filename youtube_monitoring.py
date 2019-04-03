# -*- coding: utf-8 -*-
"""
Created on Sun 2019

@author: Yusuke Nakamoto
"""

#!/usr/bin/python

import sys
import configparser

from oauth2client.tools import argparser
from apiclient.discovery import build
from apiclient.errors import HttpError
from openpyxl import Workbook, load_workbook


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.

inifile = configparser.ConfigParser()
inifile.read('./config.ini', 'UTF-8')

DEVELOPER_KEY = inifile.get('DEVELOPER_KEY', 'key')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUVE_CHANNEL_ID = inifile.get('YOUTUVE_CHANNEL_ID', 'channelId')

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    part="id,snippet",
    maxResults=options.max_results,
    channelId=YOUTUVE_CHANNEL_ID
  ).execute()

  videos = []
  channels = []
  playlists = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videoList = {}
      videoList[search_result["id"]["videoId"]] = youtube.videos().list(
        part="statistics",
        id=search_result["id"]["videoId"]
      ).execute().get("items", [])[0].get("statistics",[])["viewCount"]
      print(videoList)
      videos.append("%s (%s)" % (search_result["snippet"]["title"],
                                 search_result["id"]["videoId"]))
    elif search_result["id"]["kind"] == "youtube#channel":
      channels.append("%s (%s)" % (search_result["snippet"]["title"],
                                   search_result["id"]["channelId"]))
    elif search_result["id"]["kind"] == "youtube#playlist": 
      playlists.append("%s (%s)" % (search_result["snippet"]["title"],
                                    search_result["id"]["playlistId"]))

  print("Videos:\n", "\n".join(videos), "\n")
  print("Channels:\n", "\n".join(channels), "\n")
  print("Playlists:\n", "\n".join(playlists), "\n")


if __name__ == "__main__":
  # 検索ワード
  argparser.add_argument("--q", help="Search term", default="ベートーベン")
  # 検索上限
  argparser.add_argument("--max-results", help="Max results", default=10)
  args = argparser.parse_args()

  try:
    youtube_search(args)
  except HttpError as e:
    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))


wb = Workbook()
wb.save('sample.xlsx')
