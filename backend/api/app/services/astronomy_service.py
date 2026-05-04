import ephem
import datetime
from typing import Dict, Any, Optional, List
import lunar_python
from lunar_python import Lunar, Solar
import logging

logger = logging.getLogger(__name__)

from app.services.geo_data import CHINA_GEO_DATA, DEFAULT_COORDINATES

logger = logging.getLogger(__name__)

class AstronomyService:
    @staticmethod
    def get_coordinates(location_str: str) -> tuple:
        """
        从位置字符串中智能匹配城市或区县经纬度。
        实现逻辑：
        1. 预处理：清洗字符串，从详细到宽泛切分。
        2. 精确匹配：优先尝试匹配最具体的区县名。
        3. 层级回退：若区县未录入，自动尝试匹配其所属的地级市或省份。
        4. 兜底策略：若全无匹配，返回北京坐标。
        """
        if not location_str:
            return DEFAULT_COORDINATES
            
        # 预处理位置字符串，去除多余后缀并切分
        # 移除“省”、“市”、“区”、“县”等后缀以便提高匹配率
        clean_str = location_str.replace('省', ' ').replace('市', ' ').replace('区', ' ').replace('县', ' ')
        parts = clean_str.replace(',', ' ').replace('，', ' ').split()
        
        # 1. 尝试原始字符串中的各部分（从后往前，即从具体的区县开始）
        for part in reversed(parts):
            # 尝试精确匹配（带后缀或不带后缀）
            for suffix in ['', '市', '区', '县', '盟', '州']:
                lookup_key = f"{part}{suffix}"
                if lookup_key in CHINA_GEO_DATA:
                    return CHINA_GEO_DATA[lookup_key]
        
        # 2. 模糊匹配逻辑：如果上述匹配失败，遍历整个数据库尝试包含匹配
        for part in reversed(parts):
            if len(part) < 2: continue # 过滤掉单字
            for key in CHINA_GEO_DATA:
                if part in key:
                    return CHINA_GEO_DATA[key]
        
        return DEFAULT_COORDINATES

    @staticmethod
    def get_moon_phase(date_time: datetime.datetime) -> Dict[str, Any]:
        """计算月相信息"""
        lunar = Lunar.fromDate(date_time)
        
        # 使用 ephem 计算精确的月亮亮面占比和相位
        observer = ephem.Observer()
        observer.date = date_time.strftime('%Y/%m/%d %H:%M:%S')
        moon = ephem.Moon(observer)
        
        # 判断相位名称
        # phase_angle: 0 (new moon) -> pi (full moon) -> 2pi (new moon)
        # 简化版：根据 illumination 和 waxing/waning 判断
        illumination = moon.moon_phase # 0.0 to 1.0
        
        # 为了判断盈亏，看 1 小时后的亮度变化
        observer.date = (date_time + datetime.timedelta(hours=1)).strftime('%Y/%m/%d %H:%M:%S')
        moon_future = ephem.Moon(observer)
        is_waxing = moon_future.moon_phase > illumination

        if illumination < 0.05:
            phase_name = "新月 (朔)"
        elif illumination > 0.95:
            phase_name = "满月 (望)"
        elif 0.45 < illumination < 0.55:
            phase_name = "上弦月" if is_waxing else "下弦月"
        elif illumination < 0.5:
            phase_name = "峨眉月" if is_waxing else "残月"
        else:
            phase_name = "盈凸月" if is_waxing else "亏凸月"
        
        return {
            "lunar_day": f"农历{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
            "phase_name": phase_name,
            "illumination": round(illumination * 100, 1)
        }

    @staticmethod
    def get_retrograde_planets(date_time: datetime.datetime) -> List[str]:
        """判断当前是否有行星逆行 (水星、金星、火星等)"""
        planets = {
            "水星": ephem.Mercury(),
            "金星": ephem.Venus(),
            "火星": ephem.Mars(),
            "木星": ephem.Jupiter(),
            "土星": ephem.Saturn()
        }
        
        retrograde = []
        observer = ephem.Observer()
        observer.date = date_time.strftime('%Y/%m/%d %H:%M:%S')
        
        # 简单算法：判断行星相对于恒星的赤经变化率
        # 为了更准确，比较当前时间前后 1 天的赤经
        t1 = date_time - datetime.timedelta(days=1)
        t2 = date_time + datetime.timedelta(days=1)
        
        for name, planet in planets.items():
            observer.date = t1.strftime('%Y/%m/%d %H:%M:%S')
            planet.compute(observer)
            ra1 = planet.ra
            
            observer.date = t2.strftime('%Y/%m/%d %H:%M:%S')
            planet.compute(observer)
            ra2 = planet.ra
            
            # 如果赤经减小（排除跨越 0 点的情况），则视为逆行
            if ra2 < ra1 and abs(ra2 - ra1) < 1.0: # 1.0 radians is a large gap
                retrograde.append(name)
        
        return retrograde

    @classmethod
    def get_realtime_phenomena(cls, location_str: str, date_time: Optional[datetime.datetime] = None) -> str:
        """生成实时天象描述字符串"""
        if not date_time:
            date_time = datetime.datetime.now()
            
        try:
            coords = cls.get_coordinates(location_str)
            lunar = Lunar.fromDate(date_time)
            solar = Solar.fromDate(date_time)
            
            # 1. 月相
            moon_info = cls.get_moon_phase(date_time)
            moon_desc = f"{moon_info['lunar_day']}（{moon_info['phase_name']}，亮面占比 {moon_info['illumination']}%）"
            
            # 2. 节气
            jie_qi = lunar.getJieQi() or "无特殊节气"
            
            # 3. 行星逆行
            retro_planets = cls.get_retrograde_planets(date_time)
            retro_desc = f"{', '.join(retro_planets)}逆行中" if retro_planets else "行星运行平稳，无逆行现象"
            
            # 4. 28星宿
            mansion = lunar.getXiu()
            
            return f"当前月相：{moon_desc}；当前节气：{jie_qi}；行星动态：{retro_desc}；星宿：{mansion}宿值日。"
        except Exception as e:
            logger.error(f"Error calculating astronomical info: {e}")
            return "星辰流转，磁场稳定 (天象计算波动)"
