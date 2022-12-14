import requests
import csv
import datetime
import platform
from intra import ic

OS = platform.system()
if OS == "Darwin":
    PATH = "/Users/myko/one_day_one_solve/solved.csv"
elif OS == "Windows":
    PATH = "C:/Users/delphinus/Desktop/Workspace/solved.ac/solved.csv"
TODAY = (datetime.datetime.now() - datetime.timedelta(hours=6)).strftime("%Y-%m-%d")
URL = "https://solved.ac/api/v3/user/show"
HEADERS = {"Content-Type": "application/json"}
USERS = {"unsolved": [], "solved": [], "new_user": [], "none_user": []}
TIER = [
    "π€ newvi",
    "π€ V",
    "π€ IV",
    "π€ III",
    "π€ II",
    "π€ I",
    "π€ V",
    "π€ IV",
    "π€ III",
    "π€ II",
    "π€ I",
    "π V",
    "π IV",
    "π III",
    "π II",
    "π I",
    "π V",
    "π IV",
    "π III",
    "π II",
    "π I",
    "π V",
    "π IV",
    "π III",
    "π II",
    "π I",
    "π V",
    "π IV",
    "π III",
    "π II",
    "π I",
]


def atoi(num: str) -> int:
    """
    λ¬Έμ  νΌ μλ¦Ώμκ° λ€ λ€λ₯΄κΈ°μ λλνκ² λ°κ³  μ«μλ§ λ°ν
    Args:
        num: νΌ λ¬Έμ μ μλ‘ μμνλ λ¬Έμμ΄

    Returns:
        ans: νΌ λ¬Έμ μ μ

    """
    ans = 0
    for n in num:
        if not n.isdigit():
            break
        ans = ans * 10 + int(n)
    return ans


def total_solve(user: str) -> list:
    """
    solved.ac apiλ‘ μ κ·Όνμ¬ νΌ λ¬Έμ μ μλ₯Ό κ°μ Έμ€λ ν¨μ
    Args:
        user: λ°±μ€ μμ΄λ

    Returns:
        0 or μμ: νΌ λ¬Έμ μ μ
        -1: μλͺ»λ μμ΄λμΌ κ²½μ°

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
    κΈ°μ‘΄ csvμ λ΄μ©μ μ½κ³  κ°±μ νλ ν¨μ

    Returns:
        tmp_lst: μλ‘ κ°±μ ν  λ΄μ©μ μ μ₯ν λ¦¬μ€νΈ

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
    csv νμΌμ κ°±μ ν λ°μ΄ν°λ₯Ό μμ±νλ ν¨μ
    Args:
        tmp_lst: κ°±μ λ λ°μ΄ν°λ₯Ό μ μ₯ν λ¦¬μ€νΈ
        option:
            a: μ΄μ΄μ°κΈ°
            w: κΈ°μ‘΄ λ΄μ©μ μ§μ°κ³  μλ‘ μ°κΈ°

    """
    with open(PATH, option, newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(tmp_lst)


def get_location(intra_id: str) -> tuple:
    """
    μμΉμ μΆν΄κ·Όμ μ‘°μ¬νλ ν¨μ
    Args:
        intra_id: μΈνΈλΌ μμ΄λ

    Returns:
        μμΉμ μΆν΄κ·Ό μ¬λΆλ₯Ό λ°ν
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
    νΌ μ¬λ, μ νΌ μ¬λ, μλ‘μ΄ μ¬λμ μ λ¦¬ν΄μ μΆλ ₯νλ ν¨μ

    """
    print(f"β°νμ¬ μκ°: {datetime.datetime.now()}")
    print()
    if USERS["solved"]:
        print("πνΌ μ¬λπ")
    no_cluster = []
    for name, intra_id, tier in USERS["solved"]:
        loc, cluster = get_location(intra_id)
        if loc == "null":
            if cluster:
                no_cluster.append(f"- {intra_id}({name}) {TIER[tier]} \n(ν΄κ·Όν¨)")
            else:
                no_cluster.append(f"- {intra_id}({name}) {TIER[tier]} \n(μΆκ·Ό μ ν¨)")
        else:
            print(f"- {intra_id}({name}) {TIER[tier]} \n(νμ¬ μμΉ: {loc})")
    for s in no_cluster:
        print(s)

    if USERS["unsolved"]:
        print("\nπ’μ νΌ μ¬λπ’")
    no_cluster = []
    for name, intra_id, day, tier in USERS["unsolved"]:
        loc, cluster = get_location(intra_id)
        if loc == "null":
            if cluster:
                print(f"- {intra_id}({name}) {TIER[tier]} \n({day}μΌ μ§Έ μ νΈλ μ€, ν΄κ·Όν¨)")
            else:
                no_cluster.append(
                    f"- {intra_id}({name}) {TIER[tier]} \n({day}μΌ μ§Έ μ νΈλ μ€, μΆκ·Ό μ ν¨)"
                )
        else:
            print(
                f"- {intra_id}({name}) {TIER[tier]} \n({day}μΌ μ§Έ μ νΈλ μ€, νμ¬ μμΉ: {loc})"
            )
    if no_cluster:
        print("\nπλ°±μ€λ μ νκ³ , ν΄λ¬μ€ν°μλ μκ³ π")
    for s in no_cluster:
        print(s)

    if USERS["none_user"]:
        print("\nπsolved.ac λμ ν΄μ£ΌμΈμπ")
    for name, intra_id in USERS["none_user"]:
        loc, cluster = get_location(intra_id)
        if loc == "null" and cluster == 0:
            if cluster:
                print(f"- {intra_id}({name})\n(ν΄κ·Όν¨)")
            else:
                print(f"- {intra_id}({name})\n(μΆκ·Ό μ ν¨)")
        else:
            print(f"- {intra_id}({name})\n(νμ¬ μμΉ: {loc})")


if __name__ == "__main__":
    lst = csv_read()
    csv_write(lst, "w")
    print_name()
    print("\nμ£Όμ μ¬ν­: μΆκ·Όμ μλ²½ 6μ ~ μ΅μΌ μλ²½ 5μ 59λΆ μ¬μ΄ λ§₯ λ‘κ·ΈμΈ κΈ°λ‘μΌλ‘ νλ¨ν©λλ€.")
