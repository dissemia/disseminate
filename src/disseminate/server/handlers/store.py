"""
Local storage for requests
"""

store = dict()


def reset_store():
    global store
    store.clear()
