.PHONY: check test

check:
	python -m py_compile scene.py
	python -m json.tool scene.example.json >/dev/null

test: check
	./tests/test_scene.sh
