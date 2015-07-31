% import socket

<html>

<head>
  <title>Welcome to {{ socket.gethostname() }}!</title>
</head>

<body>
  <h1>Welcome to {{ socket.gethostname() }}!</h1>

  <h2>Available images</h2>
  <ul>
    % for layer in layers.values():
    <h3>{{ layer.yaml["name"] }}</h3>
    % if layer.yaml.get("description", ""):
    <p>{{ layer.yaml["description"] }}
    % end
    <ul>
      % for image in layer.images:
      <li><b>{{ image["target"].yaml["name"] }}</b>
      % if image["target"].yaml.get("description", ""):
      <p>{{ !image["target"].yaml.get("description", "").replace("\n", "<br>") }}
      % end
      <p><a href="{{ image["link"] }}">Download</a> ({{ "%0.2fGB" % (image["size"] / 1e9) }})
      % end
    </ul>
    % end
  </ul>

  <h2>Give feedback</h2>
  <ul>
    Questions, comments, feature requests, patches, pull requests and cake are all welcomed on <a href="http://github.com/RedHatEMEA/demobuilder">GitHub</a> or to <a href="mailto:jminter@redhat.com">jminter@redhat.com</a>.
  </ul>

</body>

</html>
