import requests
from bs4 import BeautifulSoup

URL = "https://fr.wikipedia.org/wiki/Le_Mans"
USER_AGENT = "ENSIM-BI-course-TD (educational)"

def robots_allows(url, user_agent="*"):
    # rp.read() uses urllib, which follows HTTP(S)_PROXY: behind an institutional
    # proxy it can silently default to "disallow everything". Fetching robots.txt
    # with requests and passing it to rp.parse() avoids that silent failure.
    import urllib.robotparser
    resp = requests.get("https://fr.wikipedia.org/robots.txt",
                        proxies={"http": None, "https": None},
                        headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(resp.text.splitlines())
    return rp.can_fetch(user_agent, url)

def main():
    allowed = robots_allows(URL)
    print(f"robots.txt allows fetching {URL}: {allowed}")
    if not allowed:
        raise SystemExit("robots.txt disallows this -- stopping, not scraping anyway.")

    resp = requests.get(URL, proxies={"http": None, "https": None},
                        headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.find("h1").get_text(strip=True)

    first_para = None
    for p in soup.find_all("p"):
        # Skip disambiguation notices (Wikipedia "hatnote" class).
        if p.find_parent(class_="hatnote"):
            continue
        text = p.get_text(strip=True)
        if len(text) > 40:
            first_para = text
            break

    print(f"\nPage title: {title}")
    print(f"First real paragraph ({len(first_para)} chars): {first_para[:200]}...")

    # One measurable variable extracted from unstructured HTML: population from
    # the infobox, found by label text rather than a fragile CSS position.
    population = None
    for row in soup.select("table.infobox_v2 tr, table.infobox tr"):
        header = row.find("th")
        if header and "population" in header.get_text(strip=True).lower():
            cell = row.find("td")
            if cell:
                population = cell.get_text(" ", strip=True)
                break
    print(f"Extracted population field (unstructured -> one variable): {population!r}")

if __name__ == "__main__":
    main()
