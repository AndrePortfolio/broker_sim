# Finance App

A web application that allows users to manage their stock portfolios by buying and selling shares of various stocks. This application provides simmulated stock price information, user authentication, and a historical transaction log.

## Finance App Demonstration
![Description of the photo](https://github.com/AndrePortfolio/finance_app/blob/main/finance_app.png)
You can view the demonstration of the finance app by clicking the link below:
[Watch the Finance App Video](https://github.com/AndrePortfolio/finance_app/blob/main/finance_app.mov)

## Features

- **User Authentication**: Secure login and registration for users.
- **Portfolio Management**: Users can view, buy, and sell stocks in their portfolio.
- **Real-time Price Lookup**: Fetch current stock prices for any listed symbol.
- **Transaction History**: Users can view their transaction history, including timestamps and share details.
- **Responsive Design**: User-friendly interface that works well on both desktop and mobile devices.

## Technologies Used

- **Flask**: A lightweight web framework for Python.
- **SQLite**: A lightweight database to store user data and transaction history.
- **HTML/CSS**: For the front-end user interface.
- **JavaScript**: For client-side interactivity.
- **Bootstrap**: For responsive design and styling.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/finance-app.git
   cd finance-app
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install python@3.10
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   flask run
