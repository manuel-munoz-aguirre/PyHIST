curl 'https://public-docs.crg.es/rguigo/Data/mmunoz/pyhist/test.svs' --output 'test.svs'
python pyhist.py --patch-size 64 --content-threshold 0.1 test.svs
