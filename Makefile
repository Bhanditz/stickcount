CAFFE_BUILD ?= "/path/to/caffe/build"

.PHONY: all clean data lists db solve

all: clean data lists db mean solve

data:
	python maketraining.py

lists:
	for dir in training test; do \
	    find $$dir -name *.jpg -or -name *.png \
		    | awk 'BEGIN { FS = "/" }; { print $$0" "$$2 }' > $$dir.list; \
	done

db: cleandb
	for dir in training test; do \
		$(CAFFE_BUILD)/tools/convert_imageset -gray -shuffle ./ $$dir.list $$dir.lmdb; \
	done

mean:
	for dir in training test; do \
		$(CAFFE_BUILD)/tools/compute_image_mean $$dir.lmdb $$dir\_mean.binaryproto; \
	done

solve:
	$(CAFFE_BUILD)/tools/caffe train -solver lenet_solver.prototxt


cleandb:
	rm -rf training.lmdb test.lmdb

clean:
	rm -rf test* training*
	rm -rf *.caffemodel *.solverstate
