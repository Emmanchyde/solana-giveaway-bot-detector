"""
html_report.py

Generates an interactive, production-grade Web3 HTML dashboard report for SybilClean v2.
"""

import json
import os
from wallet import is_valid_wallet
from config import BLACKLISTED_WALLETS


def generate_html_report(participants, output_filename="sybilclean_audit_report.html"):
    """
    Generates a standalone, interactive HTML dashboard summarizing the audit.
    Deduplicates participants sharing the exact same handle/username and wallet address.
    
    **Only includes participants with VALID wallet addresses.**
    No-wallet, invalid, and blacklisted entries are excluded.
    """
    
    # ---- FILTER: Only keep participants with valid wallets ----
    filtered_participants = []
    for p in participants:
        # Skip if no wallet
        if not p.wallet or not p.wallet.strip():
            continue
        wallet = p.wallet.strip()
        # Skip if blacklisted
        if wallet in BLACKLISTED_WALLETS:
            continue
        # Skip if invalid format
        if not is_valid_wallet(wallet):
            continue
        filtered_participants.append(p)
    
    # If no valid participants, generate empty report
    if not filtered_participants:
        print("⚠️ No valid wallet participants found. HTML report will be empty.")
    
    # Deduplicate entries sharing the exact same handle and wallet address
    unique_participants_dict = {}
    for p in filtered_participants:
        handle_clean = p.handle.strip().lower() if p.handle else ""
        wallet_clean = p.wallet.strip().lower() if p.wallet else ""
        key = (handle_clean, wallet_clean)
        
        if key not in unique_participants_dict:
            unique_participants_dict[key] = p
        else:
            existing_p = unique_participants_dict[key]
            combined_reasons = list(dict.fromkeys(existing_p.reasons + p.reasons))
            existing_p.reasons = combined_reasons

    deduped_participants = list(unique_participants_dict.values())

    low_count = sum(1 for p in deduped_participants if p.risk_level == "LOW")
    med_count = sum(1 for p in deduped_participants if p.risk_level == "MEDIUM")
    high_count = sum(1 for p in deduped_participants if p.risk_level == "HIGH")

    total_sol = sum(p.sol_balance for p in deduped_participants)
    funded_count = sum(1 for p in deduped_participants if p.sol_balance > 0)
    unique_handles = len({p.handle.strip().lower() for p in deduped_participants if p.handle.strip()})
    unique_wallets = len({p.wallet.strip() for p in deduped_participants if p.wallet.strip()})

    # Prepare table rows as JSON data for interactive filtering/searching
    table_data = []
    for p in deduped_participants:
        reasons_list = p.reasons if p.reasons else ["Perfect Score"]
        
        table_data.append({
            "handle": p.handle,
            "wallet": p.wallet,
            "score": p.risk_score,
            "level": p.risk_level,
            "sol": round(p.sol_balance, 4),
            "tx": p.tx_count,
            "wallet_created": p.wallet_created or "Unknown",
            "holds_token": p.holds_project_token or "No",
            "verified": "Yes" if p.verified else "No",
            "reasons": reasons_list
        })

    json_data = json.dumps(table_data)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SybilClean v2 | Audit Intelligence Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #07090e;
            --card-bg: rgba(18, 24, 38, 0.75);
            --card-border: rgba(255, 255, 255, 0.08);
            --card-hover: rgba(255, 255, 255, 0.14);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            --low-color: #10b981;
            --low-glow: rgba(16, 185, 129, 0.15);
            --med-color: #f59e0b;
            --med-glow: rgba(245, 158, 11, 0.15);
            --high-color: #ef4444;
            --high-glow: rgba(239, 68, 68, 0.15);
            --primary-accent: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.25);
            --cyan-accent: #38bdf8;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        body {{
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(56, 189, 248, 0.05) 0px, transparent 50%);
            background-attachment: fixed;
            color: var(--text-main);
            padding: 2.5rem 2rem;
            line-height: 1.5;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1440px;
            margin: 0 auto;
        }}

        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--card-border);
        }}

        .logo-title {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .logo-icon {{
            width: 42px;
            height: 42px;
            background: linear-gradient(135deg, var(--primary-accent), var(--cyan-accent));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px var(--primary-glow);
        }}

        .logo-icon svg {{
            width: 24px;
            height: 24px;
            fill: #fff;
        }}

        .logo-title h1 {{
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            background: linear-gradient(180deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .badge {{
            background: rgba(99, 102, 241, 0.12);
            color: #818cf8;
            border: 1px solid rgba(99, 102, 241, 0.3);
            padding: 0.3rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        /* On-Chain Disclaimer Banner */
        .notice-banner {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-left: 4px solid var(--cyan-accent);
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 0.85rem;
            backdrop-filter: blur(12px);
        }}

        .notice-icon {{
            color: var(--cyan-accent);
            flex-shrink: 0;
        }}

        .notice-text {{
            font-size: 0.88rem;
            color: #cbd5e1;
        }}

        .notice-text strong {{
            color: #fff;
        }}

        /* Metric Cards */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}

        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.35rem 1.5rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: transparent;
            transition: background 0.25s ease;
        }}

        .card:hover {{
            transform: translateY(-3px);
            border-color: var(--card-hover);
        }}

        .card-low:hover::before {{ background: var(--low-color); }}
        .card-med:hover::before {{ background: var(--med-color); }}
        .card-high:hover::before {{ background: var(--high-color); }}

        .card-title {{
            color: var(--text-muted);
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.6rem;
        }}

        .card-value {{
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }}

        .value-low {{ color: var(--low-color); }}
        .value-med {{ color: var(--med-color); }}
        .value-high {{ color: var(--high-color); }}

        /* Charts Section */
        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}

        @media (max-width: 960px) {{
            .charts-grid {{ grid-template-columns: 1fr; }}
        }}

        .chart-card {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 330px;
            padding: 1.5rem;
        }}

        /* Table Section */
        .table-section {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
        }}

        .table-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .search-box {{
            background: rgba(7, 9, 14, 0.8);
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 0.65rem 1.1rem;
            border-radius: 10px;
            font-size: 0.88rem;
            width: 320px;
            outline: none;
            transition: all 0.2s ease;
        }}

        .search-box:focus {{
            border-color: var(--primary-accent);
            box-shadow: 0 0 0 3px var(--primary-glow);
        }}

        .filter-buttons {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            background: rgba(7, 9, 14, 0.6);
            border: 1px solid var(--card-border);
            color: var(--text-muted);
            padding: 0.55rem 1.1rem;
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.82rem;
            font-weight: 700;
            transition: all 0.2s ease;
        }}

        .filter-btn:hover {{
            color: #fff;
            border-color: var(--card-hover);
        }}

        .filter-btn.active {{
            background: var(--primary-accent);
            color: #fff;
            border-color: var(--primary-accent);
            box-shadow: 0 0 16px var(--primary-glow);
        }}

        /* Table Design */
        .table-container {{
            overflow-x: auto;
            max-height: 620px;
            overflow-y: auto;
            border-radius: 12px;
            border: 1px solid var(--card-border);
        }}

        .table-container::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        .table-container::-webkit-scrollbar-track {{
            background: rgba(7, 9, 14, 0.5);
        }}
        .table-container::-webkit-scrollbar-thumb {{
            background: #1e293b;
            border-radius: 4px;
        }}

        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            text-align: left;
            font-size: 0.86rem;
        }}

        th {{
            background: #0f172a;
            color: var(--text-muted);
            padding: 1rem 1.1rem;
            position: sticky;
            top: 0;
            z-index: 10;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            border-bottom: 1px solid var(--card-border);
        }}

        td {{
            padding: 1rem 1.1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            vertical-align: middle;
            background: transparent;
            transition: background 0.15s ease;
        }}

        tr:hover td {{
            background: rgba(255, 255, 255, 0.025);
        }}

        .font-mono {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            color: #cbd5e1;
        }}

        /* Badges & Tags */
        .level-badge {{
            padding: 0.25rem 0.7rem;
            border-radius: 6px;
            font-size: 0.73rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            display: inline-block;
        }}

        .level-LOW {{ background: var(--low-glow); color: var(--low-color); border: 1px solid rgba(16, 185, 129, 0.3); }}
        .level-MEDIUM {{ background: var(--med-glow); color: var(--med-color); border: 1px solid rgba(245, 158, 11, 0.3); }}
        .level-HIGH {{ background: var(--high-glow); color: var(--high-color); border: 1px solid rgba(239, 68, 68, 0.3); }}

        .reasons-col {{
            white-space: normal !important;
            min-width: 260px;
            max-width: 420px;
            line-height: 1.4;
        }}

        .reason-tag {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 6px;
            padding: 0.25rem 0.55rem;
            margin: 0.15rem;
            font-size: 0.76rem;
            color: #cbd5e1;
            word-break: break-word;
        }}

        .reason-clean {{
            background: rgba(16, 185, 129, 0.08);
            color: var(--low-color);
            border-color: rgba(16, 185, 129, 0.2);
        }}
    </style>
