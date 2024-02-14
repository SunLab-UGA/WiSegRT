GPU=
ifdef gpus
    GPU=--gpus=$(gpus)
endif
export GPU

doc: FORCE
	cd doc && ./build_docs.sh

docker:
	docker build -t sionna -f DOCKERFILE .

install: FORCE
	pip install .

lint:
	pylint sionna/

run-docker:
	docker run -itd -v {write_your_path_here}:/tf/WiSegRT -u $(id -u):$(id -g) -p 8887:8888 --privileged=true $(GPU) --env NVIDIA_DRIVER_CAPABILITIES=graphics,compute,utility sionna  

test: FORCE
	cd test && pytest

FORCE:
