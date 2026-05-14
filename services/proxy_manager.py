import random

class ProxyManager:
    def __init__(self, proxy_list_file="proxies.txt"):
        with open(proxy_list_file, "r") as f:
            self.all_proxies = [line.strip() for line in f if line.strip()]
        self.active_proxies = self.all_proxies.copy()

    def get_proxy(self):
        if not self.active_proxies:
            self.active_proxies = self.all_proxies.copy()
        proxy = random.choice(self.active_proxies)
        return {"http": proxy, "https": proxy}

    def remove_proxy(self, proxy):
        try:
            self.active_proxies.remove(proxy["http"])
        except ValueError:
            pass