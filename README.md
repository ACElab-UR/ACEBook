# Animal Comparative Economics Book

This repository contains the source code for the **ACEBook** - ACElab's online JupyterBook.

All code in this project was written in and tested with R 3.xx and Python 3.xx, though older language versions (including R 2.xx and Python 2.7) should work in most cases.

## Usage

### Building the book

If you'd like to develop and/or build the ACEBook, you should:

- Clone this repository
- `cd` to it and run `pip install -r requirements.txt` (it is recommended you do this within a virtual environment - i.e. conda)
- (Recommended) Remove the existing `ACEBook/content/_build/` directory
- Run `jupyter-book build ...` (more on this below)

A fully-rendered HTML version of the book will be built in `ACEBook/_build/html/`.

### Hosting/Deploying the book online

The html version of the book is hosted on the `gh-pages` branch of this repo, which is then rendered on [link](link). 

The following workflow is used to build the book manually:

- Make changes to the book's content on the master branch of this repository
- Re-build the book with `jupyter-book build content` (assumes you are running the command from *root* directory of the repository)
- Ensure that an HTML has been built for each page of your book. There should be a collection of HTML files in the `content/_build/html` folder. Also load `_build/html/notebooks/index.html` and check that the book has been built (with navigation etc.) as expected. 
- Run `ghp-import -n -p -f content/_build/html` to deploy the book.
 
The last command will automatically push the latest build to the `gh-pages` branch. More information on this hosting process can be found [here](https://jupyterbook.org/publish/gh-pages.html#manually-host-your-book-with-github-pages).

Typically after a few minutes the site should be viewable online at [link](link). If not, check repository settings under Options -> GitHub Pages to ensure that the gh-pages branch is configured as the build source for GitHub Pages.

An example command to push all new changes to the git repository is:

`git add -A && git commit -m "Commit message" && git push -u origin master`

**Please do not push changes for every little edit you make to the book (e.g., after fixing some typos)**. Push only significant changes. Remember, you can deploy the book (by pushing to the `gh-pages` branch using `ghp-import` as explained above) without pushing changes to the `master` branch.

## Other tips:

* Read the [Jupyter Book](https://jupyterbook.org/intro.html) - This is short and to the point and addresses all of the key tools and guidelines succinctly 

* If you want to remove a particular cell from the rendered book [see this](https://jupyterbook.org/interactive/hiding.html#removing-code-cell-content)
  
* If you want to remove a cell when exporting a Jupyter Notebook (outside of Jupyter Book), say as an html, add 
 ```json
    {
    "tags": [
        "remove_cell"
        ]
    }
```
to the metadata of the cells that you want to remove from the output, and then run: 
  ```bash
  jupyter nbconvert younotebookname.ipynb --TagRemovePreprocessor.enabled=True --TagRemovePreprocessor.remove_cell_tags="['remove_cell']" --to html
  ```
  (`html` can be replaced with another export format, such as `pdf`). Read the [`nbconvert` documentation](https://nbconvert.readthedocs.io/en/latest/index.html) for more on exporting/converting.

## Contributors

Henrique Galante | henrique.galante@ur.de

## Credits

This project is created using the excellent open source [Jupyter Book project](https://jupyterbook.org/) and the [executablebooks/cookiecutter-jupyter-book template](https://github.com/executablebooks/cookiecutter-jupyter-book).