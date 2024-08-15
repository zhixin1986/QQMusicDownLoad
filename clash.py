import yaml
import base64
import sys, getopt
import requests
import os
from datetime import datetime

def decode_base64(base64_string):
    length = len(base64_string) % 4 
    for i in range(length):
        base64_string += '='
    decoded_string = base64.b64decode(base64_string)
    return decoded_string

def findVless(proxies,delList):
    for prox in proxies:
        if 'type' in prox and prox['type'] == 'vless':
            delList.append(prox)

def delVelss(proxies,proxy_groups):
    delList = []
    findVless(proxies,delList)
    for prox in delList:
        proxies.remove(prox)
        name = prox['name']
        for group in proxy_groups:
            proxies_list = group['proxies']  
            if name in  proxies_list:
                proxies_list.remove(name)

def inProxies(name, proxies):
    if name == 'DIRECT' :
       return True
    if name == 'REJECT' :
       return True
    for prox in proxies:
        if prox['name'] == name:
            return True
    return False

def convertss(proxies):
    for prox in proxies:
        if 'cipher' in prox and prox['cipher'] == 'ss':
           base64Str = prox['password'][2:]
           base64Str = decode_base64(base64Str).decode('utf-8')
           strlist= base64Str.split(':')
           prox['cipher'] = strlist[0]
           prox['password'] = strlist[1]

def delinvalid(proxies,proxy_groups):
    for group in proxy_groups:
        groups_proxies = group['proxies']
        delList = []
        for prox in groups_proxies:
            if not inProxies(prox,proxies) and not inProxies(prox,proxy_groups):
               delList.append(prox)
        for prox in delList:
            print('删除无效节点:'+prox)
            groups_proxies.remove(prox)

def downlaod(url, file_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0"
    }
    r = requests.get(url=url, headers=headers)
    with open(file_path, "wb") as f:
        f.write(r.content)
        f.flush()

def main(argv):
    try:
       opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
      print ('clash.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
    inputfile  =''
    outputfile =''
    for opt, arg in opts:
      if opt == '-h':
         print ('clash.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
    now = datetime.now()
    delInputfile = False
    if len(inputfile) ==0:
        delInputfile = True
        inputfile = '%Y%m%d-clash.yaml'
        inputfile = now.strftime(inputfile)
        url = 'http://stair.api-node.shop/node/'
        url = url + inputfile
        inputfile = inputfile +".tmp"
        downlaod(url,inputfile)
        print(url+inputfile)
    if len(outputfile) ==0:
        outputfile = 'clash_last.yaml'
    print ('输入的文件为：', inputfile)
    print ('输出的文件为：', outputfile)
    with open(inputfile, 'r',encoding='utf-8') as file:
       config = yaml.safe_load(file)
       proxies = config['proxies']
       proxy_groups = config['proxy-groups']
       convertss(proxies)
       delVelss(proxies,proxy_groups)
       delinvalid(proxies,proxy_groups)
       with open(outputfile, 'w',encoding='utf-8') as file:
           yaml.dump(config, file, default_flow_style=False,allow_unicode=True,indent=2)
       if delInputfile:
           os.remove(inputfile)

if __name__ == "__main__":
   main(sys.argv[1:])







