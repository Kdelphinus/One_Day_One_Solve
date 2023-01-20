import requests
import csv
import datetime
import platform
from intra import ic
from slack_bot import SlackAPI

OS = platform.system()
if OS == "Darwin":
    PATH = "/Users/myko/one_day_one_solve/solved.csv"
elif OS == "Windows":
    PATH = "C:/Users/delphinus/Desktop/Workspace/solved.ac/solved.csv"
TODAY = (datetime.datetime.now() - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
URL = "https://solved.ac/api/v3/user/show"
HEADERS = {"Content-Type": "application/json"}
USERS = {"unsolved": [], "solved": [], "new_user": [], "none_user": []}
SLACK_TOKEN = "xoxb-4678080307476-4673512758069-9nnNeELf0zz91Y6JOn98zrzs"
TIER = [
    "🖤 newvi",
    "🤎 V",
    "🤎 IV",
    "🤎 III",
    "🤎 II",
    "🤎 I",
    "🤍 V",
    "🤍 IV",
    "🤍 III",
    "🤍 II",
    "🤍 I",
    "💛 V",
    "💛 IV",
    "💛 III",
    "💛 II",
    "💛 I",
    "💙 V",
    "💙 IV",
    "💙 III",
    "💙 II",
    "💙 I",
    "💎 V",
    "💎 IV",
    "💎 III",
    "💎 II",
    "💎 I",
    "💖 V",
    "💖 IV",
    "💖 III",
    "💖 II",
    "💖 I",
]


def atoi(num: str) -> int:
    """
    문제 푼 자릿수가 다 다르기에 넉넉하게 받고 숫자만 반환
    Args:
        num: 푼 문제의 수로 시작하는 문자열

    Returns:
        ans: 푼 문제의 수

    """
    ans = 0
    for n in num:
        if not n.isdigit():
            break
        ans = ans * 10 + int(n)
    return ans


def total_solve(user: str) -> list:
    """
    solved.ac api로 접근하여 푼 문제의 수를 가져오는 함수
    Args:
        user: 백준 아이디

    Returns:
        0 or 양수: 푼 문제의 수
        -1: 잘못된 아이디일 경우

    """
    querystring = {"handle": user}
    response = requests.request("GET", URL, headers=HEADERS, params=querystring)
    info = [float("inf"), float("inf")]
    if response.text == "Not Found":
        return info
    for r in response.text.split(",")[::-1]:
        values = r.split(":")
        if values[0][1:-1] == "solvedCount":
            info[0] = min(atoi(values[1]), info[0])
        elif values[0][1:-1] == "tier":
            info[1] = atoi(values[1])
    return info


def csv_read() -> list:
    """
    기존 csv의 내용을 읽고 갱신하는 함수

    Returns:
        tmp_lst: 새로 갱신할 내용을 저장한 리스트

    """
    tmp_lst = []
    with open(PATH, "r", encoding="utf-8") as f:
        rd = csv.reader(f)
        if not rd:
            return []
        for name, intra_id, baek_id, solve, update, flag, tier in rd:
            tmp = total_solve(baek_id)
            if tmp[0] == float("inf") and tmp[1] == float("inf"):
                tmp_lst.append([name, intra_id, baek_id, 0, TODAY, flag, 0])
                USERS["none_user"].append([name, intra_id])
                continue

            if update == TODAY and flag == "0":
                tmp_lst.append([name, intra_id, baek_id, tmp[0], TODAY, flag, tmp[1]])
                USERS["solved"].append([name, intra_id, int(tmp[1])])
                continue

            if str(tmp[0]) <= solve:
                if update == TODAY:
                    tmp_lst.append(
                        [name, intra_id, baek_id, tmp[0], TODAY, int(flag), tmp[1]]
                    )
                    USERS["unsolved"].append((name, intra_id, int(flag), int(tmp[1])))
                else:
                    tmp_lst.append(
                        [name, intra_id, baek_id, tmp[0], TODAY, int(flag) + 1, tmp[1]]
                    )
                    USERS["unsolved"].append(
                        (name, intra_id, int(flag) + 1, int(tmp[1]))
                    )
            else:
                tmp_lst.append([name, intra_id, baek_id, tmp[0], TODAY, 0, int(tmp[1])])
                USERS["solved"].append([name, intra_id, int(tmp[1])])
    return tmp_lst


def csv_write(tmp_lst: list, option: str):
    """
    csv 파일에 갱신한 데이터를 작성하는 함수
    Args:
        tmp_lst: 갱신된 데이터를 저장한 리스트
        option:
            a: 이어쓰기
            w: 기존 내용은 지우고 새로 쓰기

    """
    with open(PATH, option, newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(tmp_lst)


def get_location(intra_id: str) -> tuple:
    """
    위치와 출퇴근을 조사하는 함수
    Args:
        intra_id: 인트라 아이디

    Returns:
        위치와 출퇴근 여부를 반환
    """
    response = ic.get("users", params={"filter[login]": intra_id})
    loc = response.json()[0]["location"]
    date, time = response.json()[0]["updated_at"].split("T")
    date = list(map(int, date.split("-")))
    time = list(map(int, time[:-5].split(":")))
    last_time = datetime.datetime(date[0], date[1], date[2], time[0], time[1], 0)
    last_time += datetime.timedelta(hours=9)
    now_day = datetime.datetime.now() - datetime.timedelta(hours=6)
    now_day = datetime.datetime(now_day.year, now_day.month, now_day.day, 6, 0, 0, 0)
    cluster = 1 if last_time >= now_day else 0
    return (loc, cluster) if loc else ("null", cluster)


def print_name():
    """
    푼 사람, 안 푼 사람, 새로운 사람을 정리해서 출력하는 함수

    """
    text = ""
    text += f"⏰현재 시각: {datetime.datetime.now()}\n\n"
    if USERS["solved"]:
        text += "😀푼 사람😀\n"
    no_cluster = []
    for name, intra_id, tier in USERS["solved"]:
        loc, cluster = get_location(intra_id)
        if loc == "null":
            if cluster:
                no_cluster.append(f"- @{intra_id} ({name}) {TIER[tier]} \n(퇴근함)")
            else:
                no_cluster.append(f"- @{intra_id} ({name}) {TIER[tier]} \n(출근 안 함)")
        else:
            text += f"- @{intra_id} ({name}) {TIER[tier]} \n(현재 위치: {loc})\n"
    for s in no_cluster:
        text += s + "\n"

    if USERS["unsolved"]:
        text += "\n😢안 푼 사람😢\n"
    no_cluster = []
    for name, intra_id, day, tier in USERS["unsolved"]:
        loc, cluster = get_location(intra_id)
        if loc == "null":
            if cluster:
                text += (
                    f"- @{intra_id} ({name}) {TIER[tier]} \n({day}일 째 안 푸는 중, 퇴근함)\n"
                )
            else:
                no_cluster.append(
                    f"- @{intra_id} ({name}) {TIER[tier]} \n({day}일 째 안 푸는 중, 출근 안 함)"
                )
        else:
            text += f"- @{intra_id} ({name}) {TIER[tier]} \n({day}일 째 안 푸는 중, 현재 위치: {loc})\n"
    if no_cluster:
        text += "\n🙏백준도 안 풀고, 클러스터에도 없고🙏\n"
    for s in no_cluster:
        text += s + "\n"

    if USERS["none_user"]:
        text += "\n🙏solved.ac 동의 해주세요🙏\n"
    for name, intra_id in USERS["none_user"]:
        loc, cluster = get_location(intra_id)
        if loc == "null" and cluster == 0:
            if cluster:
                text += f"- @{intra_id} ({name})\n(퇴근함)\n"
            else:
                text += f"- @{intra_id} ({name})\n(출근 안 함)\n"
        else:
            text += f"- @{intra_id} ({name})\n(현재 위치: {loc})\n"
    text += "\n주의 사항: 출근은 새벽 6시 ~ 익일 새벽 5시 59분 사이 맥 로그인 기록으로 판단합니다.\n"
    return text


if __name__ == "__main__":
    lst = csv_read()
    csv_write(lst, "w")
    message = print_name()
    print(message)
    slack = SlackAPI(SLACK_TOKEN)
    slack.post_chat_message("독촉", message)
