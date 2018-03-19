from urllib.parse import urlencode
from urllib.request import urlopen
import time
import json
import codecs
import operator

reader = codecs.getreader("utf-8")

token = ''

#Delete files older than this:
days = 0
#types = 'images,videos,pdfs,gdocs,zips,files'
types = 'all'
ts_to = int(time.time()) - days * 24 * 60 * 60

def list_files():
  files = []
  page = 1
  while True:
    params = {
      'token': token,
      'ts_to': ts_to,
      'count': 1000,
      'page': page,
      'types': types
    }
    uri = 'https://slack.com/api/files.list'
    response = json.load(reader(urlopen(uri + '?' + urlencode(params))))
    for f in response["files"]:
      files.append(f)
    if response["paging"]["pages"] > response["paging"]["page"]:
      page += 1
    else:
      break
  return files

def print_file_info(files):
  output = []
  for f in files:
    print("%7s" % ("%.2f" % (f['size']/(8*1024))), "KB ", f['user'], "\t", f['title'])

def print_user_info(files):
  users = {}
  output = []
  output.append('Here are the files I found older than {} days.\nIncluded file types: {}\nThese files have not yet been deleted.\n'.format(days, types))
  output.append("\n")
  for f in files:
    userkey = f['user']
    if userkey not in users:
      users[userkey] = {'count':0, 'size':0}
    users[userkey]['count'] += 1 
    users[userkey]['size'] += f['size']
    #print("%7s" % ("%.2f" % (f['size']/(8*1024))), "KB ", userkey, "\t", f['title'])
  for userId in sorted(users, key=lambda x: users[x]['size'], reverse=True):
    output.append('{0:7.2f} MB    {1:4d} files    {2}\n'.format(get_filesize(users[userId]['size']), users[userId]['count'], get_username(userId)))
  output.append("\n")
  return output

def print_totals(files):
  totalSize = sum(f['size'] for f in files)
  return 'Total: {0} files, {1:.2f} GB'.format(len(files), get_filesize(totalSize)/1024)

# convert a file size in bytes to a size in MB
def get_filesize(rawSize):
  return rawSize/(1024*1024)

def get_username(userId):
  params = {
    'token': token,
    'user': userId,
  }
  uri = 'https://slack.com/api/users.info'
  response = reader(urlopen(uri + '?' + urlencode(params)))
  return json.load(response)['user']['name']

def post_fileinfo(output):
  params = {
    'token': token,
    'channel': 'C2C4LHBDF',
    'text': output,
    'mrkdwn': 'true',
    'icon_emoji': ':kleen:',
    'as_user': 'false',
    'username': 'Trashy the Cleanup Bot'
  }
  uri = 'https://slack.com/api/chat.postMessage?' + urlencode(params)
  print(uri)
  response = reader(urlopen(uri ))
  return json.load(response)['ok']

files = list_files()
output = print_user_info(files)
output.append(print_totals(files))
print(''.join(output))
#post_fileinfo('```{}```'.format(''.join(output)))
