# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import random
import re
import sys
import time
import urllib.request
from datetime import datetime
from typing import List
from urllib import parse
from urllib.error import URLError

from loguru import logger

_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42"


def start_greet(expectId: str, securityId: str, lid: str, encryptGeekId: str, geekName: str):
    start_url = "https://www.zhipin.com/wapi/zpjob/chat/start"
    start_headers = dict()
    start_headers["Content-Type"] = "application/x-www-form-urlencoded"
    start_headers["Cookie"] = _cookie
    start_headers["User-Agent"] = _user_agent  # 非必须
    # headers["zp_token"] = "V1RN4vF-L52VhiVtRvyRkcLSK17zvQxyQ~"
    # headers["traceId"] = "AB0CE048-62F5-4883-9A0D-FD7C45BFD340"
    # headers["X-Anti-Request-Token"] = "d41d8cd98f00b204e9800998ecf8427e"
    start_content = dict()
    start_content["expectId"] = expectId  # 必须，否则会报{"code":17,"message":"缺少必要参数","zpData":{}}
    start_content["jid"] = _encryptJobId  # 必须，否则会报{"code":17,"message":"缺少必要参数","zpData":{}}
    # content["gid"] = encryptGeekId  # 非必须
    # content["lid"] = lid  # 非必须
    start_content["securityId"] = securityId  # 必须，否则会报{"code":1092,"message":"操作失败","zpData":{}}
    start_data = parse.urlencode(start_content)
    start_request = urllib.request.Request(start_url, start_data.encode(), headers=start_headers)
    start_response = urllib.request.urlopen(start_request)
    start_result_str = start_response.read().decode()
    start_result_json: dict = json.loads(start_result_str)
    start_result_code = start_result_json["code"]
    if start_result_code == 0:
        logger.success(f"向候选人：【{geekName}】打招呼成功")
        return True
    else:
        logger.error("向候选人打招呼失败：错误信息如下")
        logger.error(start_result_str)
        return False


def check_edu_list(school_name: str) -> bool:
    return True if _school_list.count(school_name) else False


def check_edu_end_date(end_date: str) -> bool:
    if len(end_date) > 4:
        return datetime.today().year >= int(end_date[:4])
    return True


def find_relevant_talent(geek: dict):
    regex_list: List[str] = list()
    geekCard: dict = geek.get("geekCard")
    geekName = geekCard.get("geekName")
    geekGender = geekCard.get("geekGender")  # 性别 1是男0是女
    geekWorkYear = geekCard.get("geekWorkYear")
    geekDegree = geekCard.get("geekDegree")
    geekDesc: dict = geekCard.get("geekDesc")
    geekDesc_content = geekDesc.get("content")  # 个人优势
    regex_list.append(geekDesc_content)
    expectPositionName = geekCard.get("expectPositionName")  # 期望岗位
    regex_list.append(expectPositionName)
    expectLocationName = geekCard.get("expectLocationName")  # 期望城市
    activeTimeDesc = geekCard.get("activeTimeDesc")  # 活跃状态
    geekEdu: dict = geekCard.get("geekEdu")  # 教育信息（最高）
    height_school = geekEdu.get("school")
    height_major = geekEdu.get("major")
    graduationDate = geekEdu.get("endDate")
    geekEdus: List[dict] = geekCard.get("geekEdus")  # 所有教育信息
    geekWorks: dict = geekCard.get("geekWorks")  # 工作经历
    if geekWorks:
        for work in geekWorks:
            company = work.get("company")
            positionCategory = work.get("positionCategory")
            positionName = work.get("positionName")
            regex_list.append(positionName)
            responsibility = work.get("responsibility")  # 工作内容
            workPerformance = work.get("workPerformance")  # 业绩
            workEmphasisList = work.get("workEmphasisList")  # 工作重点标签
            startDate = work.get("startDate")
            endDate = work.get("endDate")
    regex_math_list = list()
    for regex in regex_list:
        new_position_match = _position_match
        # 对正则的特殊字符进行转义，由于转义的时候会用到\所以提前对\转义，否则会对转义后的转义字符重复转义。目前转义的字符是【\,+,?,*,.】
        for char in "\\+?*.":
            new_position_match = new_position_match.replace(char, f"\\{char}")
        regex_result = re.search(f"\\.*{new_position_match}\\.*", regex)
        if regex_result:
            regex_math_list.append(regex)
    if regex_math_list:
        logger.info(f"匹配到岗位关键字：{regex_math_list}")
        if geekEdus:
            for index, edu in enumerate(geekEdus):
                school = edu.get("school")
                major = edu.get("major")
                degreeName = edu.get("degreeName")
                eduType = edu.get("eduType")  # 教育类型：1 全日制，2 非全日制，列表页没有给到具体的类型
                startDate = edu.get("startDate")
                endDate = edu.get("endDate")

                if check_edu_end_date(endDate) and check_edu_list(school):
                    logger.info(f"匹配到的教育经历：学校：{school}，专业：{major}，学历：{degreeName}，开始时间：{startDate}，"
                                f"结束时间：{endDate}。")
                    break
                if index == len(geekEdus) - 1:
                    logger.info(f"未匹配到教育经历：候选人姓名：{geekName}，性别：{'男' if geekGender == 1 else '女'}，"
                                f"工作年限：{geekWorkYear}，期望岗位：{expectPositionName}，学历：{geekDegree}，"
                                f"学校：{height_school}，毕业时间：{graduationDate}，专业：{height_major}")
                    return
        logger.success(
            f"匹配到简历：候选人姓名：{geekName}，性别：{'男' if geekGender == 1 else '女'}，工作年限：{geekWorkYear}，"
            f"期望岗位：{expectPositionName}，学历：{geekDegree}，学校：{height_school}，毕业时间：{graduationDate}，"
            f"专业：{height_major}")
        expectId = geekCard.get("expectId")
        lid = geekCard.get("lid")
        securityId = geekCard.get("securityId")
        encryptGeekId = geekCard.get("encryptGeekId")
        time.sleep(random.randint(3, 10))  # 随机延时3-10秒，防止出现人机验证
        if start_greet(expectId, securityId, lid, encryptGeekId, geekName):
            return True
    return False


