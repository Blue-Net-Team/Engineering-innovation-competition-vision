try:
    from cnn import *
except ModuleNotFoundError:
    try:
        from detector.model.cnn import *
    except ModuleNotFoundError:
        from model.cnn import *