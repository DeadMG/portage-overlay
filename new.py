#!python3
import sys, os, shutil

if len(sys.argv) < 3:
    print('Usage: new <qual> <version> [copy-from-version]')
    sys.exit(1)

pkg     = sys.argv[1].replace('.\\', '').replace('\\', '/')
dst_ver = sys.argv[2]
src_ver = sys.argv[3] if len(sys.argv) >= 4 else None

try:
    category, name = pkg.split('/')
except:
    print('Invalid qualified name:', pkg)
    sys.exit(1)

if src_ver:
    src_file = os.path.join(pkg, name + '-' + src_ver + '.ebuild')
else:
    src_file = 'template.ebuild'

dst_file = os.path.join(pkg, name + '-' + dst_ver + '.ebuild')

print('Copying', src_file, 'to', dst_file)
try:
    os.makedirs(pkg, exist_ok = True)
    shutil.copy(src_file, dst_file)
except OSError as e:
    print('Failed:', e)

print('Done')
