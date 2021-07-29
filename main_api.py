import os
import sys
import json
import logging
import ipaddress
import fastapi
import uvicorn
import psutil
from datetime import datetime
from typing import List, Dict, Any
from functools import lru_cache
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse


__DEBUG__ = os.getenv("JSON_DEBUG", 'False').lower() in ('true', '1', 't')
__ALLOW_DUPLICATE_TAGS__ = os.getenv("ALLOW_DUPLICATE_TAGS", 'False').lower() in ('true', '1', 't')
app: FastAPI = fastapi.FastAPI()
pid = os.getpid()

if __DEBUG__:
    logging.basicConfig(
        filename=os.getenv("JSON_LOGFILE", "nask.log"),
        filemode="a",
        level=logging.DEBUG,
    )
else:
    logging.basicConfig(
        filename=os.getenv("JSON_LOGFILE", "nask.log"), filemode="a", level=logging.INFO
    )
logging.log(
    logging.INFO,
    f"==[ START ]==\n     {datetime.now()} \n===============================",
)


def log_local(level: int, info: str) -> None:
    """

    :rtype: None
    """
    logging.log(level, f"{datetime.now()} -> {info}")


def read_database(json_file: str, encoding="utf-8") -> List[Dict[str, Any]]:
    """

    :rtype: list
    """
    try:
        with open(json_file, "r", encoding=encoding) as fin:
            readed_data = json.load(fin)
    except Exception as x:
        log_local(
            logging.ERROR,
            f"problem with file {json_file} - details: {x}",
        )
        print(f"ERROR with file {json_file} - details: {x} - exiting app.")
        sys.exit(1)

    log_local(
        logging.INFO,
        f"read database from {json_file} - {len(readed_data)} entries in file.",
    )
    data = []

    for idx, ip_tag in enumerate(readed_data):
        new_ip_tag = {
            "tag": ip_tag["tag"],
            "ip_network": ipaddress.ip_network(ip_tag["ip_network"]),
        }
        data.append(new_ip_tag)

    if __DEBUG__:
        log_local(logging.DEBUG, "Starting sorting JSON knowledgebase")
        sort_start: datetime = datetime.now()

    data.sort(key=lambda x: x["ip_network"])

    if __DEBUG__:
        log_local(
            logging.DEBUG,
            f"Time for sorting JSON knowledgebase: {datetime.now() - sort_start}",
        )
    del readed_data
    return data


if __DEBUG__:
    log_local(
        logging.DEBUG,
        f"Before JSON read RSS mem (mb): {psutil.Process(pid).memory_info()[0] / 1000000}",
    )
    log_local(logging.DEBUG, f"VIRT mem: {psutil.virtual_memory()}")


knowledgebase = read_database(os.getenv("JSON_DATABASE", "baza_wiedzy.json"))
database_info = {
    "total_entries": len(knowledgebase),
}

if __DEBUG__:
    log_local(
        logging.DEBUG,
        f"After JSON read RSS mem (mb): {psutil.Process(pid).memory_info()[0] / 1000000}",
    )
    log_local(logging.DEBUG, f"VIRT mem: {psutil.virtual_memory()}")


def binary_search(low: int, high: int, ip_net: object) -> int:
    """

    :rtype: int
    """
    if high >= low:
        mid = (high + low) // 2
        if ip_net.subnet_of(knowledgebase[mid]["ip_network"]):
            return mid
        elif knowledgebase[mid]["ip_network"] > ip_net:
            return binary_search(low, mid - 1, ip_net)
        else:
            return binary_search(mid + 1, high, ip_net)
    else:
        return -1


def build_tags_for(ip_net: object, database_slice: list) -> List:
    """

    :rtype: list
    """
    tags = []
    for net in database_slice:
        if ip_net.subnet_of(net["ip_network"]):
            if net["tag"] in tags and __ALLOW_DUPLICATE_TAGS__:
                tags.append(net["tag"])
            elif net["tag"] not in tags:
                tags.append(net["tag"])
    return tags


