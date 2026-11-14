# Automated Kaggle EuroMillions Historical Data

This repository automates the process of fetching, merging, and updating Euromillions historical data from [Euromillion's official website](https://www.euro-millions.com/) to a [dataset on Kaggle](https://www.kaggle.com/datasets/duartepereiradacruz/euromillions-historical-data).  The process runs entirely within GitHub Actions, ensuring the dataset remains fresh without any manual intervention.

## What It Does and Why
This project is designed to maintain the integrity and currency of the euromillions.csv dataset by performing three key actions automatically:
- Downloads Existing Data: The workflow first downloads the latest version of the dataset from Kaggle.
- Scrapes and Merges Missing Draws: It then scrapes the latest draws from the EuroMillions official website for the current year, identifies any dates missing from the existing Kaggle file, and merges the new data seamlessly.
- Automated Upload: Finally, the updated, merged file is uploaded back to Kaggle as a new dataset version using the Kaggle API.

This fully automates the data pipeline, moving the dataset from static to dynamically maintained.

## Workflow Overview
The core automation is handled by a GitHub Actions workflow that executes the dataset_updater.py script.

## Schedule
The update process runs automatically Twice a Week to ensure timely data ingestion:
- Every Tuesday at 23:00 UTC
- Every Friday at 23:00 UTC

The workflow can also be triggered manually via the "workflow_dispatch" button in the GitHub Actions tab.

## Technology Stack
- Python: The core scripting language.
- Libraries: requests and beautifulsoup4 for web scraping, pandas for data merging and manipulation, and kaggle for API interaction.
- Automation: GitHub Actions, with a Cloudflare Worker proxy for scraping.

## Setup and Configuration (For Contributors)
To run this automation, you must configure your Kaggle credentials securely within your GitHub repository.

### Generate Kaggle API Key:
- Go to your Kaggle Account settings.
- In the API section, click Create New API Token. This will download a kaggle.json file.

### Add GitHub Secrets:
In your GitHub repository, go to Settings > Security > Secrets and variables > Actions.
- Click New repository secret and add the following two secrets, using the values from your kaggle.json file:
- KAGGLE_USERNAME: Your Kaggle username.
- KAGGLE_API_KEY: Your Kaggle API key (the value of the key field).

The workflow will use these secrets to authenticate and update the dataset on Kaggle.

### Scraping Proxy (Cloudflare Worker)
euro-millions.com blocks GitHub-hosted runner IPs, so the workflow fetches the results pages through a small Cloudflare Worker in [`proxy/`](proxy/). The Worker only serves `results-history-<year>` pages and requires a shared token.

Deploy it once (requires a free Cloudflare account):
```bash
cd proxy
npx wrangler login
npx wrangler deploy
TOKEN=$(openssl rand -hex 32)
echo "$TOKEN" | npx wrangler secret put PROXY_TOKEN
echo "$TOKEN"
```

Then add two more repository secrets:
- SCRAPE_PROXY_URL: the `https://<name>.<subdomain>.workers.dev` URL printed by `wrangler deploy`.
- SCRAPE_PROXY_TOKEN: the token printed above (run `unset TOKEN` afterwards).

If these secrets are not set, the script connects to the site directly. If the site cannot be reached, the run ends with a "Scrape skipped" warning and no upload; the next successful run picks up every missed draw, since it re-reads the whole year's results page.

## Ignored Files
The large .csv files generated and downloaded during the update process are intentionally kept out of Git history via the .gitignore file:
- upload/
- .wrangler/ (Wrangler's local cache for the proxy)

This keeps the repository lightweight, as the data itself is version-controlled by Kaggle.

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
