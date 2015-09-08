test:
	nosetests -x --pdb --pdb-failures --detailed-errors --nologcapture 
bdd:
	behave --stop --logging-level=ERROR

clean:
	-find . -name '*.pyc' -print0| xargs -0 rm
	-find . -name '*.un~' -print0| xargs -0 rm
	-find . -name '*.swp' -print0| xargs -0 rm
	-find . -name '__pycache__' -print0| xargs -0 rm -rf
