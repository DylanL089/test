# -*- coding: utf-8 -*-
"""
litv_tvbox.py — TVBox 專用 LiTV 台灣完整免費直播/滾動頻道爬蟲
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

# LiTV 完整免費用戶頻道資料庫
# 格式: 'channel_id': ('頻道名稱', '台標URL', '分組名稱')
CHANNELS = {
    # ── 新聞財經 ──
    '4gtv-4gtv009': ('中天新聞台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/CTI2.png', '新聞財經'),
    '4gtv-4gtv052': ('華視新聞', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/CTS1.png', '新聞財經'),
    '4gtv-4gtv074': ('中視新聞', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/CTV1.png', '新聞財經'),
    'litv-longturn14': ('寰宇新聞台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/Global2.png', '新聞財經'),
    '4gtv-4gtv156': ('寰宇新聞台灣台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/Global3.png', '新聞財經'),
    '4gtv-4gtv158': ('寰宇財經台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/Global4.png', '新聞財經'),
    '4gtv-4gtv104': ('第1商業台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv104_tv.png', '新聞財經'),
    'iNEWS': ('三立新聞iNEWS', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/SET3.png', '新聞財經'),

    # ── 無線老三台/綜合 ──
    '4gtv-4gtv040': ('中視', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/CTV.png', '無線綜合'),
    '4gtv-4gtv041': ('華視', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/CTS.png', '無線綜合'),
    '4gtv-4gtv077': ('中視經典台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv077_tv.png', '無線綜合'),
    '4gtv-4gtv078': ('中視菁采台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv078_tv.png', '無線綜合'),
    '4gtv-4gtv079': ('華視教育體育文化台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv079_tv.png', '無線綜合'),

    # ── 電影戲劇 ──
    'litv-xinchuang02': ('龍華洋片台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV2.png', '電影戲劇'),
    'litv-xinchuang03': ('龍華電影台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV1.png', '電影戲劇'),
    'litv-xinchuang11': ('龍華日韓台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV5.png', '電影戲劇'),
    'litv-xinchuang12': ('龍華偶像台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV6.png', '電影戲劇'),
    'litv-xinchuang18': ('龍華戲劇台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV4.png', '電影戲劇'),
    'litv-xinchuang21': ('龍華經典台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV7.png', '電影戲劇'),
    'litv-xinchuang22': ('台灣戲劇台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/Taiwanxiju.png', '電影戲劇'),
    '4gtv-4gtv056': ('影迷數位電影台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv056_tv.png', '電影戲劇'),
    '4gtv-4gtv080': ('靖天電影台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv080_tv.png', '電影戲劇'),
    '4gtv-4gtv081': ('靖天日本台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv081_tv.png', '電影戲劇'),
    '4gtv-4gtv082': ('靖天戲劇台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv082_tv.png', '電影戲劇'),
    '4gtv-4gtv068': ('金光布袋戲', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv068_tv.png', '電影戲劇'),

    # ── 兒童動漫 ──
    'litv-xinchuang01': ('龍華卡通台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/LTV9.png', '兒童動漫'),
    '4gtv-4gtv055': ('靖天卡通台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv055_tv.png', '兒童動漫'),
    'litv-xinchuang20': ('ELTV生活英語台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/ELTA7.png', '兒童動漫'),
    '4gtv-4gtv071': ('達文西頻道 DaVinci', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv071_tv.png', '兒童動漫'),

    # ── 綜合生活與知性 ──
    '4gtv-4gtv076': ('亞洲旅遊台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/Asiatravel.png', '綜合生活'),
    'litv-xinchuang19': ('SMART知識台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/smarttv.png', '綜合生活'),
    '4gtv-4gtv084': ('國會頻道1台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/guohui1.png', '綜合生活'),
    '4gtv-4gtv085': ('國會頻道2台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/guohui2.png', '綜合生活'),
    '4gtv-4gtv083': ('靖天育樂台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv083_tv.png', '綜合生活'),
    '4gtv-4gtv062': ('靖天資訊台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv062_tv.png', '綜合生活'),
    '4gtv-4gtv063': ('靖天綜合台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv063_tv.png', '綜合生活'),
    'litv-ftv16': ('好消息 GOOD TV', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/GoodTV1.png', '綜合生活'),
    'litv-ftv17': ('好消息2台 GOOD TV 2', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/GoodTV2.png', '綜合生活'),
    '4gtv-4gtv069': ('大愛電視', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv069_tv.png', '綜合生活'),
    '4gtv-4gtv070': ('大愛二台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv070_tv.png', '綜合生活'),
    '4gtv-4gtv058': ('原住民族電視台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv058_tv.png', '綜合生活'),
    '4gtv-4gtv059': ('客家電視台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv059_tv.png', '綜合生活'),

    # ── 運動賽事 ──
    '4gtv-4gtv064': ('智林體育台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv064_tv.png', '體育運動'),
    '4gtv-4gtv065': ('博斯運動二台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv065_tv.png', '體育運動'),
    '4gtv-4gtv066': ('博斯高球台', 'https://p-cdnstatic.svc.litv.tv/pics/logo_litv_4gtv-4gtv066_tv.png', '體育運動'),

    # ── 購物頻道 ──
    '4gtv-4gtv102': ('東森購物1台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/EBC11.png', '電視購物'),
    '4gtv-4gtv103': ('東森購物2台', 'https://cdn.jsdelivr.net/gh/wanglindl/TVlogo@main/img/EBC11.png', '電視購物'),

    # ── LiTV 特色滾動隨選頻道 (VOD 輪播) ──
    'litv-ch101': ('豬哥亮歌廳秀', '', '經典綜藝輪播'),
    'litv-ch102': ('綜藝大集合', '', '經典綜藝輪播'),
    'litv-ch103': ('天才衝衝衝', '', '經典綜藝輪播'),
    'litv-ch104': ('台灣第一等', '', '生活旅遊輪播'),
    'litv-ch105': ('世界第一等', '', '生活旅遊輪播'),
    'litv-ch106': ('食尚玩家精選', '', '生活旅遊輪播'),
    'litv-ch107': ('木曜4超玩', '', '經典綜藝輪播'),
    'litv-ch108': ('大嘻哈時代', '', '經典綜藝輪播'),
    'litv-ch201': ('瑯琊榜專區', '', '古裝大劇輪播'),
    'litv-ch202': ('後宮甄嬛傳', '', '古裝大劇輪播'),
    'litv-ch203': ('軍師聯盟', '', '古裝大劇輪播'),
    'litv-ch204': ('羋月傳專區', '', '古裝大劇輪播'),
    'litv-ch205': ('知否知否應是綠肥紅瘦', '', '古裝大劇輪播'),
    'litv-ch206': ('步步驚心', '', '古裝大劇輪播'),
    'litv-ch207': ('三生三世十里桃花', '', '古裝大劇輪播'),
    'litv-ch208': ('慶餘年第一季', '', '古裝大劇輪播'),
    'litv-ch301': ('經典台語劇場', '', '台劇專區輪播'),
    'litv-ch302': ('犀利人妻精華', '', '台劇專區輪播'),
    'litv-ch401': ('蠟筆小新馬拉松', '', '動漫馬拉松'),
    'litv-ch402': ('名偵探柯南精選', '', '動漫馬拉松'),
    'litv-ch403': ('中華一番專區', '', '動漫馬拉松'),
    'litv-ch404': ('進擊的巨人馬拉松', '', '動漫馬拉松'),
    'litv-ch405': ('鬼滅之刃專區', '', '動漫馬拉松'),
    'litv-ch406': ('咒術迴戰精選', '', '動漫馬拉松'),
    'litv-ch501': ('國片經典老電影', '', '電影馬拉松'),
    'litv-ch502': ('香港懷舊動作片', '', '電影馬拉松'),
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
        return "LiTV完整頻道"

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
        """生成分組清晰的完整 M3U 清單"""
        lines = ['#EXTM3U']
        base_proxy = self.getProxyUrl()
        if not base_proxy.endswith(('?', '&')):
            base_proxy += '&'

        for cid, (name, logo, group) in CHANNELS.items():
            lines.append(f'#EXTINF:-1 tvg-id="{name}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}')
            lines.append(f'{base_proxy}do=py&fun=litv&id={cid}')

        return '\n'.join(lines)

    def localProxy(self, params):
        """動態取得 m3u8 並自動解析補全最高畫質子切片"""
        fun = params.get('fun')
        if fun == 'litv':
            channel_id = params.get('id')
            if not channel_id or channel_id not in CHANNELS:
                return [404, "text/plain", "Channel not found"]

            # 針對一般頻道與輪播頻道的參數兼容
            api_params = urllib.parse.urlencode({
                'type': 'channel' if channel_id.startswith('litv-ch') else 'live',
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
                    # 選擇最高碼率流
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

                # 補全切片絕對路徑
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