</head>
<body>

<div class="container">
    <header>
        <div class="logo-title">
            <div class="logo-icon">
                <svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8s0 0 0 0z"/></svg>
            </div>
            <div>
                <h1>SybilClean v2</h1>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <span class="badge">Commercial Audit</span>
            <div style="color: var(--text-muted); font-size: 0.88rem;">
                Valid Wallets: <strong style="color: #fff;">{len(deduped_participants)}</strong>
            </div>
        </div>
    </header>

    <!-- On-Chain Context Notice Banner -->
    <div class="notice-banner">
        <div class="notice-icon">
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>
        </div>
        <div class="notice-text">
            <strong>On-Chain Evaluation Guidance:</strong> A wallet with zero SOL balance does not inherently signal bot behavior. On-chain transaction activity and interaction volume are equally critical parameters when judging wallet legitimacy.
        </div>
    </div>

    <!-- Metrics Cards -->
    <div class="metrics-grid">
        <div class="card card-low">
            <div class="card-title">Low Risk (Clean)</div>
            <div class="card-value value-low">{low_count}</div>
        </div>
        <div class="card card-med">
            <div class="card-title">Medium Risk (Spam)</div>
            <div class="card-value value-med">{med_count}</div>
        </div>
        <div class="card card-high">
            <div class="card-title">High Risk (Sybil)</div>
            <div class="card-value value-high">{high_count}</div>
        </div>
        <div class="card">
            <div class="card-title">Unique Accounts</div>
            <div class="card-value">{unique_handles}</div>
        </div>
        <div class="card">
            <div class="card-title">Funded Wallets (>0 SOL)</div>
            <div class="card-value">{funded_count} <span style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">({total_sol:.2f} SOL)</span></div>
        </div>
    </div>

    <!-- Charts -->
    <div class="charts-grid">
        <div class="card chart-card">
            <canvas id="riskPieChart"></canvas>
        </div>
        <div class="card chart-card">
            <canvas id="solBarChart"></canvas>
        </div>
    </div>

    <!-- Table Section -->
    <div class="table-section">
        <div class="table-header">
            <input type="text" id="searchInput" class="search-box" placeholder="Search handle, wallet, or detection rule...">
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterLevel('ALL', this)">All ({len(deduped_participants)})</button>
                <button class="filter-btn" onclick="filterLevel('FUNDED', this)">Funded ({funded_count})</button>
                <button class="filter-btn" onclick="filterLevel('HOLDS_TOKEN', this)">Holds Token</button>
                <button class="filter-btn" onclick="filterLevel('LOW', this)">Low ({low_count})</button>
                <button class="filter-btn" onclick="filterLevel('MEDIUM', this)">Medium ({med_count})</button>
                <button class="filter-btn" onclick="filterLevel('HIGH', this)">High ({high_count})</button>
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Handle</th>
                        <th>Wallet Address</th>
                        <th>SOL Balance</th>
                        <th>Tx Count</th>
                        <th>Wallet Created</th>
                        <th>Holds Token</th>
                        <th>Risk Score</th>
                        <th>Risk Tier</th>
                        <th>Verified</th>
                        <th>Detection Reasons</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    <!-- Populated dynamically -->
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
    const data = {json_data};
    let currentFilter = 'ALL';

    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = 'Plus Jakarta Sans';

    const ctxPie = document.getElementById('riskPieChart').getContext('2d');
    new Chart(ctxPie, {{
        type: 'doughnut',
        data: {{
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{{
                data: [{low_count}, {med_count}, {high_count}],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0,
                hoverOffset: 6
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ position: 'bottom', labels: {{ usePointStyle: true, padding: 20 }} }}
            }},
            cutout: '70%'
        }}
    }});

    const ctxBar = document.getElementById('solBarChart').getContext('2d');
    const fundedCount = {funded_count};
    const unfundedCount = {len(deduped_participants)} - fundedCount;

    new Chart(ctxBar, {{
        type: 'bar',
        data: {{
            labels: ['Funded Wallets (>0 SOL)', 'Unfunded Wallets (0 SOL)'],
            datasets: [{{
                label: 'Wallet Count',
                data: [fundedCount, unfundedCount],
                backgroundColor: ['#6366f1', '#1e293b'],
                borderRadius: 8,
                borderSkipped: false
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ display: false }}
            }},
            scales: {{
                x: {{ grid: {{ display: false }} }},
                y: {{ grid: {{ color: 'rgba(255, 255, 255, 0.05)' }} }}
            }}
        }}
    }});

    function renderTable() {{
        const search = document.getElementById('searchInput').value.toLowerCase();
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';

        const filtered = data.filter(item => {{
            const matchesLevel = (currentFilter === 'ALL') ||
                                 (currentFilter === 'FUNDED' && item.sol > 0) ||
                                 (currentFilter === 'HOLDS_TOKEN' && item.holds_token === 'Yes') ||
                                 (item.level === currentFilter);

            const reasonsText = Array.isArray(item.reasons) ? item.reasons.join(' ') : item.reasons;
            const matchesSearch = item.handle.toLowerCase().includes(search) ||
                                  item.wallet.toLowerCase().includes(search) ||
                                  reasonsText.toLowerCase().includes(search);

            return matchesLevel && matchesSearch;
        }});

        filtered.forEach(item => {{
            const tr = document.createElement('tr');
            const txDisplay = (typeof item.tx === 'number' && item.tx >= 100) ? '&#8805; 100' : item.tx;

            let reasonsHtml = '';
            if (Array.isArray(item.reasons)) {{
                reasonsHtml = item.reasons.map(r => {{
                    const isPerfect = r.toLowerCase().includes('perfect score');
                    return `<span class="reason-tag ${{isPerfect ? 'reason-clean' : ''}}">${{r}}</span>`;
                }}).join('');
            }} else {{
                reasonsHtml = `<span class="reason-tag">${{item.reasons}}</span>`;
            }}

            tr.innerHTML = `
                <td><strong style="color: #fff;">${{item.handle}}</strong></td>
                <td class="font-mono">${{item.wallet}}</td>
                <td><strong style="color: #f1f5f9;">${{item.sol.toFixed(4)}}</strong> <span style="color: var(--text-dim); font-size: 0.78rem;">SOL</span></td>
                <td class="font-mono">${{txDisplay}}</td>
                <td style="font-size: 0.82rem; color: #94a3b8;">${{item.wallet_created}}</td>
                <td><span style="color: ${{item.holds_token === 'Yes' ? '#10b981' : '#64748b'}};">${{item.holds_token}}</span></td>
                <td><strong style="color: #fff;">${{item.score}}</strong></td>
                <td><span class="level-badge level-${{item.level}}">${{item.level}}</span></td>
                <td>${{item.verified}}</td>
                <td class="reasons-col">${{reasonsHtml}}</td>
            `;
            tbody.appendChild(tr);
        }});
    }}

    function filterLevel(level, btn) {{
        currentFilter = level;
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderTable();
    }}

    document.getElementById('searchInput').addEventListener('input', renderTable);
    renderTable();
</script>

</body>
</html>
"""

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✨ Interactive HTML Report successfully generated: {output_filename}")