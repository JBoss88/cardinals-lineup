# ⚾ Automated Cardinals Lineup Bot

A serverless Python automation pipeline that fetches the St. Louis Cardinals daily starting lineup via the MLB Stats API and delivers it directly via email.

Built as an end-to-end demonstration of API integration, cloud-based CI/CD scheduling, and state management within stateless environments.

## 🏗️ Architecture & Tech Stack

- **Language:** Python 3.13
- **Data Source:** MLB Stats API (RESTful JSON)
- **Delivery:** Python `smtplib` & `email.message` (Gmail SMTP)
- **CI/CD & Automation:** GitHub Actions (Ubuntu-latest runners)

## 🧠 Engineering Decisions & Edge Case Handling

When migrating this script from a local environment to a cloud-based automated runner, several architectural decisions were made to ensure stability and efficiency:

### 1. Bypassing Cloud Timeout Limits (The Hourly Runner)

Baseball game times vary wildly, and starting lineups are typically posted 2 to 3 hours before first pitch. GitHub Actions has a hard execution limit of 6 hours per job. A standard "sleep and wait" script triggered at noon would timeout and fail before a 9:00 PM West Coast game lineup was posted.

- **Solution:** The workflow runs on an **hourly CRON schedule** (`0 * * 4-10 *`). The script acts as a fast "sprint"—it wakes up, checks the API, and immediately shuts down. If the lineup isn't there, it simply exits and tries again the next hour.

### 2. State Tracking in a Stateless Cloud

Because the script runs every single hour, it needs a way to "remember" if it has already sent an email that day to prevent spamming the user.

- **Solution:** A lightweight state management system using a local text file (`last_sent.txt`). Once a successful email is dispatched, the script writes the current date to this file. The GitHub Action is granted write permissions to commit this file back to the repository. Upon the next hourly run, the script reads this file; if the dates match, it gracefully terminates early.

### 3. Compute Efficiency (Seasonality)

Running an hourly cloud job 365 days a year is a waste of compute resources for a seasonal sport.

- **Solution:** The GitHub Actions workflow is strictly configured to only run during the MLB regular season and postseason (Months 4 through 10).

## 🚀 Setup & Installation (Local Testing)

If you wish to clone this repository and run it locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/cardinals-lineup.git](https://github.com/yourusername/cardinals-lineup.git)
   cd cardinals-lineup
   ```
