run:
	uvicorn main:app --reload

prune.remote.branches:
	git remote prune origin
