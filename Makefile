CAFFE_HOME ?= "/usr/local/caffe"

.PHONY: all clean data lists db solve

all: clean data lists db solve status

data:
	python maketraining.py

lists:
	for dir in training test; do \
	    find $$dir -name *.jpg -or -name *.png \
		    | awk 'BEGIN { FS = "/" }; { print $$0" "$$2 }' \
	            > $$dir.list; \
	done

db: cleandb
	for dir in training test; do \
            echo converting $$dir; \
	    $(CAFFE_HOME)/bin/convert_imageset -gray -shuffle ./ \
              $$dir.list $$dir.lmdb 2>&1 \
            | awk -v E=$$(tput el) 'BEGIN { ORS="\r" } { print E, $$0 }'; \
            echo; \
	done

mean:
	for dir in training; do \
		$(CAFFE_HOME)/bin/compute_image_mean $$dir.lmdb $$dir\_mean.binaryproto; \
	done

solve:
	$(CAFFE_HOME)/bin/caffe train -solver lenet_solver.prototxt

status:
	python status.py

cleandb:
	rm -rf training.lmdb test.lmdb

clean:
	rm -rf test* training*
	rm -rf *.caffemodel *.solverstate
