import socket


class URL:
    # I’m going to make parsing a URL return a URL object,
    # and I’ll put the parsing code into the constructor
    def __init__(self, url):
        # Let’s start with the scheme, which is separated from the rest of the URL by ://.
        # Our browser only supports http, so let’s check that, too
        self.scheme, url = url.split("://", 1)
        assert self.scheme == "http"

        # Now we must separate the host from the path. The host comes before the first /,
        # while the path is that slash and everything after it
        if "/" not in url:
            url = url + "/"
        # Note that there’s some tricky logic here for handling the slash
        # between the host name and the path. That (optional) slash is part of the path.
        self.host, url = url.split("/", 1)
        self.path = "/" + url


    # Now that the URL has the host and path fields,
    # we can download the web page at that URL. We’ll do that in a new method, request
    def request(self):
      # The first step to downloading a web page is connecting to the host.
      # The operating system provides a feature called “sockets” for this
      s = socket.socket(
          family=socket.AF_INET,
          type=socket.SOCK_STREAM,
          proto=socket.IPPROTO_TCP,
      )

      # Once you have a socket, you need to tell it to connect to the
      # other computer. For that, you need the host and a port.
      s.connect((self.host, 80))

      # Now that we have a connection, we make a request to
      # the other server. To do so, we send it some data using the send method
      request = "GET {} HTTP/1.0\r\n".format(self.path)
      request += "Host: {}\r\n".format(self.host)
      # It’s essential that you put two \r\n newlines at the end,
      # so that you send that blank line at the end of the request.
      request += "\r\n"
      s.send(request.encode("utf8"))

      # Here, makefile returns a file-like object containing every byte we
      # receive from the server. I am instructing Python to turn those bytes
      # into a string using the utf8 encoding
      # I’m also informing Python of HTTP’s weird line endings.
      response = s.makefile("r", encoding="utf8", newline="\r\n")

      # Let’s now split the response into pieces. The first line is the status line
      statusline = response.readline()
      version, status, explanation = statusline.split(" ", 2)

      # After the status line come the headers
      # I split each line at the first colon and
      # fill in a map of header names to header values
      response_headers = {}
      while True:
          line = response.readline()
          if line == "\r\n": break
          header, value = line.split(":", 1)
          # Headers are case-insensitive, so I normalize them to lower case.
          # Also, whitespace is insignificant in HTTP header values,
          # so I strip off extra whitespace at the beginning and end.
          response_headers[header.casefold()] = value.strip()

      # A couple of headers are especially important because they tell us that
      # the data we’re trying to access is being sent in an unusual way.
      # Let’s make sure none of those are present.
      assert "transfer-encoding" not in response_headers
      assert "content-encoding" not in response_headers

      # Usually the content is everything after the headers
      content = response.read()
      s.close()

      return content


# DISPLAY THE HTML

# Take the page HTML and print all the text, but not the tags, in it
def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")


# Load the page
def load(url):
    body = url.request()
    show(body)

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))
