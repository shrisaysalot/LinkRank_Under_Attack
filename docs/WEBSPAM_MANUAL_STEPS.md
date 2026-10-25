# WEBSPAM-UK2006 Host Graph Manual Ingestion Guide

**Group 16:** LinkRank Under Attack  
**Date:** 25 October 2026  
**Status:** Instruction manual and download guide for host graph extraction  

---

## 1. Overview and Files Breakdown

The **WEBSPAM-UK2006** benchmark consists of two distinct data layers:
1. **Host-Level Human/Domain Labels (Downloaded & Verified):**
   - Downloaded to `data/raw/webspam-uk2006-2.0.tar.gz` (153 KB).
   - Extracted to `data/raw/webspam-uk2006-2.0/`.
   - Verified label counts:
     - **Set 1 (`webspam-uk2006-set1-labels.txt`):** 8,415 total hosts (7,472 normal, 767 spam, 176 undecided).
     - **Set 2 (`webspam-uk2006-set2-labels.txt`):** 2,247 total hosts (651 normal, 1,346 spam, 250 undecided).
     - **Domain / Two Humans Sets (`DomainOrTwoHumans.txt`):** Set 1: 5,622 hosts (4,948 normal, 674 spam); Set 2: 1,851 hosts (601 normal, 1,250 spam).

2. **Host Link Graph (Pending Ingestion):**
   - The host graph contains **11,402 nodes (web hosts)** and represents page hyperlinks aggregated at the host domain level (~1.9 MB in plain text).
   - The graph bitstream is stored in WebGraph Boldi-Vigna compressed format (`.graph` and `.properties`).

---

## 2. Official Definition of "Undecided"

From the official dataset release README (`data/raw/webspam-uk2006-2.0/README.txt`):

> "The spamicity measure is calculated by assigning 1 point for each 'spam' (S) judgment, 0.5 points for each 'borderline' (B) judgment, and 0 points for each 'normal' (N) judgment, and taking the average. The 'can not judge' (?) marks are ignored for this calculation.
>
> The label for a host with an average of over 0.5 is spam, for a host with an average of less than 0.5 is normal, and for a host with exactly 0.5 is undecided."

In our codebase ([`src/data/loader.py`](../src/data/loader.py)), undecided hosts are excluded by default (`undecided_mode="exclude"`), with configurable options for conservative (`"spam"`), lenient (`"normal"`), or ternary (`"keep"`) evaluation.

---

## 3. Step-by-Step Manual Download & Extraction Steps

### Step 1: Download WebGraph Java Binaries
Download the WebGraph runtime JARs from the [Laboratory for Web Algorithmics (LAW)](https://law.di.unimi.it/software.php):
- `webgraph-3.6.12.jar` (or latest)
- `fastutil-8.5.12.jar`
- `dsiutils-2.7.3.jar`
- `jsap-2.1.jar`
- `slf4j-api-2.0.7.jar` and `slf4j-simple-2.0.7.jar`

Place these JAR files in a directory, e.g. `tools/webgraph/`.

### Step 2: Download Host Graph Bitstream
From the LAW DELIS `.uk` repository (`https://law.di.unimi.it/webdata/uk-2006-05/` or the Web Spam Challenge archive):
- `uk-2006-05.host.graph`
- `uk-2006-05.host.properties`
- `uk-2006-05.host.nodes` (hostnames mapping file, 11,402 lines)

Place them in `data/raw/webspam-uk2006-hostgraph/`.

### Step 3: Extract BVGraph to ASCII Edge List
Run the WebGraph Java ASCII export tool:
```bash
java -cp "tools/webgraph/*" it.unimi.dsi.webgraph.ArcListASCIIGraph \
  data/raw/webspam-uk2006-hostgraph/uk-2006-05.host \
  data/raw/webspam-uk2006-hostgraph/uk-2006-05.host.edges.txt
```
This produces a whitespace-separated ASCII edge list:
```text
source_host_id destination_host_id
...
```

### Step 4: Python Ingestion & Evaluation
Once `uk-2006-05.host.edges.txt` and `uk-2006-05.host.nodes` are present:
1. Load the host edge list using NetworkX:
   ```python
   import networkx as nx
   G_host = nx.read_edgelist("data/raw/webspam-uk2006-hostgraph/uk-2006-05.host.edges.txt", create_using=nx.DiGraph, nodetype=int)
   ```
2. Map host IDs to hostnames via `uk-2006-05.host.nodes`.
3. Join with ground truth labels loaded via `load_webspam_labels("set1")` and `load_webspam_labels("set2")`.
4. Run HITS, PageRank, SALSA, and In-Degree rankers to compute Spam@k ($k \in \{10, 20, 50, 100\}$) and ROC-AUC.
