import os
import re
import sys
import json
import time
import random
import logging
import requests
import configparser
from urllib import parse

# 把翻墙软件的"系统代理模式"改为"全局模式"


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(filename)s[line:%(lineno)d] %(message)s', datefmt='%a %d/%m/%Y %H:%M:%S', filename='myapp.log', filemode='w')



# 当前所在目录
g_currentPath = os.path.abspath('.')



class CVideo:
    m_fileName1 = '.1.format'
    m_fileName2 = '.2.decrypted'
    m_fileName3 = '.3.url_encoded_fmt_stream_map'

    m_baseUrl = 'http://www.youtube.com/get_video_info?video_id='

    # 解码次数
    m_decodeTimes = 3

    m_headers = {
        #'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #'accept-encoding':'gzip, deflate, br',
        #'accept-language':'zh-CN,zh;q=0.8',
        #'x-chrome-uma-enabled':'1',
        'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36',
    }

    def __init__(self, videoId):
        self.m_videoId = videoId
        self.m_videoUrl = CVideo.m_baseUrl + videoId


    def Print(self):
        print(self.m_videoId)


    def Process(self):
        # 下载短视频详情文件
        self.DownloadVideoFile()

        # 将得到的get_video_info文件格式化
        self.Format()

        # 解码3次
        self.Decode()

        # 提取关键字段信息
        self.GetKeyInfo()


    def DownloadVideoFile(self):
        self.GetPageInfo()
        self.SaveContentToFile(self.m_videoId)


    def GetPageInfo(self):
        #time.sleep(random.randint(1, 3))
        r = requests.get(self.m_videoUrl, headers = CVideo.m_headers, timeout=5)
        if r.status_code != 200:
            exit(1)
        if not r.text:
            exit(2)
        self.m_content = r.text


    def Format(self):
        self.m_content = '[' + self.m_videoId + ']&' + self.m_content
        self.m_content = self.m_content.replace('&', '\n\n')
        fileName = self.m_videoId + CVideo.m_fileName1
        self.SaveContentToFile(fileName)


    def Decode(self):
        for i in range(1, CVideo.m_decodeTimes + 1):
            self.m_content = parse.unquote(self.m_content)
        fileName = self.m_videoId + CVideo.m_fileName2
        self.SaveContentToFile(fileName)


    def GetKeyInfo(self):
        conf = configparser.ConfigParser()
        conf.read_string(self.m_content)
        sectionNmae = self.m_videoId
        result = {}
        result['viewCount'] = conf.get(sectionNmae, 'view_count')
        result['title'] = conf.get(sectionNmae, 'title').replace('+', ' ')
        result['aboutVideo'] = conf.get(sectionNmae, 'keywords').replace('+', ' ')
        result['thumbnailUrl'] = conf.get(sectionNmae, 'thumbnail_url')
        result['author'] = conf.get(sectionNmae, 'author').replace('+', ' ')
        result['videoInfo'] = self.GetUrlEncodedFmtStreamMap(conf.get(sectionNmae, 'url_encoded_fmt_stream_map'))


    def GetUrlEncodedFmtStreamMap(self, content = None):
        if not content:
            return

        if content[0:4] != 'url=':
            print("url_encoded_fmt_stream_map need transform")
            prefix = re.match('(.*?)&url=', content).group(1)
            content = content[(len(prefix)+1):len(content)] + '&' + prefix

        fileName = self.m_videoId + CVideo.m_fileName3
        self.SaveContentToFile(fileName, content = 'url_encoded_fmt_stream_map=' + content)
        contentFormat = content[4:len(content)].replace('&url=', '\r\n').replace('?', '\n').replace('&', '\n')
        self.SaveContentToFile(fileName, 'a', content = '\r\n' + contentFormat)
        return self.GetVideoInfo(content)


    def GetVideoInfo(self, content = None):
        videoList = content[4:len(content)].split('&url=')
        self.SaveContentToFile('5', content = str(videoList))
        videoListNew = []

        for videoUrl in videoList:
            tmp = {}
            tmp['url'] = videoUrl.replace('url=', '')

            mime = re.match(r'.*&mime=(.*?)&.*', videoUrl)
            if not mime:
                mime = re.match(r'.*&mime=(.*)', videoUrl)
            tmp['mime'] = mime.group(1)

            quality = re.match(r'.*&quality=(.*?)&.*', videoUrl)
            if not quality:
                quality = re.match(r'.*&quality=(.*)', videoUrl)
            tmp['quality'] = quality.group(1)

            videoListNew.append(tmp)
        self.SaveContentToFile('6', content = str(videoListNew))
        return videoListNew


    def SaveContentToFile(self, fileName = None, accessMode = 'w', content = None):
        if not fileName:
            return

        global g_currentPath
        filePath = g_currentPath + '/' + fileName
        f = open(filePath, accessMode, encoding='utf-8')

        if content:
            f.write(content)
        else:
            f.write(self.m_content)
        f.close()
        return filePath


def Encode():
    v_1 = {'wt':'haha婚纱摄影haha'}
    v_2 = parse.urlencode(v_1)
    print(str(v_1) + "\n")
    print(str(v_2))


    SaveContentToFile(json.dumps(result), videoId + g_FileName3)
    return json.dumps(result)


if __name__ == "__main__":
    videoId = '6-M3QUaGJ7o'

    if len(sys.argv) > 1:
        videoId = sys.argv[1]

    handle = CVideo(videoId)
    handle.Process()







