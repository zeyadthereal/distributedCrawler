# 🌐 Distributed Web Crawling and Indexing System

This project is a **cloud-native distributed web crawler and indexing system**, designed to efficiently crawl websites starting from seed URLs, extract and store raw HTML content hierarchically, and build a searchable index using Elasticsearch.

The architecture is modular, scalable, and fault-tolerant — built using **Python**, **Flask**, **Docker**, and **Kubernetes**, and integrated with **Elasticsearch** and **Kibana** for indexing and visualization.

---

## 🚀 Project Overview

This system allows users to:
- Submit one or more seed URLs to start a crawl
- Automatically distribute crawling tasks across multiple worker pods
- Extract and store HTML content hierarchically under each seed
- Index content into Elasticsearch for full-text search
- Visualize indexed data using Kibana
- Deploy and scale effortlessly via Kubernetes

All application components are already **containerized** and available on **Docker Hub** — only the Kubernetes manifests are needed for deployment.

---

## 🧱 System Components

### 🔹 Client Node (`Client-Node`)
- Flask-based web interface
- Provides endpoints to submit crawl requests and monitor system status

### 🔹 Master Node (`Master-Node`)
- Coordinates task distribution to crawlers
- Monitors crawler status and reassigns failed tasks
- Sends crawled content to the indexer

### 🔹 Crawler Nodes (`Crawler-Node`)
- Python-based workers
- Fetch URLs, extract links and raw HTML
- Communicate results to the master and indexer

### 🔹 Indexing & Search
- **Elasticsearch**: Stores structured crawl data
- **Kibana**: Visualizes and searches indexed content

### 🔹 Kubernetes Specifications (`k8s-specifications`)
- All Kubernetes manifests for deploying the system (Deployments, Services, etc.)

---

## 🧰 Technology Stack

| Layer                | Technology            |
|----------------------|------------------------|
| Crawling and parsing | Python                 |
| Web Interface        | Flask                  |
| Indexing Engine      | Elasticsearch          |
| Visualization        | Kibana                 |
| Containerization     | Docker                 |
| Orchestration        | Kubernetes (GKE) |

---

## 📦 Project Structure

```bash
.
├── Client-Node/            # Flask app (client interface)
├── Master-Node/            # Master node code (scheduler/controller)
├── Crawler-Node/           # Distributed web crawlers
└── k8s-specifications/     # All Kubernetes deployment YAMLs
```

## 📄 Deployment Guide

  ### 🔹 Create A Kubernetes Cluster in GCP
  - Go to Kubernetes Engine
  - Click on Create
  - Apply the desired configurations for your K8s cluster
  - Wait for the nodes to spawn
  
  ### 🔹 Access Kubectl to Control the Node Pool
  - Spawn your google cloud shell
  - Enter the following command
  ```bash
  gcloud container clusters get-credentials <YOUR_CLUSTER_NAME> --zone <YOUR_ZONE> --project <YOUR_PROJECT_NAME>
  ```
  ### 🔹 Clone The Repository
    
  ```bash
    git clone https://github.com/zeyadthereal/distributedCrawler.git
    cd distributed-crawler/k8s-specifications
  ```
  ### 🔹 Deploy The Pods
  ```bash
    kubectl create -f MANIFEST_FILE_NAME.yaml
  ```
  ### 🔹 Visualize The Deployments
  ```bash
    kubectl get pods -o wide
  ```
  
  ## 👨‍💻 Client Interface
  ### 🔹 Access The Interface
  - You have to know the IP address on which your client is hosted
  ```bash
      kubectl get pods,svc
  ```
  - Type The IP address followed by port 5000 in the browser's search bar
  
  
  ## 🔐 Indexer And Database
  ### 🔹 To Access The Database
  - You have to know the IP address on which elasticsearch is hosted
  - Type The IP address followed by port 9200 in the browser's search bar
  ```bash
    kubectl get pods,svc
  ```
      
  ### 🔹 To Access the GUI of The Database
  - You have to know the IP address on which elasticsearch is hosted
  - Type The IP address followed by port 5601 in the browser's search bar
 
