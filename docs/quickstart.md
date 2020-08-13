### Using the Docker image<a name="usedocker"></a>
PyHIST can be directly executed using Docker.
```shell
docker run mmunozag/pyhist --help
```

To mount a local folder `/path_with/images/` mapping to the folder `/pyhist/images/` inside the container, use the `-v` flag specifying the absolute path of the local folder. 
```shell
docker run -v /path_with/images/:/pyhist/images/ mmunozag/pyhist [args]
```

Optionally, if you want to ensure that all the generated output files are written with permissions belonging to the current host user (instead of `root`, which is Docker's default), specify the username and group with the `-u` flag (retrieval of both can be automated with `id` ), as well mapping the `passwd` file with a second `-v` flag: 
```shell
docker run -v /path_with/images/:/pyhist/images/ \
	-u $(id -u):$(id -g) \ 
	-v /etc/passwd:/etc/passwd \
	mmunozag/pyhist [args]
```

A working example to process an image called `test.svs` located inside `/path_with/images/`:
```shell
docker run -v /path_with/images/:/pyhist/images/ \
	-u $(id -u):$(id -g) \
	-v /etc/passwd:/etc/passwd \
	mmunozag/pyhist --save-tilecrossed-image --output images/ images/test.svs
```

### Using PyHIST<a name="usescript"></a>
PyHIST can be directly executed as a script. To see all available options:
```
python pyhist.py --help
```

A working example to process an image called `test.svs` located inside `/path_with/images/`:
```
python pyhist.py \
	--content-threshold 0.05 \
	--patch-size 64 \
	--output-downsample 16 \
	--info "verbose" \
	--save-tilecrossed-image\
	/path_with/images/test.svs
```