@lru_cache(maxsize=65535)
def build_tags_binary_search(ip_net: object) -> List:
    """

    :rtype: list
    """
    _min = 0
    _max = database_info["total_entries"] - 1

    # szukanie metodą bisekcji
    middle_time = datetime.now()
    middle = binary_search(_min, _max, ip_net)
    log_local(
        logging.INFO,
        f"Binary search: found index {middle} in {datetime.now() - middle_time}.",
    )
    if middle > 0:
        # potem wycinam z tego, co znajdę database_slice = xx[found -20 : found +20] (w dokumentacji zadania +/- 10)
        # więc robię to nadmarowo, i z takiej listy dopiero buduję listę tagów
        first = 0 if middle <= 20 else middle - 20
        last = (
            database_info["total_entries"]
            if middle + 20 > database_info["total_entries"]
            else middle + 20
        )
        if __DEBUG__:
            log_local(
                logging.DEBUG, f"first/last for build_tags_for search: {first} / {last}"
            )
        tags = build_tags_for(ip_net, knowledgebase[first:last])
    else:
        # ostatecznie zwracam putstą listę
        log_local(
            logging.INFO,
            f"Binary search not found.",
        )
        tags = []

    return tags


def build_tags_report(ip: str, tags: list) -> str:
    """

    :rtype: str
    """
    table_body = '<TABLE border="1">'
    table_body += "<TR><TH>Adres IP<TH>Pasujące tagi"
    if len(tags):
        html_tag = tags[0].replace("\n", "<br>")
        table_body += f'<TR><TD rowspan="{len(tags)}">{ip}<TD>{html_tag}'
        if len(tags) > 1:
            for tag in tags[1:]:
                html_tag = tag.replace("\n", "<br>")
                table_body += f"<TR><TD>{html_tag}"
    else:
        table_body += f'<TR><TD rowspan="{len(tags)}">{ip}<TD>&nbsp;'
    table_body += "</TABLE>"
    return table_body


@app.get("/")
def main_page():
    html_response = """
    <h2>NASK - REST service</h2><hr>
    /ip-tags/{ip} <br>
    /ip-tags-report/{ip}
    """
    return HTMLResponse(html_response)


@app.get("/ip-tags/{ip:str}", response_model=List)
async def ip_tags(ip: str):
    """Zwracany dokument reprezentuje listę napisów, zwaną dalej listą tagów."""
    try:
        ipv4: object = ipaddress.ip_network(ip)
    except Exception as x:
        log_local(logging.ERROR, f"bad ipv4 request format - details: {x}")
        raise HTTPException(status_code=400, detail=f"Oops! {x}")

    t_start = datetime.now()
    tags = build_tags_binary_search(ipv4)
    time_elapsed = datetime.now() - t_start
    log_local(logging.INFO, f"/ip-tags built for ipv4 {ip} - time: {time_elapsed}")
    if __DEBUG__:
        log_local(logging.DEBUG, f"tags = {tags}")
    if tags:
        return tags
    else:
        raise HTTPException(status_code=404, detail="IP not found in database.")


@app.get("/ip-tags-report/{ip:str}")
async def ip_tags_report(ip: str):
    """W odpowiedzi na żądanie klienta przesyłany jest dokument w formacie HTML, zwany dalej raportem."""
    try:
        ipv4: object = ipaddress.ip_network(ip)
    except Exception as x:
        log_local(logging.ERROR, f"bad ipv4 request format - details: {x}")
        raise HTTPException(status_code=400, detail=f"Oops! {x}")

    t_start = datetime.now()
    tags = build_tags_binary_search(ipv4)
    ret_html = build_tags_report(ip, tags)
    time_elapsed = datetime.now() - t_start
    log_local(
        logging.INFO, f"/ip-tags-report built for ipv4 {ip} - time: {time_elapsed}"
    )
    if __DEBUG__:
        log_local(logging.DEBUG, f"tags = {tags}")
    return HTMLResponse(ret_html)

@app.get("/status")
def status():
    """report some status"""
    return {
        "system": os.uname(),
        "python": f"{sys.version} - {sys.version_info}",
        "logfile": os.getenv("JSON_LOGFILE", "nask.log"),
        "knowledgebase": os.getenv("JSON_DATABASE", "baza_wiedzy.json"),
        "total_entries": len(knowledgebase),
        "__DEBUG__": __DEBUG__,
        "__ALLOW_DUPLICATE_TAGS__": __ALLOW_DUPLICATE_TAGS__,
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
