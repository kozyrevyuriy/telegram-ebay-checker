import requests
from bs4 import BeautifulSoup
from services.proxy_manager import ProxyManager

proxy_manager = ProxyManager()

def parse_ebay_item(item_id):
    url = f"https://www.ebay.com/itm/{item_id}"
    for _ in range(len(proxy_manager.active_proxies)):
        proxy = proxy_manager.get_proxy()
        try:
            response = requests.get(url, proxies=proxy, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.find("h1", id="itemTitle")
            title = title.text.replace("Details about  ", "").strip() if title else "N/A"

            price = soup.find("span", id="prcIsum") or soup.find("span", id="mm-saleDscPrc")
            price = price.text.strip() if price else "N/A"

            availability = soup.find("span", id="qtySubTxt")
            availability = availability.text.strip() if availability else "N/A"

            return {"title": title, "price": price, "availability": availability}

        except Exception:
            proxy_manager.remove_proxy(proxy)
            continue

    return {"title": "N/A", "price": "N/A", "availability": "N/A"}