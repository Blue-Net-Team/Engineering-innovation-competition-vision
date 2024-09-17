try:
    from cnn import *
except ImportError:
    try:
        from detector.model.cnn import *
    except ModuleNotFoundError:
        from model.cnn import *