def query_resume():
    headers = dict()
    headers["Cookie"] = _cookie  # 必须，否则会报'{"code":7,"message":"当前登录状态已失效","zpData":{}}'
    headers["User-Agent"] = _user_agent  # 非必须
    # 搜索条件
    age = "16,30"  # 年龄：16-30岁
    gender = "0"  # 性别：0不限
    exchangeResume = "0"  # 是否与同事交换简历：0不限
    switchJob = "0"  # 跳槽频率：0不限
    activation = "2505"  # 活跃度：2505本月活跃
    recentNotView = "2301"  # 近期没有看过：2301近14天没有
    school = "0"  # 学校：
    major = "0"  # 专业：0不限
    experience = "104,105,106,103"  # 工作经验：0不限
    degree = "203,204,205"  # 学位：
    intention = "701,704,703"  # 求职意向
    salary = "0"  # 薪资待遇：0不限
    query_base_url = "https://www.zhipin.com/wapi/zpjob/rec/geek/list"
    query_url = f"https://www.zhipin.com/wapi/zpjob/rec/geek/list?age=16,29&gender=0&exchangeResumeWithColleague=0" \
                f"&switchJobFrequency=0&activation=2505&recentNotView=2301&school=1104,1105,1106,1103,1102&major=0" \
                f"&experience=104,105,106,103&degree=203,204,205&salary=0&intention=701,704,703&jobId={_encryptJobId}" \
                f"&page=1&coverScreenMemory=1&_=1664440095639"
    query_url_all = f"{query_base_url}?age={age}&gender={gender}&exchangeResumeWithColleague={exchangeResume}" \
                    f"&switchJobFrequency={switchJob}&activation={activation}&recentNotView={recentNotView}" \
                    f"&school={school}&major={major}&experience={experience}&degree={degree}&salary={salary}" \
                    f"&intention={intention}&jobId={_encryptJobId}"
    sum_resume = 0
    start_greet_count = 0
    for i in range(1, 1 + _page):
        time.sleep(random.randint(3, 10))  # 随机延时3-10秒，防止出现人机验证
        request = urllib.request.Request(f"{query_url_all}&page={i}", headers=headers)
        try:
            response = urllib.request.urlopen(request)
            result_str: str = response.read().decode()
            if not result_str:
                logger.warning(f"查询第【{i}】页的结果为空")
                break
            response_content_type = None
            for header_tuple in response.headers._headers:
                if header_tuple[0] == 'Content-Type':
                    response_content_type = header_tuple[1]
            if response_content_type == "application/json" or response_content_type == "application/json;charset=UTF-8":
                result_json: dict = json.loads(result_str)
                if result_json.get("code") == 0:
                    zp: dict = result_json.get("zpData")
                    if zp and zp.get("geekList"):
                        current_page_size = len(zp.get("geekList"))
                        logger.info(f"当前第【{i}】页，本页共获取到【{current_page_size}】份简历。")
                        if current_page_size != 15:
                            logger.warning(f"当前第【{i}】页，本页共获取到简历数不足15份，请注意，本页获取到【{current_page_size}】份简历。")
                        sum_resume += current_page_size
                        for geek in zp.get("geekList"):
                            if find_relevant_talent(geek):
                                start_greet_count += 1
                        if i % 2 == 0:
                            logger.success(f"已处理【{sum_resume}】份简历，已向【{start_greet_count}】位应聘者打招呼。")
                    else:
                        logger.warning(f"当前第【{i}】页，本页没有获取到简历。")
                        break
                    if not zp.get("hasMore"):
                        logger.warning(f"当前第【{i}】页，没有更多的简历了。")
                        break
                else:
                    logger.error(f"当前第【{i}】页，错误码：{result_json.get('code')}，错误信息：{result_json.get('message')}")
                    logger.debug(f"当前第【{i}】页，查询返回的json：{result_json}")
                    break
            else:
                logger.warning(f"当前第【{i}】页，查询信息返回的结果为【{response_content_type}】类型。")
                logger.error(f"当前第【{i}】页，可能出现人机验证，请到网页进行验证。")
                logger.debug(f"当前第【{i}】页，查询返回结果如下：\n{result_str}")
                break
        except URLError as e:
            logger.error(f"当前第【{i}】页，发生URLError异常，一般重试即可。")
            logger.error(e)
            continue
        except OSError as e:
            logger.error(f"当前第【{i}】页，发生OSError异常")
            logger.error(e)
            break
        except Exception as e:
            logger.error(f"当前第【{i}】页，发生未知异常")
            logger.error(e)
            break

    logger.success(f"共处理【{sum_resume}】份简历，共向【{start_greet_count}】位应聘者打招呼。")


