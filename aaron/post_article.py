# -*- coding:utf-8 -*-
from netcall import fetch_html
from hashutil import hash_str
from timeutil import str_to_mcroseconds
import json
from mongoutil import MongoUtil
from config import MONGO_INFO, MEDIAS
from strutil import ensure_utf8
import time
import urllib

class ArticlePoster(object):

    def __init__(self):
        self.mongo_cli = MongoUtil(MONGO_INFO['host'],
                                   MONGO_INFO['db'],
                                   MONGO_INFO['collection'])
        self.post_api = 'http://10.111.0.154:9100/post/import'
        self.transform_video_api = 'http://10.111.0.154:10100/video/add?uid=12299265&video_id=%s&media_id=%s&pic_url=%s'

    def __load_items(self, query):
        q = {
            't_p' : {'$exists' : False}
        }
        q.update(query)
        for item in self.mongo_cli.find_all(q, 10):
            yield item

    def get_blind_url(self, video_id, media_id, poster_url):
        resp = fetch_html(self.transform_video_api % (video_id, media_id, urllib.quote(poster_url)))
        try:
            data = json.loads(resp)
        except Exception:
            return
        result = data.get('result')
        return result.get('url'), result.get('cover_pic')

    def post_article(self, media_name, media_id, query):
        for item in self.__load_items(query):
            video_id = item.get('ks3_key')
            poster_url = item.get('poster')

            # get compressed video stream url and poster url
            video_url, poster_url = self.get_blind_url(video_id, media_id, poster_url)

            # format article content
            desc = ensure_utf8(item.get('content'))
            content = self.gen_content(video_url, poster_url, desc)

            self.publish_article(
                item.get('web_url'),
                media_name,
                media_id,
                ensure_utf8(item.get('title')),
                content,
                video_id
            )
            item['t_p'] = int(time.time())
            self.mongo_cli.save(item)
            print 'name: %s, title : %s' % (ensure_utf8(media_name), ensure_utf8(item.get('title')))


    def gen_content(self, video_url, poster_url, desc):
        src = '''
            javascript:void(function(a) {{
                document.open(undefined);
                if((typeof android !== 'undefined') && navigator.userAgent.toLowerCase(undefined).indexOf('android') > -1) {{
                    document.write('<div style=\\'width:100%;height:100%;background-image:url({poster_url});background-size:100%;text-align:center;\\' onclick=\\'window.top.android.playVideo(this.dataset.vid)\\' data-vid=\\'{video_url}\\'
                    >
                        <img style=\\'width:100px;position:relative;top:50%;margin-top:-50px;\\' src=\\'http://staticimg.yidianzixun.com/s/wemedia/201511/AroEyewGT.png \\' /> </div>');
                    return;
                }}
                document.write('<video src=\\'{video_url}\\' style=\\'width:100%;height:100%;\\' poster=\\'{poster_url}\\' controls preload=\\'none\\'></video>');
                document.close(undefined);
            }}(1))
        '''.format(video_url=video_url, poster_url=poster_url)

        return '''
            <iframe id="yidian_frame_d2c5f9f70" width="100%" height="380px" frameborder="0" onload="this.style.height=(this.clientWidth||window.innerWidth)/16*9+'px';this.style.display='block'"
                style="display:block;"
                scrolling="no"
                src="{video_src}">
            </iframe>
            <p>{desc}<p>
        '''.format(video_src=src, desc=desc)

    def publish_article(self, url, media_name, media_id, title, content, video_id):
        data = {
            'media_name' : media_name,
            'media_id' : media_id,
            'title' : title,
            'content' : content,
            'import_hash' : hash_str(url),
            'date' : str_to_mcroseconds('2015-10-21 18:50:00'),
            'import_url' : url,
            'passed' : '1',
            'video_id' : video_id

        }
        headers = {
            'Content-Type' : 'application/json'
        }
        resp = fetch_html(self.post_api, headers=headers, body=json.dumps(data))
        print resp

def main():
    #media_name = '创意新发现'
    #media_id = '59185'

    article_poster = ArticlePoster()
    for media in MEDIAS:
        article_poster.post_article(media.get('name'), media.get('media_id'), media.get('query'))

if __name__ == '__main__':
    main()
