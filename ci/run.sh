curl 'https://public-docs.crg.es/rguigo/Data/mmunoz/pyhist/GTEX-1117F-0126.svs' --output 'GTEX-1117F-0126.svs'
python pyhist.py --patch-size 64 --content-threshold 0.1 GTEX-1117F-0126.svs
