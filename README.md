# Automated Kaggle Euromillions Dataset
This repository automates the process of fetching, merging, and updating Euromillions historical data from [Euromillion's official website](https://www.euro-millions.com/). The updated dataset is then uploaded to Kaggle every week using GitHub Actions.

## What It Does and Why
- Weekly Updates: The repository ensures that the euromillions_data.csv dataset is always up to date with the latest data by fetching missing days of Euromillions data from the Euromillion's official website.
- Merges Existing Data: It first downloads the existing dataset from Kaggle, identifies any missing data, fetches it from the Euromillions official website, and then merges it with the existing data.
- Automated Upload: Once the missing data is merged, the updated dataset is automatically uploaded back to Kaggle, ensuring that the dataset remains accurate and complete without manual intervention.