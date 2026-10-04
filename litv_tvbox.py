# -*- coding: utf-8 -*-
"""
litv_tvbox.py — TVBox 專用 LiTV 台灣完整 94 頻道直播爬蟲
"""
import sys
import os
import time
import json
import random
import re
import urllib.request
import urllib.parse
from urllib.parse import urljoin

try:
    from base.spider import Spider as BaseSpider
except ImportError:
    class BaseSpider:
        def getProxyUrl(self):
            return "http://127.0.0.1:9978/proxy?do=py&"
        def init(self, extend): pass
        def getName(self): return "LiTV"
        def liveContent(self, url): return ""
        def localProxy(self, params): return []
        def destroy(self): return ""

# 格式: '真實 asset_id': ('頻道名稱', '分組名稱')
CHANNELS = {
    # ── 新聞財經 ──
    '4gtv-4gtv009': ('中天新聞台', '新聞財經'),
    '4gtv-4gtv051': ('台視新聞', '新聞財經'),
    '4gtv-4gtv052': ('華視新聞', '新聞財經'),
    '4gtv-4gtv074': ('中視新聞', '新聞財經'),
    'litv-ftv13': ('民視新聞台', '新聞財經'),
    '4gtv-4gtv152': ('東森新聞台', '新聞財經'),
    '4gtv-4gtv153': ('東森財經新聞台', '新聞財經'),
    'iNEWS': ('三立新聞iNEWS', '新聞財經'),
    'setnews': ('三立新聞LIVE', '新聞財經'),
    'mnews': ('鏡電視新聞台', '新聞財經'),
    'litv-longturn14': ('寰宇新聞台', '新聞財經'),
    '4gtv-4gtv156': ('寰宇新聞台灣台', '新聞財經'),
    '4gtv-4gtv158': ('寰宇財經台', '新聞財經'),
    '4gtv-4gtv010': ('非凡新聞台', '新聞財經'),
    '4gtv-4gtv048': ('非凡商業台', '新聞財經'),
    '4gtv-4gtv056': ('台視財經', '新聞財經'),
    '4gtv-4gtv104': ('第1商業', '新聞財經'),

    # ── 無線與公廣 ──
    '4gtv-4gtv066': ('台視', '無線綜合'),
    '4gtv-4gtv040': ('中視', '無線綜合'),
    '4gtv-4gtv041': ('華視', '無線綜合'),
    '4gtv-4gtv155': ('民視', '無線綜合'),
    '4gtv-4gtv043': ('客家電視台', '無線綜合'),
    '4gtv-4gtv080': ('原住民族電視台', '無線綜合'),
    '4gtv-4gtv084': ('國會頻道1台', '無線綜合'),
    '4gtv-4gtv085': ('國會頻道2台', '無線綜合'),

    # ── 民視家族 ──
    '4gtv-4gtv001': ('民視台灣台', '民視家族'),
    '4gtv-4gtv003': ('民視第一台', '民視家族'),
    '4gtv-4gtv004': ('民視綜藝台', '民視家族'),
    'litv-ftv09': ('民視影劇台', '民視家族'),
    'litv-ftv07': ('民視旅遊台', '民視家族'),

    # ── 龍華家族 ──
    'litv-xinchuang01': ('龍華卡通台', '龍華家族'),
    'litv-xinchuang02': ('龍華洋片台', '龍華家族'),
    'litv-xinchuang03': ('龍華電影台', '龍華家族'),
    'litv-xinchuang11': ('龍華日韓台', '龍華家族'),
    'litv-xinchuang12': ('龍華偶像台', '龍華家族'),
    'litv-xinchuang18': ('龍華戲劇台', '龍華家族'),
    'litv-xinchuang21': ('龍華經典台', '龍華家族'),

    # ── 靖天與靖洋家族 ──
    '4gtv-4gtv044': ('靖天卡通台', '靖天家族'),
    '4gtv-4gtv045': ('靖洋戲劇台', '靖天家族'),
    '4gtv-4gtv046': ('靖天綜合台', '靖天家族'),
    '4gtv-4gtv047': ('靖天日本台', '靖天家族'),
    '4gtv-4gtv054': ('Nice TV靖天歡樂台', '靖天家族'),
    '4gtv-4gtv055': ('靖天映畫', '靖天家族'),
    '4gtv-4gtv057': ('靖洋卡通台Nice Bingo', '靖天家族'),
    '4gtv-4gtv058': ('靖天戲劇台', '靖天家族'),
    '4gtv-4gtv061': ('靖天電影台', '靖天家族'),
    '4gtv-4gtv062': ('靖天育樂台', '靖天家族'),
    '4gtv-4gtv063': ('KLT-靖天國際台', '靖天家族'),
    '4gtv-4gtv065': ('靖天資訊台', '靖天家族'),

    # ── 電影戲劇 ──
    '4gtv-4gtv042': ('公視戲劇', '電影戲劇'),
    '4gtv-4gtv049': ('采昌影劇台', '電影戲劇'),
    '4gtv-4gtv011': ('影迷數位電影台', '電影戲劇'),
    'litv-ftv10': ('My Cinema Europe HD 我的歐洲電影', '電影戲劇'),
    'litv-xinchuang22': ('台灣戲劇台', '電影戲劇'),
    'litv-fast1226': ('Focus焦點電影台', '電影戲劇'),
    'litv-fast1224': ('Focus風采戲劇台', '電影戲劇'),
    'litv-fast1225': ('黃金八點檔', '電影戲劇'),

    # ── 綜藝娛樂 ──
    '4gtv-4gtv034': ('八大精彩台', '綜藝娛樂'),
    '4gtv-4gtv039': ('八大綜藝台', '綜藝娛樂'),
    'litv-fast1223': ('Focus歡樂綜合台', '綜藝娛樂'),
    '4gtv-4gtv006': ('豬哥亮歌廳秀', '綜藝娛樂'),
    '4gtv-4gtv016': ('韓國娛樂台 KMTV', '綜藝娛樂'),
    '4gtv-4gtv109': ('中天亞洲台', '綜藝娛樂'),

    # ── 博斯與體育運動 ──
    'litv-xinchuang04': ('博斯魅力台', '體育運動'),
    'litv-xinchuang05': ('博斯高球台', '體育運動'),
    'litv-xinchuang06': ('博斯高球二台', '體育運動'),
    'litv-xinchuang07': ('博斯運動一台', '體育運動'),
    'litv-xinchuang08': ('博斯運動二台', '體育運動'),
    'litv-xinchuang09': ('博斯網球台', '體育運動'),
    'litv-xinchuang10': ('博斯無限台', '體育運動'),
    'litv-xinchuang13': ('博斯無限二台', '體育運動'),
    '4gtv-4gtv101': ('智林體育台', '體育運動'),
    '4gtv-4gtv014': ('時尚運動X', '體育運動'),
    '4gtv-4gtv053': ('GINX Esports TV', '體育運動'),
    '4gtv-4gtv077': ('TRACE Sport Stars', '體育運動'),

    # ── 兒童知性與生活 ──
    'litv-xinchuang20': ('ELTV英語學習台', '生活知性'),
    'litv-xinchuang19': ('Smart知識台', '生活知性'),
    '4gtv-4gtv018': ('達文西頻道', '生活知性'),
    '4gtv-4gtv076': ('亞洲旅遊台', '生活知性'),
    '4gtv-4gtv064': ('幸福空間居家台', '生活知性'),
    '4gtv-4gtv110': ('Pet Club TV', '生活知性'),
    '4gtv-4gtv013': ('視納華仁紀實頻道', '生活知性'),
    'litv-ftv15': ('影迷數位紀實台', '生活知性'),
    '4gtv-4gtv070': ('INULTRA', '生活知性'),

    # ── 音樂外語與宗教 ──
    '4gtv-4gtv059': ('CLASSICA 古典樂', '音樂宗教'),
    '4gtv-4gtv082': ('TRACE Urban', '音樂宗教'),
    '4gtv-4gtv083': ('Mezzo Live HD', '音樂宗教'),
    '4gtv-4gtv079': ('ARIRANG阿里郎頻道', '音樂宗教'),
    'litv-ftv16': ('好消息', '音樂宗教'),
    'litv-ftv17': ('好消息2台', '音樂宗教'),
    'daystar': ('DayStar', '音樂宗教'),

    # ── 購物頻道 ──
    '4gtv-4gtv102': ('東森購物1台', '電視購物'),
    '4gtv-4gtv103': ('東森購物2台', '電視購物'),
    'litv-etm3': ('東森購物測試頻道', '電視購物'),
}

