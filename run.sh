while true
do
	rm -rf clear_logs/*

	python3 -B main.py

	sleep 10
done