from selenium import webdriver


class ProxyUtils:

    @staticmethod
    def _get_browser_with_proxy(proxy_ip):
        import os
        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True

        myProxy = proxy_ip
        firefox_capabilities['proxy'] = {
            'proxyType': "MANUAL",
            'httpProxy': myProxy,
            'ftpProxy': myProxy,
            'sslProxy': myProxy,
        }
        gecko_path = os.path.join('.','bin','geckodriver')
        browser = webdriver.Firefox(executable_path=gecko_path, capabilities=firefox_capabilities)
        return browser

    @staticmethod
    def get_whatsmyip_page_data(browser):
        browser.get('https://www.whatsmyip.org')
        browser_ip = browser.find_element_by_tag_name('h1').text
        browser_ip = browser_ip.replace("Your IP Address is ","")
        return browser_ip

    @staticmethod
    def dynamic_ip_change(browser, proxy_ip_port):
        from selenium.webdriver.support.wait import WebDriverWait
        browser.get("about:config")

        proxy_ip, proxy_port = proxy_ip_port.split(':')
        script = """
        var prefs = Components.classes["@mozilla.org/preferences-service;1"]
        .getService(Components.interfaces.nsIPrefBranch);

        prefs.setIntPref("network.proxy.type", 1);
        prefs.setCharPref("network.proxy.http", "{0}");
        prefs.setIntPref("network.proxy.http_port", "{1}");
        prefs.setCharPref("network.proxy.ssl", "{0}");
        prefs.setIntPref("network.proxy.ssl_port", "{1}");
        prefs.setCharPref("network.proxy.ftp", "{0}");
        prefs.setIntPref("network.proxy.ftp_port", "{1}");
        """

        browser.execute_script(script.format(proxy_ip, proxy_port))
        browser.wait = WebDriverWait(browser, 30)


class ProxyManager:
    proxy_list = [
        '69.30.240.226:15002',
        '69.30.197.122:15002',
        '142.54.177.226:15002',
        '198.204.228.234:15002',
        '195.154.255.118:15002',
        '195.154.222.228:15002',
        '195.154.255.34:15002',
        '195.154.222.26:15002'
    ]

    def __init__(self, proxy_list=None):
        self.proxy_idx = 0
        if proxy_list:
            self.proxy_list = proxy_list

    def get_next_proxy(self):
        from random import randint
        next_proxy = self.proxy_list[randint(0, len(self.proxy_list))]
        # next_proxy = self.proxy_list[self.proxy_idx % 5]
        self.proxy_idx += 1
        return next_proxy
