# MarketLens
AI-assisted market analysis and paper-trading platform for beginner investors.

## 1. THE DEMO
I open MarketLens in the browser as a beginner investor with little knowledge of financial markets and select the Balanced profile with a virtual starting balance of $10,000. The dashboard shows current market views for US Equities, US Government Bonds, and Gold, each with a forecast direction, confidence score, risk level, and a short explanation written for non-expert users. I apply the suggested model allocation to the virtual portfolio, which is then tracked using real market prices and shows how much the simulated investment gains or loses over time. I open Model History and compare earlier forecasts with actual market outcomes, including incorrect predictions. The system stores these forecast errors and uses them during periodic model retraining so that later model versions can be evaluated against earlier ones.

## 2. The shape

in     continuously updated real-world market data for US equities,
       US government bonds, and gold; a selected investor profile
       and a user-defined virtual starting balance

out    a simulated portfolio allocation, forecast signals with confidence scores,
       and continuously tracked virtual profit or loss based on actual market prices

on screen   the user chooses a risk profile and enters how much virtual money
            to invest, reviews simplified market signals and explanations,
            applies a suggested allocation to the virtual portfolio, and watches
            the portfolio change as new market data arrives. The user can later
            compare earlier forecasts with the actual market outcome.

## 3. The size

### First useful version

- The user selects a beginner investor profile and enters a virtual starting balance.
- MarketLens uses real-world market data for US equities, US government bonds, and gold.
- The system produces forecast signals with confidence scores and simple explanations.
- The user can apply a suggested model allocation to a virtual portfolio.
- The portfolio is tracked using updated real market prices and shows simulated profit or loss.
- Previous forecasts are stored and compared with actual market outcomes.
- The system measures forecast performance and supports periodic model retraining based on past prediction errors.

### Not this term

- Trading with real money.
- Connecting to brokerage accounts.
- Automatically executing real trades.
- Paid subscriptions or payment processing.
- Regulated personalized investment advice.
- Full options and futures trading.
- High-frequency or tick-by-tick real-time market data.
- Support for every global market and asset class.

## 4. How we would know it works

- Given incomplete or malformed market data, the system does not create a forecast and reports which required data is missing.
- Given a stored forecast and the corresponding later market data, the system calculates whether the forecast direction was correct and updates the model performance statistics.
- Given a virtual portfolio and a new market price, the displayed portfolio value and profit or loss change consistently with that price movement.

## 5. What could stop this

- Reliable and affordable market data may be limited. Some providers offer delayed data or restrict real-time access, so the first version may use continuously updated but not tick-by-tick market prices.
- Building a forecasting model that performs better than simple baselines may be difficult. The project still works if the model's limitations are measured honestly and displayed to the user.
- News and macroeconomic data can be difficult to collect consistently and may introduce noise, so these may be added only after the core price-based forecasting system works.
- The model must avoid look-ahead bias: when evaluating a historical prediction, it must only use information that would have been available at the time of that prediction.
- Financial markets change over time, so a model that works well on historical data may perform worse in new market conditions. Performance therefore has to be tracked continuously.
- The project will not use real customer money or connect to brokerage accounts during the course, so there is no need to store real banking or brokerage credentials.

### Data

The project will use publicly available or API-provided historical and current market data for equities, government bonds, and gold. The data will consist of market prices, volumes, and related financial indicators rather than personal or sensitive user information. A small sample dataset will be stored in the repository so the application can be demonstrated in class even if an external data provider is temporarily unavailable.

