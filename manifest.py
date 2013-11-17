#!python3
import sys, re, os, hashlib, urllib.parse
import requests

def file_info(path):
    sha1      = hashlib.sha1()
    sha256    = hashlib.sha256()
    whirlpool = hashlib.new('whirlpool')
    size      = 0

    with open(path, 'rb') as fp:
        while True:
            buf = fp.read(4096)
            if not buf:
                break
            size += len(buf)

            sha1.update(buf)
            sha256.update(buf)
            whirlpool.update(buf)

    return {
        'size': size,
        'sha1': sha1.hexdigest(),
        'sha256': sha256.hexdigest(),
        'whirlpool': whirlpool.hexdigest(),
    }

def sub_variables(path, variables):
    with open(path, 'r', encoding = 'utf-8') as fp:
        body = fp.read()
        for name, value in variables.items():
            body = body.replace('${' + name + '}', value).replace('$' + name, value)
        return body

def download_file(uri):
    info     = urllib.parse.urlparse(uri)
    filename = os.path.basename(info.path)
    path     = os.path.join('.tmp', filename)

    if os.path.exists(path):
        return filename, path

    print('\t\t\t* Downloading', uri)
    try:
        response = requests.get(uri, stream = True, verify = True)
    except Exception as e:
        print('\t\t\t! Failed:', e)
        return None

    total_bytes = int(response.headers.get('content-length', None))
    got_bytes   = 0

    try:
        with open(path, 'wb') as fp:
            for chunk in response.iter_content(4096):
                got_bytes += len(chunk)
                fp.write(chunk)

                got_bytes_mb = got_bytes / (1024 * 1024)
                if total_bytes is not None:
                    total_bytes_mb = total_bytes / (1024 * 1024)
                    progress = int((got_bytes / total_bytes) * 100)
                    print('\t\t\t* {0:.2f}MB/{1:.2f}MB [{2}%]                '.format(got_bytes_mb, total_bytes_mb, progress), end = '\r')
                else:
                    print('\t\t\t* {0:.2f}MB          '.format(got_bytes_mb))
            print('\t\t\t* Done                                      ')
    except KeyboardInterrupt:
        print('\t\t\t[Interrupted, exiting]')
        try:
            os.unlink(path)
        except Exception as e:
            print('\t\t\t! Could not cleanup partially downloaded file:', e)
        sys.exit(255)

    return filename, path

def validate_argument(arg):
    pkg = arg.replace('\\', '/').replace('./', '')

    if pkg in ('licenses', 'eclasses', 'profiles', '.git') or '/' not in pkg:
        print('Not a package:', pkg)
        print('Expected: category/package, e.g. sys-apps/portage')
        sys.exit(1)

    if not os.path.exists(pkg):
        print('No package:', pkg)
        sys.exit(1)

    return pkg

NAME_RE     = re.compile(r'^(?P<name>.*?)-(?P<version>.*?)(?:-(?P<revision>r\d+))?$')
SRC_URIS_RE = re.compile(r'SRC_URI\s*=\s*"(?P<uris>[^"]+)"', re.M)

def process_package(pkg):
    manifest = []
    ebuilds  = []

    print('Processing package', pkg)
    print('\tProcessing local files')
    for root, dirs, files in os.walk(pkg):
        rel_root = root[len(pkg)+1:]

        for filename in files:
            if filename == 'Manifest':
                continue

            if not rel_root and filename.endswith('.ebuild'):
                filetype = 'EBUILD'
                ebuilds.append(filename)
            elif not rel_root:
                filetype = 'MISC'
            else:
                filetype = 'AUX'

            path  = os.path.join(root, filename)
            entry = file_info(path)

            print('\t\t' + path.replace('\\', '/'), 'size:', entry['size'], 'SHA1:', entry['sha1'])
            entry['name'] = filename
            entry['type'] = filetype
            manifest.append(entry)

    uris = set()
    print('\tProcessing distfiles')
    for ebuild in ebuilds:
        match = NAME_RE.match(ebuild.replace('.ebuild', ''))
        if match is None:
            print('\t\t! Invalid ebuild name:', ebuild)
            continue

        name      = match.group('name')
        version   = match.group('version')
        revision  = match.group('revision') or 'r0'
        ver_rev   = version + '-' + revision if revision != 'r0' else version
        name_ver  = name + '-' + version
        full_name = name + '-' + ver_rev

        variables = {
            'P':   name_ver,
            'PN':  name,
            'PV':  version,
            'PR':  revision,
            'PVR': ver_rev,
            'PF':  full_name
        }

        body  = sub_variables(os.path.join(pkg, ebuild), variables)
        match = SRC_URIS_RE.search(body)
        if match is None:
            print('\t\t! Ebuild is missing SRC_URI:', ebuild)
            continue

        uris.update(match.group('uris').split())

    for uri in uris:
        if '://' not in uri:
            continue

        filename, path = download_file(uri)
        entry = file_info(path)

        print('\t\tDIST', filename, 'size:', entry['size'], 'SHA1:', entry['sha1'])

        entry['name'] = filename
        entry['type'] = 'DIST'
        manifest.append(entry)

    print('\tWriting Manifest for', pkg)
    with open(os.path.join(pkg, 'Manifest'), 'w', encoding = 'utf-8', newline = '\n') as fp:
        for entry in manifest:
            print(entry['type'], entry['name'], entry['size'], 'SHA1', entry['sha1'], 'SHA256', entry['sha256'], 'WHIRLPOOL', entry['whirlpool'], file = fp)

if len(sys.argv) < 2:
    print('Usage: manifest <package> [package [package ...]]')
    sys.exit(1)

os.makedirs('.tmp', exist_ok = True)
pkgs = [validate_argument(arg) for arg in sys.argv[1:]]
for pkg in pkgs:
    process_package(pkg)
