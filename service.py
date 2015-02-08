# -*- coding: utf-8 -*-
import os
import shutil
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs
import uuid
import string
import urllib
import urllib2
import socket
import re

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")
__temp__       = xbmc.translatePath( os.path.join( __profile__, 'temp') ).decode("utf-8")

sys.path.append (__resource__)

from pn_utilities import OSDBServer, log, hashFile, normalizeString, languageTranslate

self_host = "http://www.addic7ed.com"
self_pattern = re.compile(">Version(.*?),.*?class=\"buttonDownload\".*?\"(.*?)\".*?class=\"language\">(.*?)<", re.S)
self_release_filename_pattern = re.compile(".*\-(.*)\.")
self_pattern_version = re.compile("<table class=\"tabel95\">.*?>Version(.*?),(.*?)</table>", re.S)
self_pattern_langs = re.compile("class=\"language\">(.*?)<.*?<b>Completed.*?class=\"buttonDownload\" href=\"(.*?)\"", re.S)


if xbmcvfs.exists(__temp__):
  shutil.rmtree(__temp__)
xbmcvfs.mkdirs(__temp__)

def Search( item ):
 if item['tvshow'] == "":
  return
 name = item['tvshow'].lower().replace(" ", "_").replace("$#*!","shit").replace("'","")
 searchurl = "%s/serie/%s/%s/%s/addic7ed" %(self_host, name, item['season'], item['episode'])
 socket.setdefaulttimeout(5)
 page = urllib2.urlopen(searchurl)
 content = page.read()
 for version in self_pattern_version.finditer(content):
  subteams = version.groups()[0]
  
  for sub in self_pattern_langs.finditer(str(version.groups()[1])):
   file_name = self_release_filename_pattern.match(str(os.path.basename(item['file_original_path']))).groups()[0].lower()
   subUrl = sub.groups()[1]
   fullLanguage = sub.groups()[0]
   if (str(subteams).find(str(file_name))) > -1:
    hashed = True
   else:
    hashed = False
    try:
     lang = languageTranslate(fullLanguage, 0, 2)
    except:
     lang = ""
    link = "%s%s"%(self_host,subUrl)
    filename = "%s.S%.2dE%.2d-%s" %(name.replace("_", ".").title(), int(item['season']), int(item['episode']),subteams )
    if lang in item['3let_language']:
     listitem = xbmcgui.ListItem(label=fullLanguage, label2=filename, iconImage="0", thumbnailImage=lang)
     listitem.setProperty( "sync", ("false", "true")[hashed] )
     listitem.setProperty( "hearing_imp", "false" )
     url = "plugin://%s/?action=download&link=%s&filename=%s" % (__scriptid__,link,filename)
     xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)
	
def get_params(string=""):
  param=[]
  if string == "":
    paramstring=sys.argv[2]
  else:
    paramstring=string 
  if len(paramstring)>=2:
    params=paramstring
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]
                                
  return param

def get_url(url):
 req_headers = {
  'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/525.13',
  'Referer': 'http://www.addic7ed.com'}
 request = urllib2.Request(url, headers=req_headers)
 opener = urllib2.build_opener()
 response = opener.open(request)
 contents = response.read() 
 return contents 
  
params = get_params()

if params['action'] == 'search':
 item = {}
 item['temp']               = False
 item['rar']                = False
 item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                         # Year
 item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                  # Season
 item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                 # Episode
 item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))  # Show
 item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))# try to get original title
 item['file_original_path'] = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))# Full path of a playing file
 item['3let_language']      = [] #['scc','eng']
  
 for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
  item['3let_language'].append(languageTranslate(lang,0,2))
  
 if item['title'] == "":
  item['title']  = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title
    
 if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
  item['season'] = "0"                                                          #
  item['episode'] = item['episode'][-1:]
  
 Search(item)
elif params['action'] == 'download':
 contents = get_url(params['link'])   
 dest = os.path.join(__temp__, "%s.%s" %(str(uuid.uuid4()), "srt"))
 
 f = open(dest, 'wb')
 f.write(contents)
 f.close()
 
 listitem = xbmcgui.ListItem(label=dest)
 xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=dest,listitem=listitem,isFolder=False)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
