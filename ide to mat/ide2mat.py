import endaq.ide as ed
import glob, sys, os, hdf5storage
# import scipy as scipy
import numpy as np
from datetime import datetime

dirs=['x', 'y', 'z']

print(f"Python Version: {sys.version}")
start=datetime.now()
print(f"Script start time: {start}")

for file in glob.glob('./*.ide'):
    with ed.get_doc(file) as rawslam:
        print(f"Opened {file} at {datetime.now()}")
        ed.extract_time(file, "time.ide", start=0, end="1s")
        ed.get_channel_table(rawslam).data
        for i in range(len(dirs)):
            print(f"Parsing {dirs[i]} direction")
            accel=ed.to_pandas(ed.get_channels(rawslam, measurement_type="accel", subchannels=True)[i], time_mode='seconds').astype(np.float32)
            if i==0:
                out=np.zeros((4,len(accel)), dtype=np.float32)
            out[i+1]=accel.to_numpy().flatten()
            out[0]=accel.index.to_numpy()
            del accel
        
    with ed.get_doc("time.ide") as rawslam:
        times=ed.to_pandas(ed.get_channels(rawslam, measurement_type="accel", subchannels=True)[0], time_mode='datetime', tz="utc").astype(np.float32)
        starttime=str(times.index.to_numpy()[0])
        print(f"Sensor start datetime is: {starttime}")
        del times
        
    try:
        os.remove("time.ide")
    except:
        print("ERROR: Time file already removed")

    filnam=file[2:-4]+".mat"
    data_desc=["time (sec from start_time)", "X (g)", "Y (g)", "Z (g)"]
    # scipy.io.savemat(filnam, {'data':out, 'start_time':starttime, 'data_desc':data_desc}, do_compression=False)
    print(f"Writing data out to {filnam} at {datetime.now()}")
    hdf5storage.savemat(filnam, {'data':out, 'start_time':starttime, 'data_desc':data_desc}, format=7.3, matlab_compatible=True, compress=False)

print(f"Script total runtime: {datetime.now()-start}")