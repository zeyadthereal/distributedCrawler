import json
import time
from QueueUtils import receive_task, send_task
from elasticsearch import Elasticsearch

class MasterNode:
    def __init__(self, input_queue, crawler_queue, crawler_result_queue, client_result, es):
        self.input_queue = input_queue
        self.crawler_queue = crawler_queue
        self.crawler_result_queue = crawler_result_queue
        self.client_result = client_result
        self.es = es

    def send_index(self, data):
        """
        Send data to the indexer (Elasticsearch).
        """
        response = self.es.index(index="crawler", document=data)
        
        if response['result'] in ["created", "updated"]:
            print(f"[Master] Indexed data Successfully")
            return True
        else:
            print(f"[Master] Failed to index data: {response}")
            return False

    def get_index(self, url):
        """
        Get data from the indexer (Elasticsearch).
        """
        query = {
            "query": {
                "term": {
                    "seed_url.keyword": url  # Use .keyword for exact match on strings
                }
            }
        }
        
        try:
            response = self.es.search(index="crawler", body=query)
            if response['hits']['total']['value'] > 0:
                print(f"[Master] Found URL in index: {url}")
                return response['hits']['hits'][0]['_source']
            else:
                print(f"[Master] URL not found in index: {url}")
                return None
        except Exception as e:
            print(f"[Master] Error fetching from index: {e}")
            return None

    def get_task_from_client(self):
        """
        Simulate pulling a crawl request from the client.
        After reading, delete the file to simulate queue pop.
        """
        try:
            task = receive_task(self.input_queue)
            return task
        except Exception as e:
            print(f"[Master] Failed to read or delete client task: {e}")
            return None

    def is_url_already_indexed(self, url):
        """
        Stub: Check if URL is already in the index.
        """
        print(f"[Master] Checking if {url} is already indexed...")
        if (self.get_index(url)):
            return True
        return False

    def send_to_crawler(self, task):
        """
        Send a crawl request to the CrawlerNode.
        """
        try:
            send_task(self.crawler_queue, task)
            print(f"[Master] Sent task to crawler.")
        except Exception as e:
            print(f"[Master] Failed to send to crawler: {e}")

    def receive_from_crawler(self):
        """
        Wait for crawler result from crawler_result_queue.
        Once read, delete the file.
        """
        try:
            result = receive_task(self.crawler_result_queue)
            return result
        except Exception as e:
            print(f"[Master] Failed to read or delete crawler result: {e}")
            return None

    def send_to_client(self, result):
        """
        Send the crawl result to ClientNode.
        """
        try:
            send_task(self.client_result, result)
            print(f"[Master] Sent result to client.")
        except Exception as e:
            print(f"[Master] Failed to send to client: {e}")

    def run(self):
        print("MasterNode started.")
        while True:
            task = self.get_task_from_client()
            if task:
                seed_url = task.get("seed_url")
                depth = task.get("depth", 1)
                print(f"[Master] Received task for {seed_url} with depth {depth}")

                if self.is_url_already_indexed(seed_url):
                    print(f"[Master] URL already indexed. Skipping crawl.")
                    result = self.get_index(seed_url)
                    self.send_to_client(result)
                    continue

                self.send_to_crawler(task)
                
            result = self.receive_from_crawler()
            if result:
                print(f"[Master] Received crawl result. Forwarding to client.")
                self.send_to_client(result)
                self.send_index(result)
            
            if not result and not task:
                print("[Master] No tasks in queues. Sleeping...")
                time.sleep(5)

            

if __name__ == "__main__":
    es = Elasticsearch(
        "https://34.59.196.141:9200", 
        basic_auth=("elastic", "=v_ZV=-fo0KPW*nMm62V"),
        verify_certs=False
    )

    master = MasterNode(
        input_queue="client_task",
        crawler_queue="crawler_input",
        crawler_result_queue="crawler_result",
        client_result="client_result",
        es=es
    )
    master.run()
