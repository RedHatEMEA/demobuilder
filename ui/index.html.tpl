% import socket

<!DOCTYPE html>
<html>
<title>Welcome to {{ socket.gethostname() }}!</title>

<script type="text/javascript">
function hideshow(x) {
  if(x.style.display == "block")
    x.style.display = "none"
  else
    x.style.display = "block"
}
</script>

<xmp style="display:none;">
# Available images

% for layer in sorted(layers.values(), key=lambda l: l.yaml["name"]):
## {{ layer.yaml["name"] }}

% if layer.yaml.get("description", ""):
{{ layer.yaml["description"] }}
% end
% for image in layer.images:
* **{{ image["target"].yaml["name"] }} ({{ "%0.2fGB" % (image["size"] / 1e9) }})**

  {{ !image["target"].yaml.get("description", "") }}

  <a href="javascript:hideshow(document.getElementById('{{ image["link"] }}'))">More...</a>

  <div id="{{ image["link"] }}" style="display:none;">

  {{ !image["target"].yaml.get("howto", "") }}

  [Manual download]({{ image["link"] }}) (for advanced users -- only use this if
  not following the instructions above)

% end
% end

# Give feedback

Questions, comments, feature requests, patches, pull requests and cake are all
welcomed on [GitHub](http://github.com/RedHatEMEA/demobuilder) or to
[jminter@redhat.com](mailto:jminter@redhat.com).
</xmp>

<script src="/contrib/strapdown/v/0.2/strapdown.js"></script>

</html>