BASE_API_URL = 'https://www.litv.tv/vod/ajax/getUrl'
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Referer': 'https://www.litv.tv/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
}

class Spider(BaseSpider):
    def getName(self):
        return "LiTV全頻道"

    def init(self, extend):
        pass

    def _fetch_url(self, url, headers=None):
        try:
            req = urllib.request.Request(url, headers=headers or BROWSER_HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read()
        except Exception:
            return None

    def liveContent(self, url):
        """產生 TVBox 的直播列表"""
        lines = ['#EXTM3U']
        base_proxy = self.getProxyUrl()
        if not base_proxy.endswith(('?', '&')):
            base_proxy += '&'

        for cid, (name, group) in CHANNELS.items():
            lines.append(f'#EXTINF:-1 tvg-id="{name}" tvg-name="{name}" group-title="{group}",{name}')
            lines.append(f'{base_proxy}do=py&fun=litv&id={cid}')

        return '\n'.join(lines)

    def localProxy(self, params):
        """解析 LiTV 直播流並重寫 M3U8 切片為絕對路徑"""
        fun = params.get('fun')
        if fun == 'litv':
            channel_id = params.get('id')
            if not channel_id or channel_id not in CHANNELS:
                return [404, "text/plain", "Channel not found"]

            # API 請求：LiTV 對不同前綴的頻道參數兼容處理
            param_type = 'channel' if channel_id.startswith('litv-fast') else 'live'
            api_params = urllib.parse.urlencode({
                'type': param_type,
                'asset_id': channel_id,
            })
            api_url = f"{BASE_API_URL}?{api_params}"

            content = self._fetch_url(api_url)
            if not content:
                return [500, "text/plain", "Fetch LiTV API failed"]

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

                sub_content = self._fetch_url(playlist_url)
                if not sub_content:
                    return [500, "text/plain", "Fetch sub playlist failed"]

                sub_text = sub_content.decode('utf-8', errors='replace')
                base_dir = playlist_url[:playlist_url.rfind('/') + 1]
                fixed_lines = []

                # 將分片相對路徑全部替換為絕對路徑，確保 TVBox 播放器能正確請求
                for line in sub_text.splitlines():
                    line_s = line.strip()
                    if line_s and not line_s.startswith('#') and ('.ts' in line_s or '.m4s' in line_s):
                        fixed_lines.append(urljoin(base_dir, line_s))
                    else:
                        fixed_lines.append(line)

                return [200, "application/vnd.apple.mpegurl", '\n'.join(fixed_lines)]

            except Exception as e:
                return [500, "text/plain", f"Internal Error: {str(e)}"]

        return [400, "text/plain", "Bad Request"]

    def destroy(self):
        pass
