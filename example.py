from pathlib import Path
from tempfile import TemporaryDirectory

from fictus import FictusDisplay, FictusFileSystem, Renderer
from fictus.renderer import emojiRenderer, RenderTag, RenderTagEnum

# Create a FictusFileSystem.
ffs = FictusFileSystem("c:")

# Create some files in the current working directory.
ffs.mkfile("README.md", "LICENSE.md", ".ignore")

# Create dir and files relative to the current working directory.
ffs.mkdir("./files/docs")
ffs.cd("./files/docs")
ffs.mkfile("resume.txt", "recipe.wrd")

# Create/Change dir to music. Start with a `/` to ensure traversal from _root.
ffs.mkdir("/files/music/folk")
ffs.cd("/files/music/folk")
ffs.mkfile("bing.mp3", "bang.mp3", "bop.wav")

# Generate a ffs structure to be printed to stdout as text.
ffs.cd("\\")  # jump to _root

display = FictusDisplay(ffs)
display.pprint(renderer=emojiRenderer)

# FictusDisplay the ffs structure after a relative change of directory to files/docs
ffs.cd("files/music")
display.pprint()

# Update the display to use emojiRenderer from its defaultRenderer and pprint again.
# Note how this is a one time emojiRenderer.  Calling pprint() again without the
# renderer optional value will result in the defaultRenderer being used.
display.pprint(renderer=emojiRenderer)

# Create a customRenderer, apply it to a FictusDisplay and update the ffs to use it.
customRenderer = Renderer()
customRenderer.register(RenderTagEnum.FILE, RenderTag("· ", ""))
customRenderer.register(RenderTagEnum.FOLDER, RenderTag("+ ", "\\"))

# Update display to the customRenderer permanently. Each call to pprint() will use the
# customRenderer unless the optional renderer is passed in like the emoji example above.
display.renderer = customRenderer
display.pprint()

new_renderer = (
    display.renderer
)  # from previous examples -- this will return customRenderer
new_renderer.register(RenderTagEnum.FOLDER, RenderTag("✓ ", ""))
display.pprint(renderer=new_renderer)

# Create an FFS from a real directory. This temporary tree keeps the example
# portable: it does not depend on a path from the machine running it.
with TemporaryDirectory() as temp:
    source = Path(temp)
    (source / "docs").mkdir()
    (source / "README.md").write_text("", encoding="utf-8")
    (source / "docs" / "guide.md").write_text("", encoding="utf-8")

    imported_ffs = FictusFileSystem.init_from_path(source)
    FictusDisplay(imported_ffs).pprint()
