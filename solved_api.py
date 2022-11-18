import requests
import csv
import datetime

PATH = "solved.csv"
TODAY = (datetime.datetime.now() - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
URL = "https://solved.ac/api/v3/user/show"
HEADERS = {"Content-Type": "application/json"}
USERS = {"unsolved": [], "solved": [], "new_user": []}


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


def total_solve(user: str) -> int:
    """
    solved.ac api로 접근하여 푼 문제의 수를 가져오는 함수
    Args:
        user: 백준 intra_id

    Returns:
        0 or 양수: 푼 문제의 수
        -1: 잘못된 intra_id일 경우

    """
    querystring = {"handle": user}
    response = requests.request("GET", URL, headers=HEADERS, params=querystring)
    if response.text == "Not Found":
        return -1
    for r in response.text.split(",")[::-1]:
        values = r.split(":")
        if values[0][1:-1] == "solvedCount":
            return atoi(values[1])


def csv_read() -> list:
    """
    기존 csv의 내용을 읽고 갱신하는 함수

    Returns:
        tmp_lst: 새로 갱신할 내용을 저장한 리스트

    """
    tmp_lst = []
    with open(PATH, "r") as f:
        rd = csv.reader(f)
        if not rd:
            return []
        for intra_id, name, solve, update, flag in rd:
            if update == TODAY and flag == "1":
                tmp_lst.append([intra_id, name, solve, TODAY, 1])
                USERS["solved"].append(intra_id)
                continue

            tmp = total_solve(name)
            if str(tmp) == solve:
                tmp_lst.append([intra_id, name, tmp, TODAY, 0])
                USERS["unsolved"].append(intra_id)
            else:
                tmp_lst.append([intra_id, name, tmp, TODAY, 1])
                USERS["solved"].append(intra_id)
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
    with open(PATH, option, newline="") as f:
        wr = csv.writer(f)
        wr.writerows(tmp_lst)


def add_new_user():
    """
    새로운 인원이 있는지 확인하고 추가하는 함수

    """
    print("새로운 인원이 있습니까?(y/n)")
    while True:
        tmp = input()
        if tmp == "n":
            return
        elif tmp == "y":
            break
        else:
            print("y, n 중 하나로 입력하세요")

    print("새로운 유저의 백준 아이디를 입력하세요.")
    print("enter로 아이디를 구분하고 입력이 끝났으면 0을 입력하세요.")
    new_users = []
    while True:
        name = input()
        if name == "0":
            break
        tmp = total_solve(name)
        if tmp != -1:
            print(f"{name}의 인트라 아이디를 입력하세요.")
            intra_id = input()
            new_users.append([intra_id, name, total_solve(name), TODAY, 1])
            USERS["new_user"].append(intra_id)
        else:
            print("잘못된 아이디입니다. 다시 입력해주세요.")
    csv_write(new_users, "a")


def print_name():
    """
    푼 사람, 안 푼 사람, 새로운 사람을 정리해서 출력하는 함수

    """
    print(f"현재 시각: {datetime.datetime.now()}")
    print("😀푼 사람😀")
    for name in USERS["solved"]:
        print(f"@{name}")
    print("\n😡안 푼 사람😡")
    for name in USERS["unsolved"]:
        print(f"@{name}")
    if USERS["new_user"]:
        print("\n🥳새로운 사람🥳")
        for name in USERS["new_user"]:
            print(f"@{name}")


if __name__ == "__main__":
    lst = csv_read()
    csv_write(lst, "w")
    add_new_user()
    print_name()
    print("\n끝내시려면 enter를 누르세요.")
    input()
