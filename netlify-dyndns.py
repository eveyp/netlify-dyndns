import json
import requests

netlify_api_url_stem = "https://api.netlify.com/api/v1/dns_zones/"


def get_config():
    return(json.load(open("config.json")))


auth_header = {'Authorization': "Bearer " + get_config()["api_key"]}


def get_record_id():
    response = requests.get(
        url=netlify_api_url_stem + get_config()["zone_id"] + "/dns_records",
        headers=auth_header
    ).json()

    record = list(filter(lambda x: x['hostname']
                         == "home.eveperry.com", response))

    if len(record) == 0:
        return None

    return record[0]['id']


def delete_record(record):
    requests.delete(
        url=netlify_api_url_stem +
        get_config()["zone_id"] + "/dns_records/" + record,
        headers=auth_header
    )


def get_external_ip():
    return(requests.get("https://api.ipify.org/").text)


def create_record():
    requests.post(
        url=netlify_api_url_stem + get_config()["zone_id"] + "/dns_records",
        headers=auth_header,
        json={
            "type": "A",
            "hostname": get_config()["url"],
            "value": get_external_ip(),
            "ttl": 3600
        }
    )


def get_current_record_ip():
    record_id = get_record_id()

    if record_id is None:
        return None

    return(
        requests.get(
            url=netlify_api_url_stem +
            get_config()["zone_id"] + "/dns_records/" + record_id,
            headers=auth_header
        ).json()["value"]
    )


def check_ip():
    current_record_ip = get_current_record_ip()

    if current_record_ip is None:
        create_record()
    elif get_external_ip() != current_record_ip:
        delete_record(get_record_id())
        create_record()


check_ip()
