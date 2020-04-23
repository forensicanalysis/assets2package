import json
import os, shutil
import subprocess

STIX_CHECKOUT_PATH = 'cti-stix2-json-schemas'
STIX_REPOSITORY = 'https://github.com/oasis-open/cti-stix2-json-schemas.git'
MODULE_NAME = 'forensicstore_stix_schemas'
ENTRY_POINT_GROUP = 'forensicstore_schemas'
OUTPUT_FOLDER = 'packaged'
VERSION = '2.1'
AUTHOR = 'Demian Kellermann'
AUTHOR_MAIL = 'demian.kellermann@siemens.com'
URL = 'https://github.com/forensicanalysis/pyforensicstore_stix'
SETUP_PY_SKEL_HEAD = f'''
from setuptools import setup

setup(
    name="{MODULE_NAME}",
    author="{AUTHOR}",
    author_email="{AUTHOR_MAIL}",
    url="{URL}",
    description="STIX 2.1 JSON schemas as a python provider",
    version="{VERSION}",
    py_modules=['{MODULE_NAME}'],
    entry_points={{
        '{ENTRY_POINT_GROUP}': [
'''

SETUP_PY_SKEL_FOOT = '''
        ]
    }
)
'''

if not os.path.isdir(STIX_CHECKOUT_PATH):
    print("Cloning source repo...")
    subprocess.check_call(['git', 'clone', STIX_REPOSITORY])

my_module = ''
my_entrypoints = []

for root, dirs, files in os.walk(os.path.join(STIX_CHECKOUT_PATH, 'schemas')):
    for json_file in (f for f in files if f.endswith('.json')):
        json_path = os.path.join(root, json_file) 
        with open(json_path, 'r') as json_handle:
            json_contents = json.load(json_handle)
            schema_name = json_contents.get('title')
            if not schema_name:
                print(f'{json_path} does not have title key, skipping')
                continue
            schema_name_py = schema_name.replace('-', '_')
            my_module += '\n'
            my_module += f'{schema_name_py} = {json_contents.__repr__()}'
            my_entrypoints.append(f'{schema_name} = {MODULE_NAME}:{schema_name_py}')

print(f"Read {len(my_entrypoints)} schema definitions")

if os.path.exists(OUTPUT_FOLDER):
    print(f"Deleting old output folder '{OUTPUT_FOLDER}'")
    shutil.rmtree(OUTPUT_FOLDER)

os.makedirs(OUTPUT_FOLDER)

print(f"Copying package README...")
shutil.copy('README.md.package', os.path.join(OUTPUT_FOLDER, 'README.md'))

print(f"Writing schema definition file '{MODULE_NAME}.py'...")
with open(os.path.join(OUTPUT_FOLDER, MODULE_NAME+'.py'), 'w') as file_handle:
    file_handle.write(my_module)

print("Writing setup.py...")
with open(os.path.join(OUTPUT_FOLDER, 'setup.py'), 'w') as file_handle:
    file_handle.write(SETUP_PY_SKEL_HEAD)
    for ep in my_entrypoints:
        file_handle.write(' ' * 12)  # indent 3 levels
        file_handle.write(f'{ep.__repr__()},\n')
    file_handle.write(SETUP_PY_SKEL_FOOT)

print(f"Python package written to '{OUTPUT_FOLDER}'")
