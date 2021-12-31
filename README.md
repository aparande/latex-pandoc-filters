# LaTeX Pandoc Filters

This repository contains filters which can be used with the
[pandocfilters](https://github.com/jgm/pandocfilters) library to convert LaTeX
into Markdown via [pandoc](https://pandoc.org).

# Usage
Each filter is a callable object which acts like an action from
[pandocfilters](https://github.com/jgm/pandocfilters). Each filter should have
a single purpose. For complex transformations, you can cascade multiple filters
together.

To write your own filter, simply subclass `filters.PandocFilter` and implement
`__call__`. The `__call__` method accepts the same arguments as an action from
[pandocfilters](https://github.com/jgm/pandocfilters). These arguments are
- `key`: A string representing what type of Pandoc object the element is
- `value`: The content of the object
- `fmt`: A string containing the output format of the filter (latex, html, etc).
- `meta`: Document metadata

Each subclass of `filters.PandocFilter` should take in `config`, which is a
dictionary that can configure the filter, and an instance of `PandocState`.

For examples, see the `filters` module. For an example of how to use this
package in practice, see my
[BerkeleyNotes](https://github.com/aparande/BerkeleyNotes/blob/master/pandoc_filter.py)
repository.

# Filter State
When cascading filters, information sometimes needs to be persisted between each
filter. A good example of this is with labels and their references.
`PandocState` is used to keep track of this information. Currently, it only
keeps track of label information. To add more information to state, subclass
`PandocState`.

