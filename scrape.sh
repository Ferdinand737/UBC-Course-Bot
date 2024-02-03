#bash
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip -d chromedriver-linux64
mv chromedriver-linux64/chromedriver .
rm -rf chromedriver-linux64.zip chromedriver-linux64
source venv/bin/activate
pip install -r requirements.txt
python Scrape.py
