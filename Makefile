.PHONY: update_patch update_minor update_major

get_version:
	@python -m utils.bumpversion get_version

patch:
	@python -m utils.bumpversion update_version --part patch

minor:
	@python -m utils.bumpversion update_version --part minor

major:
	@python -m utils.bumpversion update_version --part major
