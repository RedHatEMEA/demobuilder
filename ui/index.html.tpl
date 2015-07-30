% import socket

<html>

<head>
  <title>Welcome to {{ socket.gethostname() }}!</title>
</head>

<body>
  <h1>Welcome to {{ socket.gethostname() }}!</h1>

  % if releases_table:
  <h2>Release images</h2>
  <ul>
    <table border=1>
      <tr>
        <th></th>
        % for target in targets:
        <th valign="bottom" width="150">{{ target }}</th>
        % end
      </tr>
      % for row in releases_table:
      <tr>
        <th align="right">{{ row[0] }}</th>
        % for item in row[1:]:
        <td align="center">
          % if item:
          <a href="{{ item[0] }}">download</a> ({{ "%0.2fGB" % (item[1] / 1e9) }})
          % end
        </td>
        % end
      </tr>
      % end
    </table>
  </ul>
  %end

  % if build_table:
  <h2>Development images</h2>
  <ul>
    <table border=1>
      <tr>
        <th></th>
        % for target in targets:
        <th valign="bottom" width="150">{{ target }}</th>
        % end
      </tr>
      % for row in build_table:
      <tr>
        <th align="right">{{ row[0] }}</th>
        % for item in row[1:]:
        <td align="center">
          % if item:
          <a href="{{ item[0] }}">download</a> ({{ "%0.2fGB" % (item[1] / 1e9) }})
          % end
        </td>
        % end
      </tr>
      % end
    </table>
  </ul>
  %end

  <h2>Give feedback</h2>
  <ul>
    Questions, comments, feature requests, patches, pull requests and cake are all welcomed at <a href="mailto:jminter@redhat.com">jminter@redhat.com</a>.
  </ul>

</body>

</html>
