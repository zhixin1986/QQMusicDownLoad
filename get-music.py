#!/usr/bin/python3
import urllib.request
import json,os,sys,getopt
def callbackfunc(blocknum, blocksize, totalsize):
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
           percent = 100
        downsize=blocknum * blocksize
        if downsize >= totalsize:
            downsize=totalsize
        s ="%.2f%%"%(percent)+"====>"+"%.2f"%(downsize/1024/1024)+"M/"+"%.2f"%(totalsize/1024/1024)+"M \r"
        sys.stdout.write(s)
        sys.stdout.flush()
class QQMusicDownLoad:
    def __init__(self,savedir,maxNum):
         self.downLoadUrl="http://streamoc.music.tc.qq.com/F000{0}.flac?vkey=F8DDEBC3CA3CDC1290A0042C18CC44AE9F495BEAD7B53157016DEEC274F52499244F437888F38B85B058E707317EC9A70984B5888AA71590&guid=joe&uin=1524&fromtag=8"
         self.saveDir=savedir
         self.curnum =0
         self.totalnum =0
         self.maxNum = maxNum
         self.downLoadNum=0
         self.failLoadNum=0
         self.fileExitsNum=0
    def downLoadMusic(self,url,fileName):
         print("正在下载 >>>%s"%fileName)
         localPath = os.path.join(self.saveDir,fileName)
         if os.path.exists(localPath)==False:
            try:
               urllib.request.urlretrieve(url,localPath,callbackfunc)
               self.downLoadNum=self.downLoadNum+1
            except:
               self.failLoadNum=self.failLoadNum+1
               print ('%s 下载失败' % fileName)
               if os.path.exists(localPath):
                  os.remove(localPath)
         else:
            self.fileExitsNum=self.fileExitsNum+1
    def getUrlJson(self,url,headers=None):
        req = urllib.request.Request(url,None, headers)
        resp=urllib.request.urlopen(req)
        html=resp.read()
        html=html.decode('utf-8')
        return html
    def searchMusicByKey(self,keyword,curpage):
        url ="https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.center&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p={0}&n=40&w={1}&&jsonpCallback=searchCallbacksong2020&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0"
        url =url.format(curpage,urllib.parse.quote(keyword))
        html=self.getUrlJson(url)[9:-1]
        musicSong=json.loads(html)["data"]["song"]
        if curpage ==1:
           self.totalnum=musicSong["totalnum"]
        self.curnum =self.curnum+musicSong["curnum"]
        self.curpage =musicSong["curpage"]
        musicList =musicSong["list"]
        print("共搜索到%d首音乐，当前页数%d,当前返回%d首"%(self.totalnum,self.curpage,self.curnum))
        for song in musicList:
            if self.downLoadNum<self.maxNum or self.maxNum<0:
               fileName =song["singer"][0]["name"]+"-"+song["title"]
               self.downLoadMusic(self.downLoadUrl.format(song["file"]["media_mid"]),fileName+".flac")
            else:
               break
    def downLoadMusicByKey(self,keyword):
            curpage =1
            self.searchMusicByKey(keyword,1)
            while self.curnum<self.totalnum:
              curpage=curpage+1
              self.searchMusicByKey(keyword,curpage)
    def downLoadMusicByPlayList(self,playlist):
       url='https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&json=1&utf8=1&onlysong=0&disstid={0}&format=jsonp&g_tk=1547190586&jsonpCallback=playlistinfoCallback&loginUin=2020197426&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'.format(playlist)
       header={}
       header['user-agent']='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
       header['referer']='https://y.qq.com/n/yqq/playlist/{0}.html'.format(playlist)
       html=self.getUrlJson(url,header)
       html=html[len("playlistinfoCallback("):-1]
       info=json.loads(html)
       songinfo=info['cdlist'][0]
       self.totalnum=songinfo["total_song_num"]
       self.curnum =songinfo["cur_song_num"]
       self.curpage =1
       print("共搜索到%d首音乐，当前页数%d,当前返回%d首"%(self.totalnum,self.curpage,self.curnum))
       songinfo=songinfo['songlist']
       for song in songinfo:
         if self.downLoadNum<self.maxNum or self.maxNum<0:
             fileName=song['singer'][0]['name']+'-'+song['songname']
             self.downLoadMusic(self.downLoadUrl.format(song["songmid"]),fileName+".flac")
         else:
            break

keyword =""
playlist=""
saveDir=os.path.dirname(__file__)
downNum=-1
try:
   opts, args = getopt.getopt(sys.argv[1:],"hk:o:n:l:",["keyword=","output=","maxNum=","playlist="])
except getopt.GetoptError:
   print ('get-music.py -k <keyword> -n <maxNum> -o <output> -l <playlist>')
   sys.exit(2)
for opt, arg in opts:
   if opt == '-h':
      print ('get-music.py -k <keyword> -n <maxNum> -o <output>')
      sys.exit()
   elif opt in ("-k", "--keyword"):
      keyword = arg
      print("keyword=%s"%(keyword))
   elif opt in ("-o", "--output"):
      saveDir = arg
      print("saveDir=%s"%(saveDir))
   elif opt in ("-n","--maxNum"):
      downNum =int(arg)
   elif opt in ("-l","--playlist"):
      playlist =arg
if len(keyword)==0 and len(playlist)==0:
   keyword =input("请输入要搜索的歌曲关键字\r\n")
musicDownLoad =QQMusicDownLoad(saveDir,downNum)
if len(keyword)>0:
   musicDownLoad.downLoadMusicByKey(keyword)
elif len(playlist)>0:
   musicDownLoad.downLoadMusicByPlayList(playlist)
print("成功下载%d首歌曲,失败%d首歌曲,忽略%d首歌曲"%(musicDownLoad.downLoadNum,musicDownLoad.failLoadNum,musicDownLoad.fileExitsNum))
