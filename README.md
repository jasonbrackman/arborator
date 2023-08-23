# Fictus

Fictus generates a fake Tree View to stdout for the purpose of documentation.

Example:
```
from fictus import System

s = System("root")
s.mkfiles(["README.md", "LICENSE.md", ".ignore"])

s.mkdirs("files/docs")
s.mkdirs("files/music")

s.cd("files/docs")
s.mkfiles(["resume.txt", "recipe.wrd"])

s.cd("../../files/music")
s.mkfiles(["bing.mp3", "bang.mp3", "bop.wav"])

s.display()

```
Produces:
```
root\
├─ files\
│  ├─ docs\
│  │  ├─ recipe.wrd
│  │  └─ resume.txt
│  └─ music\
│     ├─ bang.mp3
│     ├─ bing.mp3
│     └─ bop.wav
├─ .ignore
├─ LICENSE.md
└─ README.md
```

The way the Tree is displayed can be manipulated by overriding the Renderer.
The default renderer will display the Tree as simple text.  An alternative
MarkdownRenderer is also included and can be used to override the default.

Example:
```
from arbor import System, MarkdownRenderer 

s = System("root")
s.mkfiles(["README.md", "LICENSE.md", ".ignore"])

# can be overriden at any time before display()
s.renderer = MarkdownRenderer()
  
s.display()
```
Produces:
```
<pre style="line-height:17px">
root\
├─ <span style="color:gray">.ignore</span>
├─ <span style="color:gray">LICENSE.md</span>
└─ <span style="color:gray">README.md</span>
</pre>
```
Custom Renderer classes can be constructed as long as the 
Abstract Renderer class is used.  For example:

```
from arbor import Renderer

class MyCustomRenderer(Renderer):
    ...
```

## Building/installing the Wheel:
To build the package requires setuptools and build.
>python3 -m build

Once built:
>pip install dist/fictus-0.0.1-py3-none-any.whl --force-reinstall