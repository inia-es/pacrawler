import pycurl
import re
from io import BytesIO


def getEncoding(headers):
    encoding = None
    if 'content-type' in headers:
        content_type = headers['content-type'].lower()
        match = re.search('charset=(\S+)', content_type)
        if match:
            encoding = match.group(1)
    if encoding is None:
        # Default encoding for HTML is iso-8559-1.
        # Other content types may have different default encoding,
        # or in case of binary data, may have no encoding at all.
        encoding = 'iso-8859-1'
    return encoding

def crawl(url):
    headers = {}

    def header_function(header_line):
        # HTTP standard specifies that headers are encoded in iso-8859-1
        header_line = header_line.decode('iso-8859-1')

        # Header lines include the first status line (HTTP/1.X ...)
        # We are going to ignore all lines that don't have a colon in them.
        # This will botch headers that are split on multiple lines ...
        if ':' not in header_line:
            return

        # Break the header line into header name and value.
        name, value = header_line.split(':', 1)

        # Remove whitespace that may be present.
        # Header lines include the trailing newline, and there may be whitespace
        # arount the colon.
        name = name.strip()
        value = value.strip()

        # Header names are case insensitive.
        # Lowercase name here.
        name = name.lower()

        # Now we can actually record the header name and value.
        headers[name] = value

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.HEADERFUNCTION, header_function)
    c.perform()
    c.close()
    return buffer, headers

def print_site(content, encoding):
    body = content.getvalue()
    body = body.strip()
    # Body is a byte string.
    # We have to know the enconding in order to print it to a text file
    # such as standard ouput.
    print(body.decode(encoding))

def crawl_and_print(url):
    print(url, "\n")
    content, headers = crawl(url)
    encoding = getEncoding(headers)
    print_site(content, encoding)

sitesFile = open('sites.txt', 'r')
for line in sitesFile:
    if line[0] != '#':
	    crawl_and_print(line)
