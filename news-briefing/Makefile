.PHONY: check test

check:
	python3 -m py_compile news_briefing.py
	bash -n news-briefing.sh

test: check
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_news_briefing
