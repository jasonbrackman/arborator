## Fictus

Use `Fictus` to create and output a fictitious file system for sharing in a text driven format.

```Text
🏡kitchen:\
└─ 📁drawer
   ├─ 📁forks
   │  ├─ 📁old
   │  │  └─ 📄pitchfork.bak
   │  ├─ 📄dinner.mp3
   │  └─ 📄salad.mov
   └─ 📁spoons
      └─ 📄ladle.psd
```

Use cases include creating output for a wiki page, communicating a folder structure to a colleague over chat, or
mocking a file/folder structure layout before committing to actual creation on disk.  Since Fictus mimics a File System,
calling code can create complex loops to build up as little or as much as required to get an idea across.

If needed the virtual file system can be used to create a physical representation on the physical disk.
<HR>

### FictusFileSystem
A Fictus File System starts with instantiating a FictusFileSystem object and, optionally, providing
a root drive name.  If one is not provided, a single slash ('/') will be used.

```Python
from fictus import FictusFileSystem

# Create a FictusFileSystem.
ffs = FictusFileSystem("c:")
```

The object can then be built up using creation methods, such as `mdir` and `mkfile` and folder traversal can occur
using `cd`.


```Python
# create some directories
ffs.mkdir("/files/docs")
ffs.mkdir("/files/music/folk")

# Create some files in the current working directory (happens to be root).
ffs.mkfile("README.md", "LICENSE.md", ".ignore")

# Change directory to the `docs` and make more files. Start with `/` to traver from root.
ffs.cd("/files/docs")
ffs.mkfile("resume.txt", "recipe.wrd")

# Change directory to `music/folk`.  Note the relative cd from the `docs` folder. 
ffs.cd("../music/folk")
ffs.mkfile("bing.mp3", "bang.mp3", "bop.wav")
```
<HR>

A FictusFileSystem can also be generated based on a real world drive setup. If needed, additional
edits can be made after to add or rename data.

```Python
from pathlib import Path  # this class method requires a Path object

from fictus import FictusFileSystem

local_path = Path(r"c:\temp")
ffs = FictusFileSystem.init_from_path(local_path)
```
<HR>

### FictusDisplay
A FictusDisplay outputs the FFS.

```Python

from fictus import FictusDisplay

ffs.cd("/")  # for this example, ensure the cwd is the root of the file system

# Generate a ffs structure to be printed to stdout as text.
display = FictusDisplay(ffs)
display.pprint()
```

Produces:

```Text
c:\
├─ files\
│  ├─ docs\
│  │  ├─ recipe.wrd
│  │  └─ resume.txt
│  └─ music\
│     └─ folk\
│        ├─ bang.mp3
│        ├─ bing.mp3
│        └─ bop.wav
├─ .ignore
├─ LICENSE.md
└─ README.md
```

The display can also be generated in place:

```Python
FictusDisplay(ffs).pprint()
```

The tree displayed starts at current working directory. The same example
above with the current directory set to `c:/files/music` produces:

```Text
music\
└─ folk\
   ├─ bang.mp3
   ├─ bing.mp3
   └─ bop.wav
```

The display can also be used to generate a physical representation of the Fictus File System. 

```Python
from pathlib import Path
path = Path("c:\\fictus")
FictusDisplay(ffs).reforestation(path)
```

This creates the folders and empty `utf-8` files represented by the current FFS subtree under the provided `path`.
Existing directories are reused, but existing files are protected by default. To intentionally replace existing files,
pass `overwrite=True`. Names that could escape the destination (for example `../file`) are rejected.
<HR>

### Renderer
A FictusDisplay allows customization of the `DOC`, `ROOT`, `FOLDER`, and `FILE` types.
The Renderer can be permanently reassigned using the `renderer` property. Here is an
example that takes advantage of the built-in `emojiRenderer`.  

```Python
from fictus.renderer import emojiRenderer
...
# FictusDisplay the ffs structure after a relative change of directory to files/music
ffs.cd("files/music")

# assign a new Renderer to the display - already instantiated in a previous example.
display.renderer = emojiRenderer

# ouptut with the new Renderer applied
display.pprint()
```

This produces:

```Text
📁music
└─ 📁folk
   ├─ 📄bang.mp3
   ├─ 📄bing.mp3
   └─ 📄bop.wav
```

Previously, the `renderer` was updated so that each call to `pprint` will use
the `emojiRenderer`. If the main renderer is not required to be updated permanently, 
use the `pprint` optional argument - `renderer`.

```Python
from fictus.renderer import defaultRenderer
# current renderer is the emojiRenderer

# uses defaultRenderer just this one time
display.pprint(renderer=defaultRenderer)  

# use the emojiRenderer that was setup in the previous example set.
display.pprint() 
```

<HR>

### RenderTag Customization
Customization may be useful for creating HTML, Markdown, or other custom tags that are
not already provided. A `Renderer` can register valid `RenderTagEnum` types with 
`RenderTag` objects.   By default, all `RenderTags` contain empty strings. The user
can choose to override any number of tags as required.

You can create a new `Renderer` from scratch and customize the `RenderTag`s that are 
appropriate. For example:

```Python
from fictus.renderer import RenderTagEnum, RenderTag

# A customRenderer is created: adds special characters before a File or Folder.
customRenderer = Renderer()
customRenderer.register(RenderTagEnum.FILE, RenderTag("· ", ""))
customRenderer.register(RenderTagEnum.FOLDER, RenderTag("+ ", "\\"))

# Update display_model to the customRenderer
display.renderer = customRenderer
display.pprint()
```

Produces:

```Text
+ music\
└─ + folk\
   ├─ · bang.mp3
   ├─ · bing.mp3
   └─ · bop.wav
```

One can also create a new `Renderer` object starting with an already applied object and 
updating only the Enum value of interest.

```Python
new_renderer = (
    display.renderer
)  # from previous examples -- this will return customRenderer
new_renderer.register(RenderTagEnum.FOLDER, RenderTag("✓ ", ""))
display.pprint(renderer=new_renderer)
```

And this will, as expected, generate the following:
```
✓ music
└─ ✓ folk
   ├─ · bang.mp3
   ├─ · bing.mp3
   └─ · bop.wav
```

<hr>

### Install Using Pip
>pip install fictus

### Building/installing the Wheel locally:
To build the package requires setuptools and build.
>python3 -m build

Once built:
>pip install dist/fictus-*.whl --force-reinstall
