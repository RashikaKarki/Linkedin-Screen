# Linkedin Screener

Web application with integrated web scraper that finds potential bio-technology founders profiles from linkedin.

## TechStacks Used

- **Web application**: Flask Framework 
- **Web scraping framework**: Selenium, Beautiful Soup
- **Database**: SQLite 
- Celery and Redis engine is used to make the application asynchronous

## Installation

Install the packages as per the requirements.txt 

The script is Python 3 + compatible.

```bash
pip3 install -r requirements.txt
```

### Running the application locally
**Flask Application**
```python
set FLASK_APP=main.py
flask run
```

The flask application will run at port:5000


**Celery** 


Before running celery make sure that Redis server is running at port:6379

```bash
celery -A main.celery worker -l info -P gevent
```
