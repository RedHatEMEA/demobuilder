#!/usr/bin/python

import glob
import re
import yaml

header = '''<!DOCTYPE html>
<html>
<title>%(title)s</title>

<xmp style="display:none;">
## Description

%(description)s

<!-- HEADER -->'''

footer = '''<!-- FOOTER -->

## VM image maintainer(s)

%(maintainers)s

## Please contribute to this demo!

Questions, comments, bug reports, feature requests, patches, pull requests and
cake are all welcomed on [GitHub](http://github.com/RedHatEMEA/demobuilder) or
to [jminter@redhat.com](mailto:jminter@redhat.com).

If sending a bug report, please include the contents of
[/etc/demobuilder](/etc/demobuilder), as this will indicate the builds that were
used to create the VM image.
</xmp>

<script src="strapdown/v/0.2/strapdown.js"></script>
<script type="text/javascript">
var spans = document.getElementsByTagName('span');
for (var i = 0; i < spans.length; i++) {
  spans[i].className = "pln"
}
</script>

</html>
'''

def main():
    for path in glob.glob("layers/*/@docs/*.html"):
        layer = path.split("/")[1]

        config = yaml.load(open("layers/%s/config.yml" % layer).read())
        maintainers = "\n".join([re.sub("(.*?) <(.*)>", r"- \1 [\2](mailto:\2)", m) for m in config["maintainers"]])

        head = header % {"title": config["name"], "description": config["description"].strip()}
        foot = footer % {"maintainers": maintainers}

        f = open(path).read()

        f = re.sub(".*" + head.splitlines()[-1], head, f, flags=re.S)
        f = re.sub(foot.splitlines()[0] + ".*", foot, f, flags=re.S)

        open(path, "w").write(f)

if __name__ == "__main__":
    main()
