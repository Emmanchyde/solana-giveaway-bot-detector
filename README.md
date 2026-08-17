SybilClean V2

Solana Giveaway Sybil Detection

Find suspicious participants before you distribute your rewards.

SybilClean V2 is a local analysis tool built specifically for Solana giveaways, airdrops, quests, and community campaigns on X/Twitter.

It analyzes participant data and combines wallet analysis, account behavior, comment similarity, activity patterns, and Solana on-chain information to identify entries that deserve a closer look.

It can also check whether a participant's wallet actually holds your project's Solana token.

🚨 The Problem

Running a Solana giveaway can attract hundreds or thousands of participants.

Some may:

Enter with multiple accounts

Reuse the same wallet

Submit invalid wallets

Copy other participants' comments

Create groups of accounts that participate within seconds of each other

Use wallets with little or no meaningful history

Enter a token-holder giveaway without actually holding the project token

Manually checking all of this is difficult.

SybilClean automates these layers of investigation.

🔍 What SybilClean Checks

👛 Wallet Analysis

Detect potentially suspicious wallet relationships and activity:

Duplicate/reused wallets

Invalid Solana wallet addresses

Multiple wallets associated with the same handle

Transaction count

SOL balance

Approximate wallet creation information

💬 Comment Analysis

Identify potentially coordinated participation:

Duplicate comments

Highly similar comments

Very short comments

Repeated phrases and patterns

Comment similarity is powered by RapidFuzz.

⚡ Activity Analysis

Look for unusual participation bursts.

For example, a large number of accounts appearing within a very short period can be flagged as a potential coordination signal.

🪙 Project Token Verification

This is one of SybilClean's most useful Solana-specific features.

If your giveaway requires participants to hold your token, SybilClean can check whether their submitted wallets actually hold the specified project token.

You provide the token's Solana mint/contract address, and SybilClean checks participant wallets against it.

This can help answer:

"Does this participant actually hold our token?"

This information can then appear in the audit results alongside the participant's other risk signals.

🧠 Risk Scoring

SybilClean combines multiple signals into a participant risk score.

Score

Risk

0–29

🟢 LOW

30–59

🟡 MEDIUM

60–100

🔴 HIGH

Example:

@participant123

Risk Score: 82
Risk Level: HIGH

Reasons:
• Wallet reused by another participant
• Highly similar comment
• Activity burst detected
• Wallet does not hold project token

A high score does not automatically mean an account is fraudulent.

SybilClean is designed to help campaign operators identify entries that deserve further investigation.

📊 What You Get

After processing a campaign, SybilClean can produce:

Participant-level risk scores

LOW / MEDIUM / HIGH classifications

Duplicate-wallet detection

Invalid-wallet detection

Account/handle analysis

Comment similarity analysis

Duplicate-comment detection

Activity-burst detection

SOL balance

Transaction count

Approximate wallet creation information

Project-token holding status

CSV results

Interactive HTML audit report

🖥️ Interactive Audit Report

SybilClean can generate a standalone HTML dashboard that makes the results easier to review.

The report can show information such as:

Participant
Wallet
Risk Score
Risk Level
SOL Balance
Transaction Count
Wallet Creation Information
Project Token Status
Verification Status
Risk Reasons

The generated HTML report can be opened directly in your browser, we've attached a sample saved as sample_report.html.

🔗 How It Works

X/Twitter Giveaway
        ↓
Participant Data
        ↓
      SybilClean
        ↓
┌──────────────────────────────┐
│ Wallet Analysis              │
│ Account Analysis             │
│ Comment Analysis             │
│ Activity Analysis            │
│ Solana On-Chain Analysis     │
│ Project Token Verification   │
└──────────────────────────────┘
        ↓
    Risk Scoring
        ↓
┌──────────────────────────────┐
│ CSV Results                  │
│ HTML Audit Dashboard         │
└──────────────────────────────┘

🚀 Installation

1. Install Python


2. Install dependencies

pip install -r requirements.txt

If your operating system prevents normal pip installation, use a virtual environment:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

⚙️ Configuration

Helius API Key

SybilClean uses Helius for optional Solana on-chain enrichment.

Open:

Helius.py

Find:

YOUR_API_KEY_HERE

Replace it with your own Helius API key, you can sign up on Helius.dev, their free tier requires no credit card offers a generous amount of credits, suitable for analyzing multile campaigns.



🪙 Project Token

To check whether participant wallets hold a specific Solana token, open:

config.py

At the project-token setting near the end of the file, enter the token's Solana mint/contract address.

For example:

PROJECT_TOKEN_ADDRESS = "YOUR_TOKEN_MINT_ADDRESS"

Replace the placeholder with your project's token mint address.

SybilClean will then check participant wallets against that token.

Important: Holding or not holding a token is only one signal. It does not by itself prove that a participant is legitimate or fraudulent.

📥 Participant Data

SybilClean analyzes participant data supplied in CSV format.

A sample CSV is included in the repository in the data folder so you can see the expected structure and fields.

The analysis engine expects information such as:

Handle

Wallet

Comment

Timestamp

Verification status

▶️ Running an Audit

Once your participant CSV and configuration are ready:

Run the file run_audit.py in your code editor

SybilClean will:

Load the participant data

Analyze wallets

Analyze account behavior

Compare comments

Detect activity patterns

Optionally query Solana data through Helius

Check project-token holdings

Calculate risk scores

Generate the results

You can test sybilclean by running run_audit.py on the file in the current data folder after you have obtained your free Helius API Key, if you already have your own csv file with the format , paste it in the data folder and paste the path in possible_paths in run_audit.py (line 110). 

📁 Output

The audit produces machine-readable results as well as a human-friendly report.

CSV Results
     +
HTML Audit Report

The CSV can be used for further analysis, filtering, or campaign management.

The HTML report provides a visual overview of the participants and their risk signals.

🎯 Who Is This For?

SybilClean is designed for:

Solana projects

Solana giveaway organizers

Airdrop teams

Web3 community managers

Crypto marketing agencies

Campaign operators

Token projects

Web3 security researchers

If you're distributing tokens or rewards to a large number of participants, SybilClean can help you investigate the entries before rewards go out.

🆓 Free & Open Source

The SybilClean analysis engine is available here for developers and campaign operators to use and experiment with.

You can run it locally and configure it for your own campaigns.

🛠️ Need Participant Data Collected?

SybilClean analyzes participant data once it is available in the required format.

If you have a specific X/Twitter Solana giveaway and don't want to handle participant collection yourself, I can provide participant extraction as a separate service.

I can help with:

Participant extraction

Send me the giveaway URL and I can provide the participant data in a format ready for SybilClean.

Full campaign audit

I can also discuss handling the complete workflow:

Giveaway URL
     ↓
Participant Collection
     ↓
SybilClean Analysis
     ↓
Risk Results
     ↓
HTML Report

Contact

Telegram:
https://t.me/emmanchyde

X:
https://x.com/emman_chyde

Github:
https://github.com/emmanchyde


📜 License

See the repository license for the terms governing use, modification, and distribution.

Built for Solana Campaigns

Analyze the participants.
Investigate the wallets.
Check the token.
Find the entries that deserve a closer look.
If you want to configure Sybilclean for another social media platform, feel free to reach out to me.

SybilClean V2
