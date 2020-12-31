# some-ZNO-statistics
Some experiments with ZNO-related data to practice the Python Data Science stack

# Notebooks
* `is-shortest-wrong.ipynb` - a little research that tests hypothesis about the shortest test options.

# Used Data & Data Collectors
### Dataset of tasks with options and correct answers
* `data/ukrainian_questions_dataset.csv` - ZNO in ukrainian language and literature 2006-2020 years tasks 
* `questions_webscrapper.py` - script that was used to collect that data. I prefer not to say what site I used to collect data, so original `questions_webscrapper_config.py`
file required to start this script is not provided. If you know the site url you can recreate it by yourself.

### Anonymized data of ZNO participants and their works
[Official data](https://zno.testportal.com.ua/opendata) from Ukrainian Center for Educational Quality Assessment about all the ZNO works from 2016-2020 years.
Variables description can be found on the official site too.\
Due to its size it cannot be uploaded to GitHub. But there is `opendata_downloader.py` which downloads datasets and combines them into
sqlite database located at `data/opendata.sqlite3`. If you run it, expect that process takes about one hour and the resulting database will be around 4.2GB.