if __name__ == '__main__':
    # cookie = "wd_guid=ab4bc162-c51a-4869-9db3-da0a3c965061; historyState=state; _bl_uid=4vlL85k6gbb1mXbpXf9eetq4wCnz;
    # lastCity=101210100; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1661156155,1662340656,1663552953;
    # wt2=Dg_v58CDzj-7CQjwxWSCq6aYBeMA4GQZ6n8GuoicAuz49tiTcvq4vlZY6U_VHNdt4NQvSv339qhsAvvOuviJzqQ~~;
    # wbg=1; __g=-; __l=l=%2Fwww.zhipin.com%2Fweb%2Fboss%2Findex&r=&g=&s=3&friend_source=0; __c=1664158854;
    # __a=60503236.1657273107.1663552951.1664158854.290.19.2.74; zp_token=V1RN4vF-L52VhiVtRvyRkcLSmy5TPVzSo%7E"
    _wt2 = "DMNUqkUp0RqCcgpmtzRV7MipLqEpyO9ZY9Iq94mTSKlODg1zn9JqUqdm0BBOMsIH7fYxO7eCvbdjnzyQ1b4KH8A~~"
    _cookie = f"wt2={_wt2}"
    _encryptJobId = "c99d46982f8c9e961Xd-09q4GVFY"  # jobid,发布职位的id
    _position_match = "C++"  # 要匹配的职位
    _page = 30  # 查询的页数，每页15条应聘者数据，网页上一次最多只给查30页的数据，不支持30页以上的参数
    _school_check = True  # 是否匹配教育经历，默认匹配
    _log_level = "INFO"  # 日志等级，默认INFO，可选DEBUG，SUCCESS，ERROR，WARNING等
    logger.remove()
    logger.add(sys.stderr, level=_log_level)
    if _school_check:
        _school_list = list(
            filter(
                lambda line: not (line == ""),
                map(lambda line: line.rstrip("\n"), open("schoolList.txt", encoding="utf-8").readlines()),
            )
        )
    else:
        _school_list = list()
    query_resume()
