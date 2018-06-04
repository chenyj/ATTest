# -*-coding:utf8-*-
import httplib2


def getAttachCenter():
    http = httplib2.Http()
    host = 'http://www.ipip.net/'
    response,content = http.request(host, 'GET')
    #print(content.decode('utf-8').split('","')[2])
    print(content.decode('utf-8'))

def main():
    getAttachCenter()

if __name__ == '__main__':
    main()