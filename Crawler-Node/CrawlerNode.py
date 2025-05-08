import requests
import json
import time
from urllib.parse import urlparse
from QueueUtils import receive_task, send_task

MAX_PAGES_PER_TASK = 100

class CrawlerNode:
    def __init__(self, input_queue, output_queue, max_pages_per_task=MAX_PAGES_PER_TASK):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.max_pages_per_task = max_pages_per_task
        self.visited_urls = set()
        self.pages_crawled = 0
        self.domain_url = None

    def fetch_url(self, url):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.text
            else:
                print(f"[Crawler] Failed to fetch {url}, Status Code: {response.status_code}")
                return None
        except Exception as e:
            print(f"[Crawler] Exception fetching {url}: {e}")
            return None

    def extract_endpoints(self, raw_html, base_url):
        endpoints = []
        lines = raw_html.splitlines()
        for line in lines:
            if 'href' in line:
                start = line.find('href="') + 6
                end = line.find('"', start)
                if end != -1 and start != 5:
                    endpoints.append(self.build_absolute_url(line[start:end], base_url))

                start = line.find("href='") + 6
                end = line.find("'", start)
                if end != -1 and start != 5:
                    endpoints.append(self.build_absolute_url(line[start:end], base_url))
            
            if 'src' in line:
                start = line.find('src="') + 5
                end = line.find('"', start)
                if end != -1 and start != 4:
                    endpoints.append(self.build_absolute_url(line[start:end], base_url))
                
                start = line.find("src='") + 5
                end = line.find("'", start)
                if end != -1 and start != 4:
                    endpoints.append(self.build_absolute_url(line[start:end], base_url))
        
        return list(set(endpoints))

    def build_absolute_url(self, link, base_url):
        if link.startswith("http"):
            return link
        elif link.startswith("/"):
            return self.domain_url.rstrip("/") + link
        else:
            return base_url.rstrip("/") + "/" + link
        
    
    def same_domain(self, base_url, new_url):
        try:
            base_domain = urlparse(base_url).netloc
            new_domain = urlparse(new_url).netloc
            return base_domain == new_domain
        except:
            return False


    def crawl_recursive(self, url, current_depth, max_depth):
        if current_depth > max_depth:
            return None

        if url in self.visited_urls:
            return None  # Already crawled

        if self.pages_crawled >= self.max_pages_per_task:
            print("[Crawler] Max pages limit reached.")
            return None

        raw_html = self.fetch_url(url)
        if not raw_html:
            return None

        self.visited_urls.add(url)
        self.pages_crawled += 1

        page = {
            "url": url,
            #"raw_html": "",
            "raw_html": raw_html, # Uncomment to include raw HTML in the output
            "children": []
        }

        if current_depth < max_depth:
            endpoints = self.extract_endpoints(raw_html, url)
            for endpoint in endpoints:
                if self.same_domain(self.domain_url, endpoint):
                    child_page = self.crawl_recursive(endpoint, current_depth + 1, max_depth)
                    if child_page:
                        page["children"].append(child_page)
                else:
                    print(f"[Crawler] Skipping external link: {endpoint}")


        return page

    def crawl_seed_url(self, seed_url, depth):
        """
        Starts recursive crawl from the seed URL
        """
        # Reset per task
        self.visited_urls = set()
        self.pages_crawled = 0

        o = urlparse(seed_url)
        self.domain_url = (o.scheme) + "://" + (o.netloc) + "/"

        print(f"[Crawler] URL Domain is {self.domain_url}")

        result_json = {
            "seed_url": seed_url,
            "pages": []
        }

        root_page = self.crawl_recursive(seed_url, current_depth=0, max_depth=depth)
        if root_page:
            result_json["pages"].append(root_page)

        return result_json

    def get_task(self):
        try:
            task = receive_task(self.input_queue)
            return task
        except:
            return None

    def send_result(self, result):
        send_task(self.output_queue, result)
        print("[Crawler] Result written to output queue.")

    def run(self):
        print("[Crawler] CrawlerNode started.")
        while True:
            task = self.get_task()
            if task:
                seed_url = task.get("seed_url")
                depth = task.get("depth", 1)
                print(f"[Crawler] Crawling seed URL: {seed_url} with depth: {depth}")
                result = self.crawl_seed_url(seed_url, depth)
                if result:
                    self.send_result(result)
            else:
                print("[Crawler] No task found. Sleeping...")
                time.sleep(5)

if __name__ == "__main__":
    input_queue = "crawler_input"
    output_queue = "crawler_result"
    crawler_node = CrawlerNode(input_queue, output_queue)
    crawler_node.run()
