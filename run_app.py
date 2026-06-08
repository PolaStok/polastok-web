import sys
import asyncio
import streamlit.web.cli as stcli

# Memaksa Windows menggunakan Event Loop yang stabil
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == '__main__':
    # Ini sama dengan mengetik "streamlit run PolaStok.py" di terminal
    sys.argv = ["streamlit", "run", "PolaStok.py"]
    sys.exit(stcli.main())
