"""Build script for Mid-Project Progress Report PDF (Group 16).

Compiles HTML/CSS source into a strictly 4-page PDF using headless Chrome/Edge,
renders each page to PNG for automated visual inspection, and validates page budget.
"""
import subprocess
import sys
import shutil
from pathlib import Path
import fitz  # PyMuPDF

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = REPO_ROOT / "report"
OUTPUT_PDF = REPORT_DIR / "16_LinkRankUnderAttack.pdf"
ROOT_PDF = REPO_ROOT / "16_LinkRankUnderAttack.pdf"
HTML_SOURCE = REPORT_DIR / "report.html"

# Verify browser executable
CHROME_PATHS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]


def get_browser_path():
    for p in CHROME_PATHS:
        if p.exists():
            return str(p)
    raise RuntimeError("Neither Google Chrome nor Microsoft Edge was found at standard paths.")


def generate_html_source():
    # Load image paths as file URIs
    arch_img = (REPO_ROOT / "figures" / "architecture.png").as_uri()
    h2_img = (REPO_ROOT / "figures" / "h2_spectral_takeover.png").as_uri()

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LinkRank Under Attack: Adversarial Robustness of HITS - Mid-Project Report</title>
<style>
  @page {
    size: A4 portrait;
    margin: 18mm;
    @bottom-right {
      content: "Page " counter(page) " of " counter(pages);
      font-size: 8pt;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      color: #718096;
    }
  }

  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 8.5pt;
    line-height: 1.22;
    color: #2D3748;
    margin: 0;
    padding: 0;
  }

  .page {
    height: 261mm;
    max-height: 261mm;
    overflow: hidden;
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
  }

  .page:last-child {
    page-break-after: avoid;
  }

  /* Typography */
  h1 {
    font-size: 13pt;
    font-weight: 800;
    color: #1A365D;
    margin: 0 0 2px 0;
    line-height: 1.15;
    letter-spacing: -0.2px;
  }

  .subtitle {
    font-size: 8.8pt;
    color: #4A5568;
    font-weight: 600;
    margin-bottom: 3px;
  }

  .meta-bar {
    background-color: #EDF2F7;
    border-left: 3px solid #2B6CB0;
    padding: 3px 6px;
    font-size: 8pt;
    color: #2D3748;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
  }

  .meta-bar span {
    margin-right: 8px;
  }

  h2 {
    font-size: 9.8pt;
    font-weight: 700;
    color: #2B6CB0;
    margin: 5px 0 2.5px 0;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 1.5px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }

  h3 {
    font-size: 8.5pt;
    font-weight: 700;
    color: #2D3748;
    margin: 3.5px 0 2px 0;
  }

  p {
    margin: 0 0 3.5px 0;
    text-align: justify;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 7.0pt;
    margin-bottom: 4px;
    line-height: 1.12;
  }

  th, td {
    border: 0.5px solid #CBD5E0;
    padding: 1.8px 3.2px;
    text-align: left;
  }

  th {
    background-color: #F7FAFC;
    color: #1A202C;
    font-weight: 700;
    border-bottom: 1px solid #A0AEC0;
  }

  tr:nth-child(even) {
    background-color: #F8FAFC;
  }

  .text-center { text-align: center; }
  .text-right { text-align: right; }
  .font-mono { font-family: SFMono-Regular, Menlo, Monaco, Consolas, monospace; }

  /* Badges */
  .badge {
    display: inline-block;
    padding: 1px 3.5px;
    font-size: 6.5pt;
    font-weight: 700;
    border-radius: 2px;
  }
  .badge-done { background-color: #C6F6D5; color: #22543D; }
  .badge-partial { background-color: #FEFCBF; color: #744210; }
  .badge-notstarted { background-color: #FED7D7; color: #742A2A; }

  /* Layout helpers */
  .row {
    display: flex;
    gap: 7px;
    margin-bottom: 3px;
  }
  .col-6 { flex: 1; }
  .col-7 { flex: 1.35; }
  .col-5 { flex: 1; }

  .figure-box {
    text-align: center;
    margin: 1px 0 3px 0;
  }

  .figure-box img {
    max-width: 100%;
    height: auto;
    border: 0.5px solid #E2E8F0;
    border-radius: 2px;
  }

  .caption {
    font-size: 6.8pt;
    color: #4A5568;
    margin-top: 1px;
    font-style: italic;
  }

  .highlight-box {
    background-color: #F7FAFC;
    border-left: 2.5px solid #4299E1;
    padding: 2.5px 5px;
    font-size: 7.4pt;
    margin-bottom: 3.5px;
    line-height: 1.18;
  }

  ul {
    margin: 0 0 3px 0;
    padding-left: 13px;
  }
  li {
    margin-bottom: 1px;
  }
</style>
</head>
<body>

<!-- ============================================================== -->
<!-- PAGE 1: HEADER, IMPLEMENTATION STATUS, ARCHITECTURE, IR PIPELINE -->
<!-- ============================================================== -->
<div class="page">
  <div style="border-bottom: 2px solid #1A365D; padding-bottom: 3px; margin-bottom: 4px;">
    <h1>LinkRank Under Attack: Adversarial Robustness of HITS</h1>
    <div class="subtitle">Information Retrieval (IR) Course &mdash; Mid-Project Progress Update (75&ndash;80% Milestone)</div>
    <div class="meta-bar">
      <span><strong>Group:</strong> 16</span>
      <span><strong>Members:</strong> Shrisay Shandilya, Vibhor Rathi, Prachi Jain</span>
      <span><strong>Date:</strong> 25 Oct 2026 (Final Planned: 15 Nov 2026)</span>
      <span><strong>Repo:</strong> <a href="https://github.com/shrisaysalot/LinkRank_Under_Attack" style="color:#2B6CB0; text-decoration:none;">github.com/shrisaysalot/LinkRank_Under_Attack</a></span>
    </div>
  </div>

  <h2>1. Executive Summary & Problem Scope</h2>
  <p>
    Hyperlink-Induced Topic Search (HITS) identifies authoritative web resources by computing dominant eigenvectors of <i>A</i><sup>T</sup><i>A</i> (authority) and <i>A</i><i>A</i><sup>T</sup> (hub). Unlike PageRank, which incorporates uniform teleportation (&alpha; = 0.85) to diffuse random walk probability mass globally, Kleinberg's mutual reinforcement model exhibits acute sensitivity to adversarial link manipulation. This study provides an empirical benchmark evaluating HITS vulnerability across 6 threat topologies (A1&ndash;A6) and assesses 5 algorithmic defense families (D1&ndash;D5) against PageRank, SALSA, and In-Degree baselines on synthetic topologies and SNAP web graphs.
  </p>

  <h2>2. Implementation Status & Architecture</h2>
  <div class="row">
    <div class="col-7">
      <table>
        <thead>
          <tr>
            <th style="width: 25%;">Module Category</th>
            <th style="width: 33%;">Component / Specifications</th>
            <th style="width: 14%;">Status</th>
            <th style="width: 28%;">Test / Verification Note</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Core Rankers</strong></td>
            <td>Sparse HITS, PageRank, SALSA, In-Degree</td>
            <td><span class="badge badge-done">DONE</span></td>
            <td>Power iter. verified vs NetworkX (tol &le; 10<sup>&minus;8</sup>)</td>
          </tr>
          <tr>
            <td><strong>Ranker Defenses (D1)</strong></td>
            <td>Randomized HITS (&epsilon;=0.15), Subspace HITS (<i>k</i>=5)</td>
            <td><span class="badge badge-done">DONE</span></td>
            <td>Verified in <code>test_rankers.py</code></td>
          </tr>
          <tr>
            <td><strong>SNAP Loaders</strong></td>
            <td>wiki-Vote, web-Stanford, web-NotreDame</td>
            <td><span class="badge badge-done">DONE</span></td>
            <td>Edge-list re-indexer, header parsing, self-loops</td>
          </tr>
          <tr>
            <td><strong>WEBSPAM Labels</strong></td>
            <td>UK-2006 Set 1 & Set 2 (8,415 labeled hosts)</td>
            <td><span class="badge badge-done">DONE</span></td>
            <td>Explicit undecided (176 hosts) filtering</td>
          </tr>
          <tr>
            <td><strong>WEBSPAM Host Graph</strong></td>
            <td>UK-2006 host link graph bitstream ingestion</td>
            <td><span class="badge badge-partial">PARTIAL</span></td>
            <td>Labels parsed; BVGraph bitstream pending Java run</td>
          </tr>
          <tr>
            <td><strong>Synthetic & Base-Set</strong></td>
            <td>BA (<i>m</i>=3,4), ER, Planted SBM; Kleinberg expansion</td>
            <td><span class="badge badge-done">DONE</span></td>
            <td>Root sampling (|<i>R</i>|&approx;100&ndash;200), in-link cap &le; 50</td>
          </tr>
          <tr>
            <td><strong>Attacks (A1&ndash;A3)</strong></td>
            <td>A1 Single Hub, A2 Hub Farm, A3 Bipartite Block</td>
            <td><span class="badge badge-done">DONE</span></td>
            <td>Edge budget strictly enforced (&le; <i>B</i> edges)</td>
          </tr>
          <tr>
            <td><strong>Attacks (A4&ndash;A6)</strong></td>
            <td>A4 Proposal Inflation, A4b Multi, A5 Cross, A5b, A6</td>
            <td><span class="badge badge-done">DONE</span></td>
            <td>A6 uses greedy gradient &part;&sigma;<sub>1</sub> / &part;<i>A</i><sub>ij</sub> = <i>h</i><sub>i</sub> <i>a</i><sub>j</sub></td>
          </tr>
          <tr>
            <td><strong>Defenses (D2&ndash;D5)</strong></td>
            <td>D2 Bharat-Henzinger (1/<i>k</i>), D3 Cap, D4/D4b Wu-Davison, D5 Trust</td>
            <td><span class="badge badge-done">DONE</span></td>
            <td>D3 verified no-op; D4 mutual & D4b out-Jaccard</td>
          </tr>
          <tr>
            <td><strong>Evaluation & Stats</strong></td>
            <td>Norm. rank gain, <i>B</i>*(<i>k</i>), Top-10, NDCG, Jaccard, CIs</td>
            <td><span class="badge badge-done">DONE</span></td>
            <td>1,000 bootstrap resamples; Holm-Bonferroni test</td>
          </tr>
          <tr>
            <td><strong>Automated Tests</strong></td>
            <td>Full unit test suite (30 test cases)</td>
            <td><span class="badge badge-done">DONE</span></td>
            <td>30 passed in &lt; 4s under bare <code>pytest</code></td>
          </tr>
          <tr>
            <td><strong>Stretch Items</strong></td>
            <td>Game loop (NOT STARTED), closed-form bound (PARTIAL)</td>
            <td><span class="badge badge-partial">PARTIAL</span></td>
            <td>Empirical <i>p</i>* &approx; 0.82 &sigma;<sub>1</sub><sup>2</sup> observed; proof pending</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="col-5">
      <div class="figure-box">
        <img src="{arch_img}" style="max-height: 148px;" alt="System Architecture">
        <div class="caption">Figure 1: End-to-end system architecture highlighting BUILT vs PENDING components.</div>
      </div>
    </div>
  </div>

  <h2>3. IR Link-Analysis Pipeline Details</h2>
  <p>
    <strong>Non-Applicability of Standard IR Text Processing:</strong> Standard IR text processing pipelines (tokenization, stemming, stopwords, inverted indexing, BM25) do not apply to this investigation. The web information retrieval setting addressed here operates on the hyperlink graph layer to determine authority and hub quality scores independently of keyword indexing.
  </p>
  <div class="highlight-box">
    <strong>Link-Analysis Ingestion & Processing Pipeline:</strong>
    <ul style="margin: 1.5px 0 0 0;">
      <li><strong>Graph Ingestion & Normalization:</strong> Raw SNAP edge lists (e.g., <code>web-Stanford</code>, <code>wiki-Vote</code>) and synthetic networks are ingested, deduplicated, filtered for self-loops, and mapped into contiguous zero-indexed node arrays ($0 \dots N-1$) stored as SciPy CSR/CSC sparse matrices.</li>
      <li><strong>Kleinberg Query Base-Set Builder:</strong> Implements Kleinberg (1999) topic base-set construction: generates a query root set <i>R</i> (|<i>R</i>| &approx; 100&ndash;200 nodes) via localized random walks, expands forward to all immediate out-neighbors (<i>S</i> = <i>R</i> &cup; <i>Out</i>(<i>R</i>)), and expands backward with strict in-link capping (at most 50 predecessors per root node) to prevent ubiquitous web portals from overwhelming graph topology.</li>
      <li><strong>Sparse Power Iteration Ranking:</strong> Computes stationary distributions via accelerated sparse matrix-vector multiplication with strict convergence threshold tol = 10<sup>&minus;8</sup> and max iterations = 200. PageRank enforces damping &alpha; = 0.85 with dangling node mass redistribution. SALSA incorporates an ergodic teleport (&epsilon; = 10<sup>&minus;4</sup>) to prevent multi-component stalls.</li>
      <li><strong>Adversarial Injection & Evaluation:</strong> Injects synthetic attacker nodes and directed edges under budget <i>B</i>. Computes ranking disruption metrics comparing clean vector <b>a</b><sub>clean</sub> against attacked vector <b>a</b><sub>att</sub> with non-parametric bootstrap confidence intervals.</li>
    </ul>
  </div>
</div>

<!-- ============================================================== -->
<!-- PAGE 2: PRELIMINARY RESULTS (COST CURVES & DEFENSES)           -->
<!-- ============================================================== -->
<div class="page">
  <h2>4. Preliminary Evaluation Results: Cost Curves & Defenses</h2>
  
  <h3>4a. Attack Cost Curves Across Threat Topologies (n = 60 per cell, 95% Bootstrap CIs)</h3>
  <p style="font-size: 7.2pt; margin-bottom: 2.5px;">
    Evaluated across 4 graphs (BA-500, ER-500, SBM-500, web-Stanford base set), 3 seeds (42, 123, 456), and 5 target tiers. Metrics reported: Normalized Rank Gain (<i>r</i><sub>clean</sub> &minus; <i>r</i><sub>att</sub>) / (<i>r</i><sub>clean</sub> &minus; 1) &isin; [0, 1], Top-10 Entry Rate, and Top-20 Jaccard.
  </p>
  <table>
    <thead>
      <tr>
        <th style="width: 12%;">Budget</th>
        <th style="width: 25%;">Attack Topology</th>
        <th style="width: 15%;">Plain HITS</th>
        <th style="width: 17%;">PageRank (&alpha; = 0.85)</th>
        <th style="width: 15%;">SALSA</th>
        <th style="width: 16%;">In-Degree</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td rowspan="3"><strong><i>B</i> = 25</strong><br><span style="font-size:6.5pt; color:#718096;">Pre-Takeover</span></td>
        <td><strong>A2: Hub Farm</strong><br><span style="font-size:6.2pt; color:#718096;">Norm Gain | Top10 | Jacc</span></td>
        <td>0.316 [0.230, 0.413]<br>13.3% [5.0%, 23.3%]<br>Jacc@20: 0.837</td>
        <td><strong>0.982</strong> [0.973, 0.990]<br><strong>100.0%</strong> [100.0%, 100.0%]<br>Jacc@20: 0.794</td>
        <td>0.950 [0.918, 0.976]<br>86.7% [78.3%, 95.0%]<br>Jacc@20: 0.892</td>
        <td>0.982 [0.973, 0.989]<br>91.7% [85.0%, 96.7%]<br>Jacc@20: 0.839</td>
      </tr>
      <tr>
        <td><strong>A5: Proposal Cross-Score</strong><br><span style="font-size:6.2pt; color:#718096;">Norm Gain | Top10 | Jacc</span></td>
        <td><strong>0.872</strong> [0.820, 0.916]<br>26.7% [16.7%, 38.3%]<br>Jacc@20: 0.733</td>
        <td>0.421 [0.370, 0.481]<br>0.0% [0.0%, 0.0%]<br>Jacc@20: 0.936</td>
        <td>0.745 [0.531, 0.864]<br>18.3% [8.3%, 28.3%]<br>Jacc@20: 0.954</td>
        <td>0.835 [0.785, 0.879]<br>23.3% [13.3%, 35.0%]<br>Jacc@20: 0.871</td>
      </tr>
      <tr>
        <td><strong>A6: Greedy Gradient</strong><br><span style="font-size:6.2pt; color:#718096;">Norm Gain | Top10 | Jacc</span></td>
        <td><strong>0.998</strong> [0.998, 0.999]<br><strong>100.0%</strong> [100.0%, 100.0%]<br>Jacc@20: 0.622</td>
        <td>0.916 [0.889, 0.941]<br>66.7% [55.0%, 78.3%]<br>Jacc@20: 0.852</td>
        <td>0.960 [0.911, 0.987]<br>91.7% [85.0%, 96.7%]<br>Jacc@20: 0.895</td>
        <td>0.982 [0.973, 0.989]<br>91.7% [85.0%, 96.7%]<br>Jacc@20: 0.858</td>
      </tr>
      <tr>
        <td rowspan="3"><strong><i>B</i> = 100</strong><br><span style="font-size:6.5pt; color:#718096;">Post-Takeover</span></td>
        <td><strong>A2: Hub Farm</strong><br><span style="font-size:6.2pt; color:#718096;">Norm Gain | Top10 | Jacc</span></td>
        <td>0.576 [0.473, 0.687]<br>50.0% [38.3%, 63.3%]<br>Jacc@20: 0.438</td>
        <td><strong>0.998</strong> [0.996, 1.000]<br><strong>100.0%</strong> [100.0%, 100.0%]<br>Jacc@20: 0.634</td>
        <td>0.958 [0.929, 0.983]<br>88.3% [80.0%, 95.0%]<br>Jacc@20: 0.844</td>
        <td>0.996 [0.992, 0.999]<br>100.0% [100.0%, 100.0%]<br>Jacc@20: 0.831</td>
      </tr>
      <tr>
        <td><strong>A5: Proposal Cross-Score</strong><br><span style="font-size:6.2pt; color:#718096;">Norm Gain | Top10 | Jacc</span></td>
        <td>0.883 [0.831, 0.928]<br>50.0% [38.3%, 63.3%]<br>Jacc@20: 0.607</td>
        <td>0.817 [0.791, 0.842]<br>23.3% [13.3%, 35.0%]<br>Jacc@20: 0.841</td>
        <td>0.939 [0.865, 0.976]<br>91.7% [85.0%, 96.7%]<br>Jacc@20: 0.877</td>
        <td>0.968 [0.959, 0.977]<br>91.7% [85.0%, 96.7%]<br>Jacc@20: 0.816</td>
      </tr>
      <tr>
        <td><strong>A6: Greedy Gradient</strong><br><span style="font-size:6.2pt; color:#718096;">Norm Gain | Top10 | Jacc</span></td>
        <td><strong>0.999</strong> [0.998, 0.999]<br><strong>100.0%</strong> [100.0%, 100.0%]<br>Jacc@20: 0.614</td>
        <td>0.992 [0.985, 0.998]<br>100.0% [100.0%, 100.0%]<br>Jacc@20: 0.638</td>
        <td>0.997 [0.993, 0.999]<br>100.0% [100.0%, 100.0%]<br>Jacc@20: 0.898</td>
        <td>0.996 [0.992, 0.999]<br>100.0% [100.0%, 100.0%]<br>Jacc@20: 0.850</td>
      </tr>
    </tbody>
  </table>

  <h3>Secondary Pooled Summary (All 8 Attacks, n = 480 per ranker, Preliminary)</h3>
  <table>
    <thead>
      <tr>
        <th>Budget</th>
        <th>Ranker</th>
        <th>Normalized Rank Gain</th>
        <th>Top-10 Entry Rate (%)</th>
        <th>Top-20 Jaccard</th>
        <th>Top-20 NDCG</th>
        <th>Kendall's &tau;</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td rowspan="4"><strong><i>B</i> = 25</strong></td>
        <td><strong>Plain HITS</strong></td>
        <td>0.511 [0.471, 0.551]</td>
        <td>24.0% [20.4%, 27.9%]</td>
        <td>0.783 [0.758, 0.806]</td>
        <td>0.974 [0.967, 0.980]</td>
        <td>0.960 [0.952, 0.968]</td>
      </tr>
      <tr>
        <td><strong>PageRank (&alpha; = 0.85)</strong></td>
        <td>0.472 [0.442, 0.506]</td>
        <td>20.8% [17.3%, 24.6%]</td>
        <td>0.921 [0.908, 0.932]</td>
        <td>0.986 [0.982, 0.990]</td>
        <td>0.991 [0.989, 0.993]</td>
      </tr>
      <tr>
        <td><strong>SALSA</strong></td>
        <td>0.665 [0.619, 0.707]</td>
        <td>30.6% [26.5%, 34.4%]</td>
        <td>0.945 [0.937, 0.953]</td>
        <td>0.983 [0.978, 0.988]</td>
        <td>0.987 [0.984, 0.990]</td>
      </tr>
      <tr>
        <td><strong>In-Degree</strong></td>
        <td>0.695 [0.664, 0.728]</td>
        <td>33.3% [29.4%, 37.5%]</td>
        <td>0.884 [0.871, 0.897]</td>
        <td>0.982 [0.978, 0.986]</td>
        <td>0.997 [0.996, 0.998]</td>
      </tr>
      <tr>
        <td rowspan="4"><strong><i>B</i> = 100</strong></td>
        <td><strong>Plain HITS</strong></td>
        <td>0.600 [0.560, 0.642]</td>
        <td>43.8% [39.4%, 48.1%]</td>
        <td>0.622 [0.590, 0.655]</td>
        <td>0.875 [0.852, 0.898]</td>
        <td>0.878 [0.862, 0.895]</td>
      </tr>
      <tr>
        <td><strong>PageRank (&alpha; = 0.85)</strong></td>
        <td>0.630 [0.597, 0.663]</td>
        <td>33.5% [29.2%, 37.9%]</td>
        <td>0.838 [0.819, 0.855]</td>
        <td>0.946 [0.937, 0.956]</td>
        <td>0.977 [0.974, 0.981]</td>
      </tr>
      <tr>
        <td><strong>SALSA</strong></td>
        <td>0.751 [0.720, 0.784]</td>
        <td>62.1% [57.7%, 66.5%]</td>
        <td>0.894 [0.881, 0.906]</td>
        <td>0.958 [0.949, 0.967]</td>
        <td>0.966 [0.960, 0.971]</td>
      </tr>
      <tr>
        <td><strong>In-Degree</strong></td>
        <td>0.760 [0.728, 0.793]</td>
        <td>64.6% [60.4%, 68.8%]</td>
        <td>0.845 [0.829, 0.860]</td>
        <td>0.952 [0.943, 0.960]</td>
        <td>0.996 [0.995, 0.997]</td>
      </tr>
    </tbody>
  </table>

  <h3>4b. Algorithmic Defense Evaluation Matrix (n = 110 positive attack gain cells)</h3>
  <table>
    <thead>
      <tr>
        <th>Defense Variant</th>
        <th>Attack Reduction (Mean [95% CI])</th>
        <th>Median Red.</th>
        <th>Clean Top-20 Jacc</th>
        <th>Clean NDCG Loss</th>
        <th>Goal Rate (&ge;50% red, &le;5% loss)</th>
        <th>Operational Finding</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Undefended HITS</strong></td>
        <td>0.0% [0.0%, 0.0%]</td>
        <td>0.0%</td>
        <td>1.000</td>
        <td>0.0%</td>
        <td>0.0%</td>
        <td>Baseline reference on positive gain cells (<i>n</i> = 110).</td>
      </tr>
      <tr>
        <td><strong>D1: Randomized HITS (&epsilon;=0.15)</strong></td>
        <td>-72.6% [-145.4%, -22.6%]</td>
        <td>-1.0%</td>
        <td>0.781</td>
        <td><strong>0.1%</strong></td>
        <td>13.6%</td>
        <td>Uniform reset diffuses probability mass like PageRank.</td>
      </tr>
      <tr>
        <td><strong>D1: Subspace HITS (<i>k</i>=5)</strong></td>
        <td>-0.8% [-50.0%, 51.8%]</td>
        <td>15.7%</td>
        <td>0.338</td>
        <td>28.3%</td>
        <td>9.1%</td>
        <td>Severe clean graph rank distortion.</td>
      </tr>
      <tr>
        <td><strong>D2: Bharat-Henzinger (1/<i>k</i>)</strong></td>
        <td>38.7% [13.4%, 57.0%]</td>
        <td><strong>89.4%</strong></td>
        <td>0.254</td>
        <td>59.6%</td>
        <td>1.8%</td>
        <td>High median mitigation but distorts clean web hubs.</td>
      </tr>
      <tr>
        <td><strong>D3: Hub Capping (10%)</strong></td>
        <td>0.0% [0.0%, 0.0%]</td>
        <td>0.0%</td>
        <td>1.000</td>
        <td>0.0%</td>
        <td>0.0%</td>
        <td><strong>Exact No-Op:</strong> 10% cap never triggered on tested graphs.</td>
      </tr>
      <tr>
        <td><strong>D4: Wu-Davison (Mutual)</strong></td>
        <td>-23.3% [-96.0%, 16.9%]</td>
        <td>3.0%</td>
        <td>0.786</td>
        <td><strong>0.5%</strong></td>
        <td><strong>36.4%</strong></td>
        <td>Effective on A2/A3 (69&ndash;75% red); fails on camouflaged/A6.</td>
      </tr>
      <tr>
        <td><strong>D4b: Wu-Davison (Out-Jaccard)</strong></td>
        <td>-24.0% [-103.9%, 17.7%]</td>
        <td>2.5%</td>
        <td>0.680</td>
        <td><strong>1.3%</strong></td>
        <td><strong>38.2%</strong></td>
        <td>Effective on A2/A3 (74&ndash;85% red); fails on camouflaged/A6.</td>
      </tr>
      <tr>
        <td><strong>D5: Trust-Based HITS</strong></td>
        <td>-150.7% [-323.7%, -29.4%]</td>
        <td>11.1%</td>
        <td>0.337</td>
        <td>27.7%</td>
        <td>6.4%</td>
        <td>In-degree proxy seed causes high clean NDCG loss.</td>
      </tr>
    </tbody>
  </table>
  <div class="highlight-box">
    <strong>Key Defense Findings:</strong> (1) <strong>NO defense met the target criteria</strong> (&ge;50% reduction at &le;5% clean NDCG loss) across all attack topologies. (2) <strong>D3 Hub Capping is an exact no-op</strong> because no single hub accumulated &gt;10% of total hub mass. (3) <strong>Wu-Davison D4 and D4b</strong> achieve high mitigation against isolated farms (A2/A3: 69&ndash;85% reduction, 75&ndash;86% goal rate), but fail completely when attackers camouflage links or use greedy gradient additions.
  </div>
</div>

<!-- ============================================================== -->
<!-- PAGE 3: H2 TAKEOVER, COMPUTATIONAL EFFICIENCY, HYPOTHESES      -->
<!-- ============================================================== -->
<div class="page">
  <h2>4c. Hypothesis H2: Spectral Phase Transition (Preliminary)</h2>
  <div class="row" style="align-items: center;">
    <div class="col-7">
      <div class="figure-box">
        <img src="{h2_img}" style="max-height: 135px;" alt="H2 Spectral Takeover">
        <div class="caption">Figure 2: HITS authority score & rank vs hub farm size <i>p</i> showing abrupt bifurcation at <i>p</i> &approx; &sigma;<sub>1</sub><sup>2</sup> vs smooth PageRank.</div>
      </div>
    </div>
    <div class="col-5">
      <div class="highlight-box" style="font-size: 7.3pt;">
        <strong>Empirical H2 Robustness Findings (<i>n</i> = 60 instances):</strong>
        <ul style="margin: 1.5px 0 0 0;">
          <li><strong>Upper Bound Hold Rate:</strong> &sigma;<sub>1</sub><sup>2</sup> &ge; max in-degree holds in <strong>100.0%</strong> of instances (60/60).</li>
          <li><strong>Takeover Point:</strong> Takeover occurs somewhat below &sigma;<sub>1</sub><sup>2</sup>:
            <br>&bull; Top-10 takeover: <i>p</i>*(10) / &sigma;<sub>1</sub><sup>2</sup> = <strong>0.817</strong> [0.751, 0.879] (<i>n</i> = 60).
            <br>&bull; Top-1 takeover: <i>p</i>*(1) / &sigma;<sub>1</sub><sup>2</sup> = <strong>0.873</strong> [0.819, 0.923] (<i>n</i> = 60).</li>
          <li><strong>Abrupt Bifurcation:</strong> HITS exhibits an abrupt single-step jump in <strong>63.3%</strong> of instances (38/60) with mean single-step jump of <strong>69.7 ranks</strong> (median 64.0) vs <strong>16.9 ranks</strong> for PageRank.</li>
          <li><strong>Counterexamples (36.7%):</strong> In 22/60 runs (12 on ER, 7 on BA, 3 on Stanford), jumps were gradual due to narrow eigengaps.</li>
        </ul>
      </div>
    </div>
  </div>

  <h2>4d. Clean Baseline Computational Efficiency & Peak Memory</h2>
  <table>
    <thead>
      <tr>
        <th>Dataset / Graph</th>
        <th>Nodes</th>
        <th>Edges</th>
        <th>HITS Runtime (Iter)</th>
        <th>PageRank Runtime (Iter)</th>
        <th>SALSA Runtime (Iter)</th>
        <th>Peak Heap (tracemalloc)</th>
        <th>Process RSS (psutil)</th>
        <th>Eigengap &sigma;<sub>1</sub><sup>2</sup> &minus; &sigma;<sub>2</sub><sup>2</sup></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Synthetic BA-1000</strong></td>
        <td>1,000</td>
        <td>4,369</td>
        <td>0.045s (42 it)</td>
        <td>0.013s (26 it)</td>
        <td>0.016s (57 it)</td>
        <td>0.85 MB</td>
        <td>108.2 MB</td>
        <td>45.41</td>
      </tr>
      <tr>
        <td><strong>Synthetic ER-1000</strong></td>
        <td>1,000</td>
        <td>4,973</td>
        <td>0.080s (39 it)</td>
        <td>0.013s (22 it)</td>
        <td>0.014s (34 it)</td>
        <td>0.82 MB</td>
        <td>114.7 MB</td>
        <td>14.44</td>
      </tr>
      <tr>
        <td><strong>Planted SBM-840</strong></td>
        <td>840</td>
        <td>2,971</td>
        <td>0.023s (11 it)</td>
        <td>0.010s (28 it)</td>
        <td>0.017s (125 it)</td>
        <td>0.50 MB</td>
        <td>118.9 MB</td>
        <td>275.51</td>
      </tr>
      <tr>
        <td><strong>SNAP wiki-Vote</strong></td>
        <td>7,115</td>
        <td>103,689</td>
        <td>0.657s (23 it)</td>
        <td>0.580s (23 it)</td>
        <td>0.643s (53 it)</td>
        <td>18.17 MB</td>
        <td>183.4 MB</td>
        <td>6,158.51</td>
      </tr>
      <tr>
        <td><strong>SNAP web-Stanford BaseSet</strong></td>
        <td>1,686</td>
        <td>13,849</td>
        <td>0.110s (23 it)</td>
        <td>0.155s (81 it)</td>
        <td>0.114s (200 it)</td>
        <td>2.45 MB</td>
        <td>152.1 MB</td>
        <td>2,518.81</td>
      </tr>
    </tbody>
  </table>
  <p style="font-size: 7.0pt; color: #4A5568; margin-top: -3px; margin-bottom: 4px;">
    <em>Benchmarked Hardware:</em> 12th Gen Intel Core i5-12500H (12 physical cores, 16 logical threads), 15.69 GB RAM, Windows 11 64-bit, Python 3.12.5. Note: Process RSS (108.2&ndash;183.4 MB) is dominated by the Python runtime/library baseline; active heap allocation (0.50&ndash;18.17 MB) measures ranker data structures.
  </p>

  <h2>5. Hypothesis Status Summary</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 18%;">Hypothesis</th>
        <th style="width: 22%;">Status</th>
        <th style="width: 60%;">Empirical Evidence & Theoretical Bounds</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>H1: Random Graphs HITS &sim; In-Degree</strong></td>
        <td><span class="badge badge-notstarted">NOT SUPPORTED</span><br><span style="font-size:6.5pt; color:#742A2A;">(Attack Cost)</span></td>
        <td>In minimal budget tests to penetrate Top-10 (<i>B</i>*(10) across <i>n</i> = 9 controlled trials on ER-500), HITS required a mean of <strong>4.44&times; more budget</strong> than simple in-degree (30&ndash;50 edges vs 5&ndash;10 edges). Clean rank correlation (&tau; = 0.746, &rho; = 0.887 on ER-1000) is supplementary only.</td>
      </tr>
      <tr>
        <td><strong>H2: Spectral Phase Takeover at <i>p</i> &approx; &sigma;<sub>1</sub><sup>2</sup></strong></td>
        <td><span class="badge badge-done">SUPPORTED</span><br><span style="font-size:6.5pt; color:#22543D;">(Preliminary)</span></td>
        <td>Empirical takeover occurs somewhat below &sigma;<sub>1</sub><sup>2</sup> (<i>p</i>*(10) / &sigma;<sub>1</sub><sup>2</sup> = <strong>0.817</strong> [0.751, 0.879], <i>n</i> = 60). Bound &sigma;<sub>1</sub><sup>2</sup> &ge; max in-degree holds in 60/60 instances (100.0%). Abrupt jump observed in 63.3% of curves (mean jump 69.7 ranks vs 16.9 for PageRank); 36.7% counterexamples (22/60).</td>
      </tr>
      <tr>
        <td><strong>H3: Dense Communities Cheaper Attachment</strong></td>
        <td><span class="badge badge-notstarted">INCONCLUSIVE / NOT SUPPORTED</span></td>
        <td>Evaluated A2 (isolated farm) vs proposal A5 (linking to target and <i>c</i> = 3 top real authorities, <i>n</i> = 18 trials). On ER control (<i>n</i> = 9), attaching saved <strong>48.1%</strong> [39.3%, 57.0%] budget. On Planted SBM (<i>n</i> = 9), target failed to reach Top-10 under A2 within <i>B</i> &le; 200, leaving cost saving undefined / NaN.</td>
      </tr>
      <tr>
        <td><strong>H4: Defense Pareto Trade-Off Frontier</strong></td>
        <td><span class="badge badge-notstarted">NOT SUPPORTED</span><br><span style="font-size:6.5pt; color:#742A2A;">(So Far)</span></td>
        <td>Tested across 1,152 evaluations (<i>n</i> = 110 positive attack gain instances). <strong>NO defense achieved &ge;50% mean reduction at &le;5% clean NDCG loss across all attacks.</strong> D4/D4b mitigate isolated farms but fail on camouflaged/gradient attacks; D2 destroys clean ranking (59.6% loss).</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- ============================================================== -->
<!-- PAGE 4: PATH TO FINAL, CONTRIBUTION MATRIX, OTHER INFO         -->
<!-- ============================================================== -->
<div class="page">
  <h2>6. Path to Final Submission (20&ndash;25% Remaining Work)</h2>
  <div class="row">
    <div class="col-6">
      <div class="highlight-box">
        <strong>Planned Technical Milestones:</strong>
        <ul style="margin: 1.5px 0 0 0;">
          <li><strong>WEBSPAM-UK2006 Host Graph Pipeline (Planned: 28 Oct):</strong> Convert the compressed BVGraph bitstream to an ASCII edge list using Java WebGraph utilities, then evaluate baseline Spam@k, AUC, and precision/recall across rankers. <em>Note: Host graph size and format were not verified from the dataset page (the proposal assumed ~1.9 MB; per the proposal, to be confirmed).</em></li>
          <li><strong>Experimental Scale-Up (Planned: 1 Nov):</strong> Expand evaluations to 5 seeds (currently 3), budgets up to <i>B</i> = 500 (currently &le; 100), additional target nodes, <code>web-NotreDame</code>, and higher budget cap (<i>B</i> &gt; 200) for SBM community runs to resolve H3.</li>
          <li><strong>Defense Matrix on Larger Graphs (Planned: 5 Nov):</strong> Run full defense matrix on large subgraphs with thresholds calibrated on a separate validation graph.</li>
          <li><strong>Experiments Freeze (Planned: 8 Nov):</strong> Lock raw CSVs, regenerate 300 DPI figures, and conduct final hypothesis tests.</li>
          <li><strong>Final Submission (Planned: 15 Nov):</strong> Final Report and presentation deck.</li>
        </ul>
      </div>
    </div>
    <div class="col-6">
      <div class="highlight-box">
        <strong>Status of Stretch Objectives:</strong>
        <ul style="margin: 1.5px 0 0 0;">
          <li><strong>Game-Theoretic Loop:</strong> <span class="badge badge-notstarted">NOT STARTED</span>. Iterative attacker-defender equilibrium model scheduled for final sprint.</li>
          <li><strong>Closed-Form Spectral Bound:</strong> <span class="badge badge-partial">PARTIAL</span>. Empirical takeover at <i>p</i>* &approx; 0.82 &sigma;<sub>1</sub><sup>2</sup> observed across 60 instances; formal closed-form mathematical proof and generalized <i>B</i>*(<i>k</i>) bound are in progress.</li>
          <li><strong>WEBSPAM-UK2007 Classifier:</strong> <span class="badge badge-notstarted">NOT STARTED</span>. Dependent on Milestone 1 host graph ingestion.</li>
        </ul>
      </div>
    </div>
  </div>

  <h2>7. Team Contributions</h2>
  <p style="font-size: 7.3pt; margin-bottom: 2.5px;">
    The project functional areas and contributions confirmed across all team members are detailed below:
  </p>
  <table>
    <thead>
      <tr>
        <th style="width: 28%;">Team Member</th>
        <th style="width: 72%;">Contributions & Functional Areas</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Shrisay Shandilya</strong></td>
        <td>Core sparse rankers (HITS, PageRank, SALSA), SNAP data loaders, Kleinberg base-set pipeline, clean computational efficiency baselines.</td>
      </tr>
      <tr>
        <td><strong>Vibhor Rathi</strong></td>
        <td>Adversarial link injection attacks (A1&ndash;A6, A4b, A5b), threat model validation suite, edge budget constraint verification.</td>
      </tr>
      <tr>
        <td><strong>Prachi Jain</strong></td>
        <td>Algorithmic defenses (D1&ndash;D5), evaluation metrics (NDCG, Jaccard, Tau, Rho), statistical testing suite (Bootstrap, Wilcoxon), publication figure generation.</td>
      </tr>
    </tbody>
  </table>

  <h2>8. Other Information & Disclosures</h2>
  <div class="row">
    <div class="col-6">
      <div class="highlight-box" style="font-size: 7.2pt;">
        <strong>Corrections vs Version 1 of Progress Report:</strong>
        <ul style="margin: 1.5px 0 0 0;">
          <li><strong>CPU Model:</strong> Probed actual hardware as 12th Gen Intel Core i5-12500H (12 cores, 16 threads), correcting unverified v1 claim.</li>
          <li><strong>H1 Correlation:</strong> Verified clean ER-1000 &tau; = 0.746 (<i>p</i> = 7.99 &times; 10<sup>&minus;244</sup>; &rho; = 0.887), correcting unverified v1 claim of 0.912.</li>
          <li><strong>Defense Metric Bug:</strong> Resolved metric defect that returned 1.0 on zero-gain cells, correctly assessing undefended reduction as 0.0%.</li>
          <li><strong>Defense D2 & D3:</strong> Fixed D2 WCC no-op with true domain weighting; empirically verified D3 Hub Capping as an exact no-op on tested graphs.</li>
          <li><strong>Attack Definitions:</strong> Restored proposal A4 (single fake page) and A5 (fake hubs with no cross-links), retaining multi-hub variants as A4b/A5b.</li>
        </ul>
      </div>
    </div>
    <div class="col-6">
      <div class="highlight-box" style="font-size: 7.2pt;">
        <strong>Verification, Reproduction & Ethics:</strong>
        <ul style="margin: 1.5px 0 0 0;">
          <li><strong>Automated Test Suite:</strong> <strong>30 passed</strong> unit tests in 11.4s under bare <code>pytest -v</code>, asserting ranker correctness vs NetworkX (&lt; 10<sup>&minus;8</sup>).</li>
          <li><strong>Reproduction Commands:</strong> Fully reproducible via relative scripts:
            <br>&bull; <code>python scripts/download_data.py</code>
            <br>&bull; <code>python scripts/run_clean_baselines.py</code>
            <br>&bull; <code>python scripts/run_tier_b_experiments.py</code>
            <br>&bull; <code>python scripts/compute_facts_v2.py</code>
            <br>&bull; <code>python scripts/generate_figures.py</code></li>
          <li><strong>Research Ethics:</strong> All experiments conducted offline on public, anonymized SNAP web datasets and synthetic benchmark topologies.</li>
          <li><strong>AI-Assistance Disclosure:</strong> <em>Code and experiments were developed with an AI coding agent (Antigravity) under the team's direction; results were audited by the team.</em></li>
        </ul>
      </div>
    </div>
  </div>
</div>

</body>
</html>
"""
    html = html.replace("{arch_img}", arch_img).replace("{h2_img}", h2_img)
    HTML_SOURCE.write_text(html, encoding="utf-8")
    print(f"[GENERATED] HTML source written to {HTML_SOURCE}")


def compile_pdf():
    browser_exe = get_browser_path()
    print(f"[BROWSER] Using browser: {browser_exe}")

    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUTPUT_PDF}",
        str(HTML_SOURCE),
    ]

    print("[RUNNING] Compiling PDF via headless browser...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] Browser returned code {res.returncode}")
        print("Stdout:", res.stdout)
        print("Stderr:", res.stderr)
        sys.exit(1)

    if not OUTPUT_PDF.exists():
        raise FileNotFoundError(f"PDF was not generated at {OUTPUT_PDF}")

    # Copy to root
    shutil.copyfile(OUTPUT_PDF, ROOT_PDF)
    print(f"[SAVED] Report PDF saved to {OUTPUT_PDF} and copied to {ROOT_PDF}")


def inspect_and_render_pages():
    doc = fitz.open(str(OUTPUT_PDF))
    page_count = len(doc)
    print(f"\n=== PDF PAGE COUNT: {page_count} ===")

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        png_path = REPORT_DIR / f"page_{i+1}.png"
        pix.save(str(png_path))
        print(f"  [RENDERED] Page {i+1} saved to {png_path}")

    doc.close()
    return page_count


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    generate_html_source()
    compile_pdf()
    pages = inspect_and_render_pages()
    if pages > 4:
        print(f"\n[WARNING] PDF exceeds 4 pages (got {pages}). Adjusting required.")
        sys.exit(2)
    elif pages < 4:
        print(f"\n[INFO] PDF is {pages} pages (target is up to 4).")
    else:
        print(f"\n[SUCCESS] PDF is exactly {pages} pages. Fits budget perfectly.")


if __name__ == "__main__":
    main()
