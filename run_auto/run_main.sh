mkdir -p /media/sdcard/code/Engineering-innovation-competition-vision/run_log
touch /media/sdcard/code/Engineering-innovation-competition-vision/run_log/output.log
touch /media/sdcard/code/Engineering-innovation-competition-vision/run_log/error.log

/media/sdcard/miniconda3/envs/EIC/bin/python /media/sdcard/code/Engineering-innovation-competition-vision/main.py --deal_method hide --config_path /media/sdcard/code/Engineering-innovation-competition-vision/config.json> /media/sdcard/code/Engineering-innovation-competition-vision/run_log/output.log 2> /media/sdcard/code/Engineering-innovation-competition-vision/run_log/error.log