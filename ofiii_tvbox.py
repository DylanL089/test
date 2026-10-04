# -*- coding: utf-8 -*-
"""
ofiii_tvbox.py — 專供 TVBox 使用的 ofiii 台灣直播爬蟲
"""
import sys
import os
import time
import json
import random
import re
import urllib.request
import urllib.parse
from urllib.parse import urlparse, urljoin

try:
    from base.spider import Spider as BaseSpider
except ImportError:
    class BaseSpider:
        def getProxyUrl(self):
            return "http://127.0.0.1:9978/proxy?do=py&"
        def init(self, extend): pass
        def getName(self): return "Ofiii"
        def liveContent(self, url): return ""
        def localProxy(self, params): return []
        def destroy(self): return ""

# 頻道資料庫：頻道ID: (頻道名稱, 台標, 分組)
CHANNELS = {
    '4gtv-4gtv009': ('中天新聞台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/CTI2.png', '新聞財經'),
    '4gtv-4gtv040': ('中視', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/CTV.png', '綜合其他'),
    '4gtv-4gtv041': ('華視', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/CTS.png', '綜合其他'),
    '4gtv-4gtv052': ('華視新聞', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/CTS1.png', '新聞財經'),
    '4gtv-4gtv074': ('中視新聞', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/CTV1.png', '新聞財經'),
    '4gtv-4gtv076': ('亞洲旅遊台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/Asiatravel.png', '生活旅遊'),
    '4gtv-4gtv084': ('國會頻道1台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/guohui1.png', '綜合其他'),
    '4gtv-4gtv085': ('國會頻道2台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/guohui2.png', '綜合其他'),
    '4gtv-4gtv102': ('東森購物1台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/EBC11.png', '綜合其他'),
    '4gtv-4gtv103': ('東森購物2台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/EBC11.png', '綜合其他'),
    '4gtv-4gtv104': ('第1商業台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv104_tv.png', '新聞財經'),
    '4gtv-4gtv156': ('寰宇新聞台灣台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/Global3.png', '新聞財經'),
    '4gtv-4gtv158': ('寰宇財經台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/Global4.png', '新聞財經'),
    'litv-xinchuang01': ('龍華卡通台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV9.png', '兒童卡通'),
    'litv-xinchuang02': ('龍華洋片台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV2.png', '電影戲劇'),
    'litv-xinchuang03': ('龍華電影台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV1.png', '電影戲劇'),
    'litv-xinchuang11': ('龍華日韓台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV5.png', '電影戲劇'),
    'litv-longturn14': ('寰宇新聞台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/Global2.png', '新聞財經'),
    'litv-xinchuang12': ('龍華偶像台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV6.png', '電影戲劇'),
    'litv-xinchuang18': ('龍華戲劇台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV4.png', '電影戲劇'),
    'litv-xinchuang19': ('SMART知識台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/smarttv.png', '生活旅遊'),
    'litv-xinchuang20': ('ELTV生活英語台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/ELTA7.png', '兒童卡通'),
    'litv-xinchuang21': ('龍華經典台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV7.png', '電影戲劇'),
    'litv-xinchuang22': ('台灣戲劇台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/Taiwanxiju.png', '電影戲劇'),
    'litv-ftv16': ('好消息', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/GoodTV1.png', '綜合其他'),
    'litv-ftv17': ('好消息2台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/GoodTV2.png', '綜合其他'),
    'iNEWS': ('三立新聞iNEWS', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/SET3.png', '新聞財經'),
}

BASE_API_URL = 'https://cdi.ofiii.com/ofiii_cdi/video/urls'
BROWSER_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'origin': 'https://www.ofiii.com',
    'referer': 'https://www.ofiii.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

class Spider(BaseSpider):
    def getName(self):
        return "Ofiii台灣直播"

    def init(self, extend):
        pass

    def _fetch_url(self, url, headers=None):
        try:
            req = urllib.request.Request(url, headers=headers or BROWSER_HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read()
        except Exception:
            return None

    def _generate_device_id(self):
        return '%04x%04x-%04x-%04x-%04x-%04x%04x%04x' % (
            random.randint(0, 0xffff), random.randint(0, 0xffff),
            random.randint(0, 0xffff),
            random.randint(0, 0x0fff) | 0x4000,
            random.randint(0, 0x3fff) | 0x8000,
            random.randint(0, 0xffff), random.randint(0, 0xffff), random.randint(0, 0xffff),
        )

    def liveContent(self, url):
        """產生 TVBox 的直播清單"""
        lines = ['#EXTM3U']
        base_proxy = self.getProxyUrl()
        if not base_proxy.endswith(('?', '&')):
            base_proxy += '&'

        for cid, (name, logo, group) in CHANNELS.items():
            lines.append(f'#EXTINF:-1 tvg-id="{name}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}')
            # 將請求導引至 TVBox 本地代理
            lines.append(f'{base_proxy}do=py&fun=ofiii&id={cid}')

        return '\n'.join(lines)

    def localProxy(self, params):
        """處理播放代理請求"""
        fun = params.get('fun')
        if fun == 'ofiii':
            channel_id = params.get('id')
            if not channel_id or channel_id not in CHANNELS:
                return [404, "text/plain", "Channel not found"]

            device_id = self._generate_device_id()
            timestamp = int(time.time())
            puid = self._generate_device_id()

            api_url = (f'{BASE_API_URL}?device_type=pc&device_id={device_id}'
                       f'&media_type=channel&asset_id={channel_id}&_t={timestamp}'
                       f'&project_num=OFWEB00&puid={puid}')

            content = self._fetch_url(api_url)
            if not content:
                return [500, "text/plain", "Fetch API failed"]

            try:
                data = json.loads(content.decode('utf-8'))
                asset_urls = data.get('asset_urls', [])
                if not asset_urls:
                    return [404, "text/plain", "No stream URL found"]

                master_m3u8_url = asset_urls[0]
                master_content = self._fetch_url(master_m3u8_url)
                if not master_content:
                    return [500, "text/plain", "Fetch master m3u8 failed"]

                master_text = master_content.decode('utf-8', errors='replace')
                matches = re.findall(r'#EXT-X-STREAM-INF:.*?BANDWIDTH=(\d+).*?\n(.+?\.m3u8)', master_text, re.S)
                
                if matches:
                    matches.sort(key=lambda x: int(x[0]), reverse=True)
                    playlist_rel = matches[0][1].strip()
                    playlist_url = urljoin(master_m3u8_url, playlist_rel)
                else:
                    playlist_url = master_m3u8_url

                # 抓取真實子分片 m3u8
                sub_content = self._fetch_url(playlist_url)
                if not sub_content:
                    return [500, "text/plain", "Fetch sub playlist failed"]

                sub_text = sub_content.decode('utf-8', errors='replace')
                # 將相對路徑補全為絕對 URL
                base_dir = playlist_url[:playlist_url.rfind('/') + 1]
                fixed_lines = []
                for line in sub_text.splitlines():
                    line_s = line.strip()
                    if line_s and not line_s.startswith('#') and '.ts' in line_s:
                        fixed_lines.append(urljoin(base_dir, line_s))
                    else:
                        fixed_lines.append(line)

                return [200, "application/vnd.apple.mpegurl", '\n'.join(fixed_lines)]

            except Exception as e:
                return [500, "text/plain", f"Internal Error: {str(e)}"]

        return [400, "text/plain", "Bad Request"]

    def destroy(self):
        pass