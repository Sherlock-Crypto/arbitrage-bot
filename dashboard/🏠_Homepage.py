import streamlit as st


st.set_page_config(page_title='SHERLOCK CRYPTO - Home',  layout='wide', page_icon=':house:')

st.title('Sherlock Crypto arbitrage dashboard')
st.header('Welcome to Sherlock Crypto!')
st.markdown('Sherlock Crypto is a comprehensive tool that allows users to find and analyze crypto arbitrage opportunities on the go.')
st.markdown('**The tool is composed of:**\n'
            '- [**Telegram bot**](https://t.me/ArbitrageScannerBot) \- searches for arbitrage opportunities and sends them to users on a fixed interval \- _30 minutes_\n'
            '- **Database** \- collects all events\n'
            '- **Scanner dashboard** \- helps users search for opportunities manually\n'
            '- **Analytical dashboard** \- gives a thorough overview on both current and historical arbitrage market state')
