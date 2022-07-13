# ml-tradingbot-template
A Template for your Cryptocurrency Trading Bot. 

#### The things you need to get this trading bot working for you:
###### Kraken account (https://www.kraken.com/)
This bot uses Kraken's API to do all the longing and shorting so you need that. You need to pass your Kraken API key and secret to the place where it is inidicated

###### Finnhub API key (https://finnhub.io/)
The bot uses Finnhub's API to get the current price of the cryptocurrency (you can also change this, probably a better way to do this [maybe yfinance])

###### A Working Machine Learning Model
The bot template has separate models for shorting and longing. You can see it in model.py. !BUT DO NOT USE THE TEMPLATE MODELS! They are not great models and you will definitely lose money using them. You must train your own models.

###### A Telegram Bot
This is not mandatory, You can just delete all the lines with `telegram_bot_sendtext("message")`. But it's a super nice feature. You will get automatic messages on Telegram about all the trades. Creating a telegram bot is quite easy, check out this: https://core.telegram.org/bots

That's it!
