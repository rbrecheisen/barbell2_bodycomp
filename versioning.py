import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--level', help='upgrade level: [major|minor(default)|patch]', default='minor')
args = parser.parse_args()

f = open('VERSION', 'r')
version = f.readline().strip().split('.')
f.close()
v_major = int(version[0])
v_minor = int(version[1])
v_patch = int(version[2])
if args.level == 'major':
    v_major += 1
    v_minor = 0
    v_patch = 0
elif args.level == 'minor':
    v_minor += 1
    v_patch = 0
elif args.level == 'patch':
    v_patch += 1
version_new = f'{v_major}.{v_minor}.{v_patch}'
print(version_new)
f = open('VERSION', 'w')
f.write(version_new)
f.close()
