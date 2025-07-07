import requests
from datetime import datetime, timedelta
from collections import defaultdict


def format_date_chinese(dt: datetime) -> str:
    """
    将 datetime 对象格式化为中文日期格式，如：
    输入：2025-07-04 10:00:00
    输出："7月4日"
    """
    month = dt.month
    day = dt.day
    return f"{month}月{day}日"


def get_zqcy(start_time=None, end_time=None):
    # 1. 设置默认时间（默认查询过去24小时数据）
    # 1. 设置默认时间（默认查询过去24小时数据）
    if start_time is None:
        start_dt = datetime.now() - timedelta(days=1)
    elif isinstance(start_time, str):
        # 尝试将字符串转为 datetime 对象
        try:
            start_dt = datetime.strptime(start_time, "%Y-%m-%d")
        except ValueError:
            try:
                start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(f"无法解析开始时间：{start_time}")
    else:
        start_dt = start_time

    if end_time is None:
        end_dt = datetime.now()
    elif isinstance(end_time, str):
        try:
            end_dt = datetime.strptime(end_time, "%Y-%m-%d")
        except ValueError:
            try:
                end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(f"无法解析结束时间：{end_time}")
    else:
        end_dt = end_time

    # 2. 格式化时间参数（与接口要求的格式匹配）

    start_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')
    end_str = end_dt.strftime('%Y-%m-%d %H:%M:%S')

    # 3. 调用接口获取数据
    url = 'http://10.112.239.217:8000/get_ylzdjcxxnew'
    params = {'STARTTM': start_str, 'ENDTM': end_str}
    headers = {
        'Authorization': 'Bearer eyJ0eXAiOiJqd3QiLCJhbGciOiJIUzI1NiIsInVjIjoiNWVmMGY2MGEyY2U0MTFmMGE1MTUwMjQyMTFhZDZmY2IiLCJ0b2tlbl90eXBlIjoxfQ.eyJpc3MiOiJ6WEVXNGVKTENsVXZ3NnUyVTdBZkZlMDFjSWlBbjlRciIsImlhdCI6MTc0OTgwMDAxMH0.l7VubKAAPXn_SEyhTnpyWiooR0lHUzqaGHR67vwcl4s'
        # 认证令牌
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        api_data = response.json()
    except requests.exceptions.JSONDecodeError:
        return "接口返回数据格式错误，无法解析为JSON"
    except Exception as e:
        return f"数据获取失败：{str(e)}"

    # 4. 验证接口返回状态
    if api_data.get('status') != 200 or api_data.get('message') != 'success':
        return f"接口返回异常：状态码{api_data.get('status')}，信息{api_data.get('message')}"

    # 5. 提取并过滤有效站点数据
    try:
        stations = api_data['data']['result']['values']
        # 仅保留包含必要字段的有效字典
        stations = [s for s in stations if isinstance(s, dict) and 'station_name' in s and 'gqyxsjs' in s]
    except (KeyError, TypeError):
        print(api_data)
        return "接口数据结构异常，无法提取站点信息"

    if not stations:
        return "未获取到有效水文站数据"

    # 6. 按站点名称累加降水量（核心逻辑）
    station_rainfall = defaultdict(float)  # 键：站点名称，值：累加后的降水量
    for station in stations:
        # 处理站点名称（去重的依据）
        name = station['station_name'].strip() or '未知站点'
        # 处理降水量（转换为浮点数，异常值视为0）
        gqyxsjs_val = station['gqyxsjs']
        try:
            rainfall = float(gqyxsjs_val) if gqyxsjs_val is not None else 0.0
        except (ValueError, TypeError):
            rainfall = 0.0
        # 累加同一站点的降水量
        station_rainfall[name] += rainfall

    # 7. 按累加后的降水量统计各区间站点数量
    count_0_10 = 0  # 0-10mm
    count_10_50 = 0  # 10-50mm
    count_50_100 = 0  # 50-100mm
    count_100_200 = 0  # 100-200mm
    count_200_up = 0  # 200mm以上
    max_rainfall = -1  # 最大累加降水量
    max_station = "无数据"  # 最大降水量对应站点

    for name, total in station_rainfall.items():
        # 统计区间
        if 0 <= total < 10:
            count_0_10 += 1
        elif 10 <= total < 50:
            count_10_50 += 1
        elif 50 <= total < 100:
            count_50_100 += 1
        elif 100 <= total < 200:
            count_100_200 += 1
        elif total >= 200:
            count_200_up += 1
        # 更新最大降水量及站点
        if total > max_rainfall:
            max_rainfall = total
            max_station = name

    # 8. 生成结果文本
    # date_range = f"{start_time.strftime('%m月%d日')}-{end_time.strftime('%m月%d日')},"
    formatted_range = f"{format_date_chinese(start_dt)}-{format_date_chinese(end_dt)},"
    result = (f"{formatted_range} 0-10mm降水量的水文站{count_0_10}个，"
              f"10-50mm降雨量的水文站{count_10_50}个，"
              f"50-100mm降雨量的水文站{count_50_100}个，"
              f"100-200mm降雨量的水文站{count_100_200}个，"
              f"200mm以上降雨量的水文站{count_200_up}个，"
              f"最大降雨量发生在{max_station}（累计{max_rainfall:.1f}mm）。")
    return result


def get_zhgk(params: dict):
    """_summary_ 灾情综述
    Args:
        params (_type_): _description_
    Returns:
        _type_: _description_
    """
    result = f"{params['startdate']}至{params['enddate']}，[榆阳区]遭受严重洪涝灾害袭击。据统计，本次洪涝灾害共涉及[2]个县（市、区）、[3]个乡（镇、街道），受灾人口达[4]万人，农作物受灾面积[40]千公顷。灾害造成[5]个城镇受淹，因灾死亡[3000]人，失踪[300]人，紧急转移安置人口[50]人。本次洪涝灾害直接经济损失总计[30]亿元，其中水利工程设施直接经济损失[20]亿元。"

    return result


def get_slgcssssqk(params: dict):
    """_summary_ 水利工程设施受损情况

    """

    p1 = "此次洪涝灾害共造成[5]座水库不同程度受损，其中大(1)型水库[1]座、大(2)型水库[1]座、中型水库[1]座、小(1)型水库[2]座、小(2)型水库[3]座，直接经济损失合计[5000]万元。特别严重的是发生了[2]座水库垮坝事件，涉及大(1)型水库[2]座、大(2)型水库[2]座、中型水库[3]座、小(1)型水库[12]座、小(2)型水库[12]座。"
    p2 = "    洪涝灾害导致堤防设施大面积受损，共计[10]处堤防受损，其中1级堤防[2]处、2级堤防[3]处、3级及以下堤防[5]处，受损长度分别为[6]米、[60]米、[21]米，造成直接经济损失[6000]万元。更为严重的是出现了[10]处堤防决口，涉及1级堤防[4]处、2级堤防[3]处、3级及以下堤防[3]处，决口长度分别为[10]米、[5]米、[8]米。大中型护岸[12]处受损，小型护岸[12]处受损，直接经济损失[1000]万元。"
    p3 = "    水闸设施共[5]座受损，直接损失[6]万元。塘坝工程[6]座受损，损失[3]万元。灌排设施[12]处受损，损失[1211]万元。水文测站[5]个受损，损失[12]万元。机电井[11]座受损，损失[6000]万元。机电泵站[8]座受损，损失[1600]万元。水电站[8]座受损，损失[500]万元。淤地坝[6]座受损，直接损失[1200]万元。人饮基础设施[12]处受损，直接损失[3]万元。供水工程设施[3]处受损，直接损失[5] 万元其他水利工程设施[7]处受损，损失[6000]万元。"
    return p1 + "\n" + p2 + "\n" + p3


def get_zdslgcsgqk(params: dict):
    """_summary_ 重大水利工程事故详情

    """
    p1 = "本次洪涝灾害期间发生水库垮坝事故[10]起。其中[水库名称]位于[水系名称]，为[大型水库]，总库容[10]万立方米，[大坝类型]，坝高[10]米，由[佳县水利局]管理。该水库于[年-月-日-时]在[垮坝位置]发生垮坝，垮坝原因为[具体原因]，垮坝形式为[具体形式]，造成[10]人受灾。[其他水库垮坝情况类似描述]"
    p2 = "    洪涝灾害期间共发生堤防决口事故[10]起。[堤防名称]位于[水系名称]，为[堤防级别]，由[佳县水利局]管理。该堤防于[年-月-日-时]在[决口位置]（起始桩号[具体桩号]）发生决口，决口宽度[10]米，决口原因为[具体原因]，决口形式为[具体形式]，造成[10]人受灾。[其他堤防决口情况类似描述]"
    p3 = "   本次洪涝灾害造成较大水毁工程[10]处。[工程名称]为[工程类型]，工程级别为[具体级别]，由[佳县水利局]管理，位于[具体位置]。该工程水毁等级为[具体等级]，损毁情况为[损毁描述]，损毁原因为[具体原因]，造成直接经济损失[10]万元。[其他较大水毁工程情况类似描述]"
    return p1 + "\n" + p2 + "\n " + p3


def get_czsyqk(params: dict):
    """_summary_ 城镇受淹情况

    Args:
        params (_type_): _description_

    Returns:
        _type_: _description_
    """
    result = "洪涝灾害期间，共有[10]个城镇不同程度受淹。其中[城镇名称]受淹面积[10]平方公里，占城镇总面积的[10]%，进水时代表站水位[10]米，进水时间为[月-日-时]，淹没历时[10]小时，主要街区最大水深达[10]米。[其他受淹城镇情况类似描述]"
    return result


def get_khqxjszcqk(params: dict):
    """_summary_ 抗洪抢险技术支撑情况

    Args:
        params (_type_): _description_
    """
    p1 = "各级政府高度重视抗洪抢险工作，组织开展了大规模的巡堤查险活动，巡堤查险[10]人天。派出省级专家组[10]人天、市级[10]人天、县级[10]人天指导抢险，为抗洪抢险提供技术支撑。"
    p2 = "    省级及以下各级政府总计投入抗洪抢险资金[10]万元，其中水利救灾资金投入[10]万元，技术支撑投入[10]万元，有力保障了抗洪抢险工作的顺利开展。"
    p3 = "    通过积极有效的防汛抗洪措施，取得了显著的防洪减灾效益。减少受灾人口[10]万人，减淹耕地[10]千公顷，避免县级以上城镇受淹[10]座，防洪减灾经济效益达[10]亿元。"
    return p1 + "\n" + p2 + "\n" + p3


def get_shzhfyqk(params: dict):
    """_summary_ 山洪灾害防御情况
    Args:
        params (_type_): _description_

    Returns:
        _type_: _description_
    """
    p1 = "山洪灾害防御期间，共有[10]个县发布山洪灾害预警，发布山洪灾害预警[10]次，发布预警[10]次。向责任人发布预警短信[10]万条，向社会公众发布预警短信[10]万条，启动预警广播[10]站次，预警发布服务人数达[10]人，成功转移人口[10]万人。"
    p2 = "    本次洪涝灾害期间共发生山洪灾害事件[10]起。[发生时间：年-月-日-时]在[县（市、区）-乡（镇、街道）-村（社区）]发生山洪灾害，造成死亡[10]人，失踪[10]人。当时实测降雨量为1小时[10]毫米、3小时[10]毫米、6小时[10]毫米、24小时[10]毫米，灾害类型为[灾害类型]，[是]发布预警。该事件造成受灾人口[10]人，倒塌房屋[10]间，直接经济损失[10]万元。[暂无]"
    return p1 + "\n" + p2


def get_zdszdqfx(params: dict):
    """_summary_ 重点受灾地区分析

    Args:
        params (_type_): _description_

    Returns:
        _type_: _description_
    """
    result = "根据统计数据分析，[榆阳区]、[衡山区]、[子洲县]等地区受灾相对较重。其中[榆阳区]受损[设施类型][10]座（处），损失[10]万元，占该地区水利设施损失的[10]%；[地区名称]受损[设施类型][10]座（处），损失[10]万元，占该地区水利设施损失的[10]%。[地区名称][具体受损情况]受损[10]处，损失[10]万元，占该地区水利设施损失的[10]%。"
    return result
