import docker
import os
import shutil
import uuid

from docker.errors import *

IMAGE_NAME = 'qianmao/cs503_coj_demo'

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEMP_BUILD_DIR = '%s/tmp/' % CURRENT_DIR

SOURCE_FILE_NAMES = {
    'java': 'Solution.java',
    'python': 'solution.py'
}

BINARY_NAMES = {
    'java': 'Solution',
    'python': 'solution.py'
}

BUILD_COMMANDS = {
    'java': 'javac',
    'python': 'python'
}

EXECUTE_COMMANDS = {
    'java': 'java',
    'python': 'python'
}

client = docker.from_env()

def load_image():
    # pull images to machine
    try:
        client.images.get(IMAGE_NAME)
    except ImageNotFound:
        print 'Image not found locally. Loading from Dockerhub...'
        client.images.pull(IMAGE_NAME)
    except APIError:
        print 'Image not found locally. Cannot connect Dockerhub...'
        return
    print 'Image:[%s] loaded.' % IMAGE_NAME


def build_and_run(code, lang):
    result = {'build': None, 'run': None, 'error': None}

    # uuid.uuid4() is a gen.ed unique number to mark a task
    source_file_parent_dir_name = uuid.uuid4()
    # dir in host OS
    source_file_host_dir = '%s/%s' % (TEMP_BUILD_DIR, source_file_parent_dir_name)
    # dir in docker container
    source_file_guest_dir = '/test/%s' % source_file_parent_dir_name
    make_dir(source_file_host_dir)

    # write code to a source file
    source_file_host = '%s/%s' % (source_file_host_dir, SOURCE_FILE_NAMES[lang])
    with open(source_file_host, 'w') as source_file:
        source_file.write(code)

    # BUILD
    try:
        client.containers.run(
            image=IMAGE_NAME,
            command='%s %s' % (BUILD_COMMANDS[lang], SOURCE_FILE_NAMES[lang]), # command passed to the image
            # map file directories
            volumes={
                source_file_host_dir:
                    {'bind': source_file_guest_dir, 'mode': 'rw'}
            },
            working_dir=source_file_guest_dir
        )
        print 'Source built.'
        result['build'] = 'OK'
    except ContainerError as e:
        print 'Build failed'
        result['build'] = e.stderr
        shutil.rmtree(source_file_host_dir)
        return result

    # RUN
    try:
        log = client.containers.run(
            image=IMAGE_NAME,
            command='%s %s' % (EXECUTE_COMMANDS[lang], BINARY_NAMES[lang]), # command passed to the image
            volumes={ # map file directories
                source_file_host_dir:
                    {'bind': source_file_guest_dir, 'mode': 'rw'}
            },
            working_dir=source_file_guest_dir
        )
        print 'Source Executed.'
        result['run'] = log # will have stdout
    except ContainerError as e:
        print 'Execution failed'
        result['run'] = e.stderr
        shutil.rmtree(source_file_host_dir)
        return result

    shutil.rmtree(source_file_host_dir)
    return result

def make_dir(dir_):
    try:
        os.mkdir(dir_)
        print 'Tmp build directory [%s] created' % dir_
    except OSError:
        print 'Tmp build directory [%s] exists' % dir_


make_dir(TEMP_BUILD_DIR)
