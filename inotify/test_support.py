import os
import logging
import shutil
import tempfile
import contextlib

_LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def temp_path():
    path = tempfile.mkdtemp()

    original_wd = os.getcwd()
    os.chdir(path)

    try:
        yield path
    finally:
        os.chdir(original_wd)

        if os.path.exists(path) is True:
            shutil.rmtree(path)


def equals_modulo_watch_descriptor(inotify_event_a, inotify_event_b):
    return tuple(inotify_event_a[1:]) == tuple(inotify_event_b[1:])


def have_same_elements(list_a, list_b):
    return set(list_a) == set(list_b)


def fuzzyAssertEventListEquals(test_self, event_list_a, event_list_b):
    watch_descriptors_a = dict()
    watch_descriptors_b = dict()
    for event_a, event_b in zip(event_list_a, event_list_b):
        # First check for equality where it is strictly necessary
        test_self.assertEquals(event_a[2:], event_b[2:])
        inotify_event_a, type_names_a, path_a, _ = event_a
        inotify_event_b, type_names_b, path_b, _ = event_b
        track_wd_path_correlation(test_self, inotify_event_a, path_a, watch_descriptors_a)
        track_wd_path_correlation(test_self, inotify_event_b, path_b, watch_descriptors_b)
        test_self.assertTrue(equals_modulo_watch_descriptor(inotify_event_a,
                                                            inotify_event_b))
        test_self.assertTrue(have_same_elements(type_names_a, type_names_b))


def track_wd_path_correlation(test_self, inotify_event, path, watch_descriptors):
    if path in watch_descriptors:
        test_self.assertEquals(watch_descriptors[path], inotify_event.wd)
    else:
        watch_descriptors[path] = inotify_event.wd
