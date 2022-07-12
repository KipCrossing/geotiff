# Contributing

If you would like to contribute to this project, please fork this repo and make a PR with your patches.

You can join the conversation by saying "hi" in the [project discussion board](https://github.com/KipCrossing/geotiff/discussions).

## Code compliance

To help users and other contributors, be sure to:
- Make documentation blocks, as needed.
- Use static typing wherever possible.
- Format code with `black`.

*Note:* The continuous integration has lint checking with **mypy**, so be sure to check it yourself before making a PR.

To help with code compliance, we strongly suggest that contributors use `pre-commit`, an automatic git hook runner
for ensuring that code meets compliance standards. It can be installed as follows:

> $ cd geotiff
>
> $ pip install pre-commit
>
> $ pre-commit install

This will run all existing code compliance checks automatically whenever committing to the repo.
