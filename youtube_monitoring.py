# -*- coding: utf-8 -*-
"""
Created on Sun 2019/04/04
@author: Yusuke Nakamoto
"""

#!/usr/bin/python

import sys
import os
import configparser
import csv
import datetime
import re

from oauth2client.tools import argparser
from apiclient.discovery import build
from apiclient.errors import HttpError

inifile = configparser.ConfigParser()
inifile.read('./config.ini', 'UTF-8')

#APIキー
DEVELOPER_KEY = inifile.get('DEVELOPER_KEY', 'key')
#APIサービス名aa
YOUTUBE_API_SERVICE_NAME = inifile.get('YOUTUBE_API_SERVICE_NAME', 'service')
#APIバージョン
YOUTUBE_API_VERSION = inifile.get('YOUTUBE_API_VERSION', 'version')
#モニタリング対象channelId
YOUTUVE_CHANNEL_ID = inifile.get('YOUTUVE_CHANNEL_ID', 'channelId')
#取得動画の最大数
MAX_VIDEOS_COUNT = inifile.get('MAX_VIDEOS_COUNT','maxVideo')
#動画一覧取得順（APIパラメータ）
ORDER_PARAM = inifile.get('ORDER_PARAM','order')
#出力ファイル（csv形式）
OUTPUT_FILE_PATH = inifile.get("OUTPUT_FILE_PATH","output")

YOUTUBE = build(YOUTUBE_API_SERVICE_NAME,
                  YOUTUBE_API_VERSION,
                  developerKey=DEVELOPER_KEY)
#実施日付
now = datetime.datetime.now()

#モニタリングメイン処理
def exceute(channelId):
  # 検索上限
  # チャンネルのIDを取得
  search_responseList = []
  try:
   search_responseList = youtube_search(channelId)
  except HttpError as e:
    print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

  # 対象動画詳細一覧
  for search_response in search_responseList:
    for search_result in search_response.get("items", []):
      if search_result["id"]["kind"] == "youtube#video":
        vodeo_result = ""
        try:
          vodeo_result = youtube_video(search_result)
        except HttpError as e:
          print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            
        # 動画詳細リスト作成
        for videorep in vodeo_result.get("items", []):
          videodetail = {}
          videodetail["日付"] = now.strftime("%Y/%m/%d")
          videodetail["チャンネル"] = videorep["snippet"]["channelTitle"]
          videotitle = videorep["snippet"]["title"]
          videodetail["動画名"] = videotitle.replace('\u3099','\u309B').replace('\u309A','\u309C')
          videodetail["URL"] = "https://www.youtube.com/watch?v=" + videorep["id"]
          videodetail["再生数(累計)"] = videorep["statistics"]["viewCount"] 
          #アップロード日時が今日の場合スキップ
          prelist = 0
          uplaodeDate = videorep["snippet"]["publishedAt"] 
          uplaodeDate = uplaodeDate[0:10].replace("-","/")
          if not now.strftime("%Y/%m/%d") == uplaodeDate:
            prelist = get_date_view(videodetail)
          videodetail["再生数(当日)"] = prelist
          write_csv(videodetail)
                                

# 動画一覧検索API
# 対象チャンネルの動画一覧を取得
def youtube_search(agschannelId):
  pagecount = 0
  nextpageToken = ""
  maxparam = int(MAX_VIDEOS_COUNT)
  retList = []
  while True:
    #retListの中身があればパラメータ取得
    respons = ""
    respons = YOUTUBE.search().list(
      part="id,snippet",
      maxResults= 50 if 50 <= maxparam else maxparam,
      channelId=agschannelId,
      order=ORDER_PARAM,
      pageToken=nextpageToken
    ).execute()
    retList.append(respons)
    #次のページがなければ終了
    if not "nextPageToken" in respons:
      break
    nextpageToken = respons["nextPageToken"]
    pagecount += int(respons["pageInfo"]["resultsPerPage"])
    maxparam -= 50
    if 0 >= maxparam:
      break
  return retList

# 動画API
# 対象動画の情報を取得
def youtube_video(search_result):
  return YOUTUBE.videos().list(
    part="statistics,snippet",
    id=search_result["id"]["videoId"],
    fields="items(id,snippet(channelTitle,title,publishedAt),statistics(viewCount))"
  ).execute()

# 追記書き
def write_csv(videoDetail):
  with open(OUTPUT_FILE_PATH, 'a',  encoding='shift_jis') as f:
    writer = csv.DictWriter(f, ["日付","チャンネル","動画名","URL","再生数(累計)","再生数(当日)"],lineterminator='\n')
    writer.writerow(videoDetail)

# 当日の再生を取得する
def get_date_view(videodetail):
  viewcount = 0
  with open(OUTPUT_FILE_PATH, encoding='shift_jis') as f:
      reader = csv.reader(f)
      for retlist in reversed(list(reader)):
        if retlist[3] == videodetail["URL"]:
          viewcount = int(retlist[4]) 
          break
  if 0 < viewcount:
    return int(videodetail["再生数(累計)"]) - viewcount
  return 0


if __name__ == "__main__":
  # ファイルが存在しない場合新規で作成
  if not os.path.exists(OUTPUT_FILE_PATH):
    with open(OUTPUT_FILE_PATH, 'w', encoding='shift_jis') as csv_file:
      writer = csv.DictWriter(csv_file, ["日付","チャンネル","動画名","URL","再生数(累計)","再生数(当日)"],lineterminator='\n')
      writer.writeheader()

  channelList = str(YOUTUVE_CHANNEL_ID).split(',')
  for channelId in channelList:
    exceute(channelId)

  
  






      
        






    
