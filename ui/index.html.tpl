% import socket

<html>

<head>
  <title>Welcome to {{ socket.gethostname() }}!</title>
</head>

<body>
  <h1>Welcome to {{ socket.gethostname() }}!</h1>

  <h2>Available images</h2>
  <ul>
    <table>
      <tr>
        <th></th>
        % for target in targets:
        <th valign="bottom" width="150">{{ target }}</th>
        % end
      </tr>
      % for row in table:
      <tr>
        <th align="right">{{ row[0] }}</th>
        % for item in row[1:]:
        <td align="center">
          % if item:
          <a href="{{ item }}">download</a>
          % end
        </td>
        % end
      </tr>
      % end
    </table>
  </ul>

  <h2>Give feedback</h2>
  <ul>
    Questions, comments, feature requests, patches, pull requests and cake are all welcomed at <a href="mailto:jminter@redhat.com">jminter@redhat.com</a>.
  </ul>

</body>

</html>
