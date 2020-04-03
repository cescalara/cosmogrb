import h5py
from cosmogrb.utils.hdf5_utils import recursively_load_dict_contents_from_group



class DetectorSave(object):

    def __init__(self, name, is_detected, extra_info=None):
        """
        reloads the information collected from running detection
        algorithm on a GRB


        :param name: 
        :param is_detected: 
        :param extra_info: 
        :returns: 
        :rtype: 

        """

        self._name = name
        self._is_detected = is_detected
        self._extra_info = extra_info

        if extra_info is not None:
            assert isinstance(extra_info, dict)
        self._extra_info = extra_info

    @property
    def name(self):
        return self._name

    @property
    def is_detected(self):
        return self._is_detected

    @property
    def extra_info(self):
        return self._extra_info


    @classmethod
    def from_file(cls, file_name):

        with h5py.File(file_name, "r") as f:

            name = f.attrs["name"]
            is_detected = f.attrs["is_detected"]
            
            try:

                extra_info = recursively_load_dict_contents_from_group(f, "extra_info")
                
            except:

                extra_info = None


            return cls(name, is_detected, extra_info)
