import requests
from bs4 import BeautifulSoup

from scrapers.new_listing import new_listings
from scrapers.vacancies import get_vacancie
from scrapers.price_change import price_change


cookies = {
    'lang': 'uk',
    'deviceGUID': '94b61546-28dd-4783-9dec-c3f280091524',
    '_sharedid': '0f8b0513-bb8d-43dc-8cdd-fb3c810f39f8',
    '_sharedid_cst': 'zix7LPQsHA%3D%3D',
    '__gads': 'ID=baeb5b21b131be43:T=1764529511:RT=1764529511:S=ALNI_MZNxj0EYRMlDgghb4leE1Bnm7goMA',
    '__gpi': 'UID=000012955e4e6aa4:T=1764529511:RT=1764529511:S=ALNI_MazIOk65fllugZGSOZlcPCt5iablQ',
    '__eoi': 'ID=1da1d563d4ac06b3:T=1764529511:RT=1764529511:S=AA-AfjbXXCjPWL6MB9D9_axVVpXf',
    '__gsas': 'ID=1f2ef5f2a4539b7c:T=1765256404:RT=1765256404:S=ALNI_MbOm57OCf-gTWjQUPMvExzi9_3VKw',
    'cookieBarSeenV2': 'true',
    'cookieBarSeen': 'true',
    'PHPSESSID': 'o1oj87ijd53ctdbghufrp0oui6',
    'session_start_date': '1766747854973',
    '_legacy_a0.spajs.txs.309lsgh0deirlo2la9kmrmhe3v': '{%22nonce%22:%22NWFvSFpjbDBuTWo5RXI1cWt0anlCSlh0NkxEOEtYVGd4VFRBWXRhcnNyRw==%22%2C%22code_verifier%22:%22gYuSS22DUkmK0~Qm2xNG9HKHWelKkUPcwZ_DkmgBfFH%22%2C%22scope%22:%22openid%20profile%20email%20offline_access%22%2C%22audience%22:%22default%22%2C%22redirect_uri%22:%22https://www.olx.ua/d/uk/callback/%22%2C%22state%22:%22RzVCXzlnT3lYWjFpd2VUQmEtaF9tX29sLjNrT3llWmJ2MHljSEZyWC5BSg==%22%2C%22appState%22:{%22backUrl%22:%22/uk/myaccount%22%2C%22referer%22:%22%22}}',
    'a0.spajs.txs.309lsgh0deirlo2la9kmrmhe3v': '{%22nonce%22:%22NWFvSFpjbDBuTWo5RXI1cWt0anlCSlh0NkxEOEtYVGd4VFRBWXRhcnNyRw==%22%2C%22code_verifier%22:%22gYuSS22DUkmK0~Qm2xNG9HKHWelKkUPcwZ_DkmgBfFH%22%2C%22scope%22:%22openid%20profile%20email%20offline_access%22%2C%22audience%22:%22default%22%2C%22redirect_uri%22:%22https://www.olx.ua/d/uk/callback/%22%2C%22state%22:%22RzVCXzlnT3lYWjFpd2VUQmEtaF9tX29sLjNrT3llWmJ2MHljSEZyWC5BSg==%22%2C%22appState%22:{%22backUrl%22:%22/uk/myaccount%22%2C%22referer%22:%22%22}}',
    'datadome': 'jrLPBBGhiBrGJvlKhTMlUxNgdSYTehscxBGwuNJob_JW4fnPmrTpek_C59sOzELm4NK3~H4WJzhZWPzyyc0~kmmh4VcqPZPYqC2BCm4fnPlo6oeI5ZCRxKd2irmEtcGi',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'uk,ru;q=0.9,en-US;q=0.8,en;q=0.7,pl;q=0.6,fr;q=0.5,de;q=0.4',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.olx.ua/d/uk/obyavlenie/ayfon-10-v-garnomu-stan-IDYIXiR.html',
    'sec-ch-ua': '"Opera";v="125", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 OPR/125.0.0.0',
    # 'cookie': 'lang=uk; deviceGUID=94b61546-28dd-4783-9dec-c3f280091524; _sharedid=0f8b0513-bb8d-43dc-8cdd-fb3c810f39f8; _sharedid_cst=zix7LPQsHA%3D%3D; __gads=ID=baeb5b21b131be43:T=1764529511:RT=1764529511:S=ALNI_MZNxj0EYRMlDgghb4leE1Bnm7goMA; __gpi=UID=000012955e4e6aa4:T=1764529511:RT=1764529511:S=ALNI_MazIOk65fllugZGSOZlcPCt5iablQ; __eoi=ID=1da1d563d4ac06b3:T=1764529511:RT=1764529511:S=AA-AfjbXXCjPWL6MB9D9_axVVpXf; __gsas=ID=1f2ef5f2a4539b7c:T=1765256404:RT=1765256404:S=ALNI_MbOm57OCf-gTWjQUPMvExzi9_3VKw; cookieBarSeenV2=true; cookieBarSeen=true; PHPSESSID=o1oj87ijd53ctdbghufrp0oui6; session_start_date=1766747854973; _legacy_a0.spajs.txs.309lsgh0deirlo2la9kmrmhe3v={%22nonce%22:%22NWFvSFpjbDBuTWo5RXI1cWt0anlCSlh0NkxEOEtYVGd4VFRBWXRhcnNyRw==%22%2C%22code_verifier%22:%22gYuSS22DUkmK0~Qm2xNG9HKHWelKkUPcwZ_DkmgBfFH%22%2C%22scope%22:%22openid%20profile%20email%20offline_access%22%2C%22audience%22:%22default%22%2C%22redirect_uri%22:%22https://www.olx.ua/d/uk/callback/%22%2C%22state%22:%22RzVCXzlnT3lYWjFpd2VUQmEtaF9tX29sLjNrT3llWmJ2MHljSEZyWC5BSg==%22%2C%22appState%22:{%22backUrl%22:%22/uk/myaccount%22%2C%22referer%22:%22%22}}; a0.spajs.txs.309lsgh0deirlo2la9kmrmhe3v={%22nonce%22:%22NWFvSFpjbDBuTWo5RXI1cWt0anlCSlh0NkxEOEtYVGd4VFRBWXRhcnNyRw==%22%2C%22code_verifier%22:%22gYuSS22DUkmK0~Qm2xNG9HKHWelKkUPcwZ_DkmgBfFH%22%2C%22scope%22:%22openid%20profile%20email%20offline_access%22%2C%22audience%22:%22default%22%2C%22redirect_uri%22:%22https://www.olx.ua/d/uk/callback/%22%2C%22state%22:%22RzVCXzlnT3lYWjFpd2VUQmEtaF9tX29sLjNrT3llWmJ2MHljSEZyWC5BSg==%22%2C%22appState%22:{%22backUrl%22:%22/uk/myaccount%22%2C%22referer%22:%22%22}}; datadome=jrLPBBGhiBrGJvlKhTMlUxNgdSYTehscxBGwuNJob_JW4fnPmrTpek_C59sOzELm4NK3~H4WJzhZWPzyyc0~kmmh4VcqPZPYqC2BCm4fnPlo6oeI5ZCRxKd2irmEtcGi',
}


def get_soup(url):
    req = requests.get(url, cookies=cookies, headers=headers)
    soup = BeautifulSoup(req.text, "lxml")
    return soup


def get_new_listing(url):
    soup = get_soup(url)

    data = new_listings(soup, url)

    return data


def get_vacancies(url):
    soup = get_soup(url)

    data = get_vacancie(soup, url)

    return data


def get_price_change(url):
    soup = get_soup(url)

    data = price_change(soup, url)

    return data

    
