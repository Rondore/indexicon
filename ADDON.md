The addon folder can be used to customize indexicon in some ways. Here are a few examples.

## Adding a new page

To add a new page to Indexicon, we need two parts: the html file and the python code.

For our example, we will put the html file in `addon/templates/about.html` with the following content:

```html
<article>
<h2>Why?</h2>
<p>
    This site is dedicated to finding pictures of cats.
</p>
</article>
```

Next, we need to add the page to the menu bar and set up the function to allow python's flask library to serve the page which we will save as `addon/custom_pages.py`:

```python
#!/usr/bin/env python3

import app as indexicon
from flask import render_template
from app import app, footer, header, nav
from flask import Blueprint
import settings

# append takes [relative url witout first slash, page title, function name]
indexicon.menu_items.append(["about", "About", 'about'])

customBluprint = Blueprint('addon', __name__, template_folder='templates')
app.register_blueprint(customBluprint, url_prefix='/addon')

# route must have the relative url with the first slash
@app.route('/about')
def about():
    output = header('')
    output += '<h1>About ' + settings.name + '</h1>'
    output += nav()
    output += render_template('about.html')
    output += footer()
    return output
```

## Changing the search more box

At the end of the search results is a box with a link to search google for the same search resuls. To customize or remove this box we can replace the function to generate it. Here is an example which adds a yandex search. We will save the python as `addon/search_more.py`:

```python
#!/usr/bin/env python3

import app as indexicon
from flask import Blueprint
from flask import render_template

customBluprint = Blueprint('addon', __name__, template_folder='templates')
app.register_blueprint(customBluprint, url_prefix='/addon')

def search_other_content(raw_search):
    plus_search = raw_search.replace(' ', '+').replace('"', '\"')
    google_search = 'https://www.google.com/search?udm=14&q=' + plus_search
    yandex_search = 'https://yandex.ru/search/?text=' + plus_search

    return render_template('search_other_content.html', google_search=google_search, yandex_search=yandex_search)

indexicon.search_other = search_other_content
```

For this example, we need the matching html file saved as `addon/templates/search_other_content.html`:

```html
<div class="search-help">
    Can&apos;t find it? Try these sources:<br>
    <a target="about:blank" href="{{ google_search }}">Google</a>
    - <a target="about:blank" href="{{ yandex_search }}">Yandex</a>
</div>
```