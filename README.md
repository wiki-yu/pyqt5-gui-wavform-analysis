
<h1>
PYQT to display respirary waveform data
</h1>

## Description
<p>
This GUI is for displaying the dynamical waveform data and locating the peak and valley automatically.  
</p>


## Setup 
Get the code by either cloning this repository using git
>git clone https://github.com/wiki-yu/pyqt5-gui-wavform-analysis.git

Open a new terminal window in the the root folder.

### Build virtual enviroment:

_For Windows:_

```bash
py -m venv env # Only run this if env folder does not exist
.\env\Scripts\activate
pip install -r requirements.txt
```

_For MacOS/Linux:_

```bash
python3 -m venv env # Only run this if env folder does not exist
source env/bin/activate
pip install -r requirements.txt
```

### Get into the src file folder
```
cd src
```

### Run the code
```
python main.py
```

## Interface

![PYQT Interface for waveform analysis](/images/interface.png)






